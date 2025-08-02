import urllib.request
import json
import zipfile
import os
import shutil
import sys
import subprocess

def get_latest_release_info():
    url = f"https://api.github.com/repos/RyeHands/pinots-display/releases/latest"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read())
        return data['tag_name'], data['zipball_url']

def download_file(url, dest_path):
    urllib.request.urlretrieve(url, dest_path)

def extract_zip(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def write_updater_script(old_dir, new_dir):
    code = f"""
import os
import shutil
import time
import sys
import subprocess

old_dir = r\"\"\"{old_dir}\"\"\"
new_dir = r\"\"\"{new_dir}\"\"\"

def copytree(src, dst):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

time.sleep(1)

# Backup room.txt if it exists
room_txt = os.path.join(old_dir, 'room.txt')
backup_room_txt = None
if os.path.exists(room_txt):
    backup_room_txt = os.path.join(old_dir, 'room.txt.bak')
    shutil.copy2(room_txt, backup_room_txt)

# Delete all files and folders in old_dir except updater.py, temp_update, and room.txt.bak
for item in os.listdir(old_dir):
    if item not in ['updater.py', 'temp_update', 'room.txt.bak']:
        path = os.path.join(old_dir, item)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

# Move new files in place
copytree(new_dir, old_dir)

# Restore room.txt if it was backed up
if backup_room_txt and os.path.exists(backup_room_txt):
    shutil.move(backup_room_txt, room_txt)
else:
    # No local room.txt before, keep the room.txt from repo (if it exists)
    pass

# Cleanup
shutil.rmtree(os.path.join(old_dir, 'temp_update'))
os.remove(os.path.join(old_dir, 'updater.py'))

# Relaunch app
subprocess.Popen([sys.executable, 'launcher.py'])

# Remove update flag
try:
    os.remove(os.path.join(old_dir, 'update_in_progress.flag'))
except FileNotFoundError:
    pass
"""
    with open("updater.py", "w") as f:
        f.write(code.strip())

def main():
    current_version_path = "version.txt"

    if not os.path.exists(current_version_path):
        print("[Updater] Missing version.txt")
        return

    with open(current_version_path) as f:
        current_version = f.read().strip()

    try:
        latest_version, zip_url = get_latest_release_info()

        if latest_version != current_version:
            print(f"[Updater] New version found: {latest_version}")
            zip_name = "update.zip"
            temp_dir = os.path.join(os.getcwd(), "temp_update")
            os.makedirs(temp_dir, exist_ok=True)

            print("[Updater] Downloading release...")
            download_file(zip_url, zip_name)

            print("[Updater] Extracting release...")
            extract_zip(zip_name, temp_dir)
            os.remove(zip_name)

            # GitHub source zip includes a folder inside temp_update
            extracted_dir = next(os.path.join(temp_dir, d)
                                 for d in os.listdir(temp_dir)
                                 if os.path.isdir(os.path.join(temp_dir, d)))

            print("[Updater] Preparing updater script...")
            write_updater_script(os.getcwd(), extracted_dir)

            print("[Updater] Launching updater...")
            # Signal that the updater will relaunch the app
            with open("update_in_progress.flag", "w") as f:
                f.write("1")
                
            subprocess.Popen([sys.executable, "updater.py"])
            sys.exit()

        else:
            print(f"[Updater] App is up to date. ({current_version})")

    except Exception as e:
        print(f"[Updater] Update check failed: {e}")

if __name__ == "__main__":
    main()

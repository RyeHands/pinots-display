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

# Delete all files and folders in old_dir except this script and temp_update
for item in os.listdir(old_dir):
    if item not in ['updater.py', 'temp_update']:
        path = os.path.join(old_dir, item)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

# Move new files in place
copytree(new_dir, old_dir)

# Cleanup
shutil.rmtree(os.path.join(old_dir, 'temp_update'))
os.remove(os.path.join(old_dir, 'updater.py'))

# Relaunch app
subprocess.Popen([sys.executable, 'launcher.py'])
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
            subprocess.Popen([sys.executable, "updater.py"])
            sys.exit()

        else:
            print("[Updater] App is up to date.")

    except Exception as e:
        print(f"[Updater] Update check failed: {e}")

if __name__ == "__main__":
    main()

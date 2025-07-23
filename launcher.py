import subprocess
import os

def run_updater_if_present():
    if os.path.exists("auto_updater.py"):
        print("[Launcher] Running updater...")
        subprocess.run(["python", "auto_updater.py"])
        print("[Launcher] Updater finished.")

def launch_main_app():
    print("[Launcher] Launching app...")
    subprocess.run(["python", "web.py"])

if __name__ == "__main__":
    print("Update Test!!")
    run_updater_if_present()
    launch_main_app()

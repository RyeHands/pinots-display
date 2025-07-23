import subprocess
import sys
import os

def run_updater_if_present():
    if os.path.exists("auto_updater.py"):
        print("[Launcher] Running updater...")
        subprocess.run(["python", "auto_updater.py"])
        print("[Launcher] Updater finished.")

    # If an update is in progress, don't run the app
    if os.path.exists("update_in_progress.flag"):
        print("[Launcher] Update is in progress. Exiting launcher.")
        sys.exit(0)

def launch_main_app():
    print("[Launcher] Launching app...")
    subprocess.run(["python", "web.py"])

if __name__ == "__main__":
    run_updater_if_present()
    launch_main_app()

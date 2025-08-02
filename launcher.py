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

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except subprocess.CalledProcessError:
        print(f"[Launcher] Failed to install {package}")

def ensure_installed(module_name, package_name=None):
    try:
        __import__(module_name)
        print(f"[Launcher] Module '{module_name}' already installed.")
    except ImportError:
        print(f"[Launcher] Module '{module_name}' not found. Installing...")
        install_package(package_name or module_name)

if __name__ == "__main__":
    ensure_installed("PIL", "Pillow")
    ensure_installed("tkinterdnd2")  # package name same as module
    run_updater_if_present()
    launch_main_app()
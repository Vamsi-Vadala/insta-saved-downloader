import os
import platform
import requests
import zipfile
import shutil

# CONFIGURATION
BINARY_TYPE = "chromedriver"
DOWNLOAD_DIR = "../drivers"
JSON_URL = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"

# Detect platform

class WebdriverDownloader:
    def __init__(self):
        self.platform_name = None
        self.driver_path = None
        self.current_version = None
        system = platform.system().lower()
        machine = platform.machine().lower()

        if system == "windows":
            self.platform_name = "win64"
        elif system == "linux":
            self.platform_name = "linux64"
        elif system == "darwin":
            if machine == "x86_64":
                self.platform_name = "mac-x64"
            elif "arm" in machine:
                self.platform_name = "mac-arm64"
        # raise Exception("Unsupported platform")

    def download_and_extract(self,url, download_path):
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
        self.driver_path = os.path.join(download_path, BINARY_TYPE+'-'+self.platform_name)

        with open(os.path.join(self.driver_path, "version.txt"), "w") as f:
            f.write(self.current_version)
            f.close()
        print(f"Extracted to {self.driver_path}")

    def mainDownloader(self):

        if self.platform_name is None:
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
        if os.path.exists(final_path):
            self.driver_path = os.path.join(final_path, BINARY_TYPE+'-'+self.platform_name)
            with open(os.path.join(self.driver_path,'version.txt'), "r") as f:
                if self.current_version == f.read().strip():
                    print(f"Driver already up to date: {self.current_version}")
                    return
                else:                
                    print(f"Removing old existing directory: {final_path}")
                    shutil.rmtree(final_path)
        self.download_and_extract(url, final_path)
        print(f" {BINARY_TYPE} downloaded successfully.")

                    
    def get_driver(self):
        if self.driver_path is None:
            raise Exception("Driver not downloaded yet.")
        if self.platform_name == "win64":
            return os.path.join(self.driver_path, BINARY_TYPE + ".exe")
        return os.path.join(self.driver_path, BINARY_TYPE)

def get_driver():
    downloader = WebdriverDownloader()
    downloader.mainDownloader()
    print(f'The downloaded driver is are {downloader.get_driver()}')
    return downloader.get_driver()
import os
import re
import time
import json
import ffmpeg
import pickle
import urllib.request
import threading
import concurrent.futures
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from loginHandler import InstaLoginHandler as Login
import itertools
from collections import defaultdict

class InstagramDownloader:
    def __init__(self, max_workers=2):
        self.max_workers = max_workers
        self.no_video_url_count = 0
        self.lock = threading.Lock()
        self.pbar = None
        login = Login()
        self.insta_username = login.get_username()
        self.insta_cookies = pickle.load(open("../instagram_cookies.pkl", "rb"))
        self.chrome_service = login.chrome_service

    def _get_bitrate(self, url):
        try:
            metadata = ffmpeg.probe(url)
            video_bitrate = next((int(s.get('bit_rate', 0)) for s in metadata['streams'] if s['codec_type'] == 'video'), 0)
            audio_bitrate = next((int(s.get('bit_rate', 0)) for s in metadata['streams'] if s['codec_type'] == 'audio'), 0)
            return video_bitrate, audio_bitrate
        except Exception:
            return 0, 0

    def _update_progress(self, block_num, block_size, total_size):
        if self.pbar is None:
            self.pbar = tqdm(total=total_size, unit='B', unit_scale=True)
        downloaded = block_num * block_size
        self.pbar.update(min(downloaded - self.pbar.n, total_size - self.pbar.n))
        if downloaded >= total_size:
            self.pbar.close()
            self.pbar = None

    def _extract_title(self, url):
        match = re.search(r"instagram.com/p/([^/?]+)", url)
        return match.group(1) if match else "instagram_video"

    def _extract_video_urls(self, url):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        try:
            driver = webdriver.Chrome(options=chrome_options, service=self.chrome_service)
        except Exception as e:
            print(f"Chrome driver crashed for {url} with error: {e}")
            with open("../failed_urls.txt", "a") as f:
                f.write(f"{url}\n")
            print("The URL has been added to the failed URLs list.")
            return
        # driver.set_window_size(480, 256)
        driver.get(url)
        for cookie in self.insta_cookies:
            driver.add_cookie(cookie)
        driver.refresh()
        time.sleep(3)
        logs = driver.get_log("performance")
        driver.quit()
        urls = set()
        for entry in logs:
            try:
                message = json.loads(entry["message"])["message"]
                if message["method"] == "Network.requestWillBeSent":
                    req_url = message["params"]["request"]["url"]
                    if ".mp4" in req_url:
                        urls.add(re.sub(r"&bytestart=.*&byteend=.*", "", req_url))
            except Exception:
                continue
        return urls

    def download(self, url, video_only=False, audio_only=False):
        try:
            video_urls = self._extract_video_urls(url)
            if not video_urls:
                with self.lock:
                    self.no_video_url_count += 1
                print(f"No video URL found for {url}. Count: {self.no_video_url_count}")
                return

            best_video_url = best_audio_url = None
            max_video_bitrate = max_audio_bitrate = 0
            for u in video_urls:
                v_bitrate, a_bitrate = self._get_bitrate(u)
                if v_bitrate > max_video_bitrate:
                    max_video_bitrate, best_video_url = v_bitrate, u
                if a_bitrate > max_audio_bitrate:
                    max_audio_bitrate, best_audio_url = a_bitrate, u

            title = self._extract_title(url)
            if best_video_url and not audio_only:
                urllib.request.urlretrieve(best_video_url, f"../videos/{title}.mp4", self._update_progress)
            if best_audio_url and not video_only:
                urllib.request.urlretrieve(best_audio_url, f"../videos/{title}.mp3", self._update_progress)
            self.merge(title)
        except Exception as e:
            print(f"Error processing {url}: {e}")

    def threaded_download(self, urls, video_only=False, audio_only=False):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            executor.map(self.download, urls, itertools.repeat(video_only), itertools.repeat(audio_only))


    def _list_media_files(self):
        files = os.listdir("../videos/")
        videos = {f[:-4] for f in files if f.endswith(".mp4")}
        audios = {f[:-4] for f in files if f.endswith(".mp3")}
        return videos & audios

    def merge(self, title):
        try:
            v_file, a_file, out_file = f"../videos/{title}.mp4", f"../videos/{title}.mp3", f"../videos/{title}_converted.mp4"
            if not os.path.exists(v_file) or not os.path.exists(a_file):
                raise FileNotFoundError(f"Missing files for {title}")
            (
                ffmpeg
                .output(ffmpeg.input(v_file).video, ffmpeg.input(a_file).audio, out_file, vcodec="copy", acodec="aac", loglevel="error")
                .run(overwrite_output=True)
            )
            if os.path.exists(out_file):
                os.remove(v_file)
                os.remove(a_file)
                print(f"Merged and cleaned: {title}")
        except Exception as e:
            print(f"Error merging {title}: {e}")

    def mass_merge(self):
        titles = self._list_media_files()
        with tqdm(total=len(titles), desc="Merging Files") as pbar:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(self.merge, title) for title in titles]
                for _ in concurrent.futures.as_completed(futures):
                    pbar.update(1)

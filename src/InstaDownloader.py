import os
import re
import time
import json
import ffmpeg
import urllib.request
import threading
import progressbar
import itertools
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
from loginHandler import InstaLoginHandler as Login
import pickle

class InstagramDownloader:
    def __init__(self, max_workers=10):
        self.max_workers = max_workers
        self.no_video_url_count = 0  # Counter for failed video extractions
        self.lock = threading.Lock()  # Thread-safe lock for counter updates
        self.pbar = None  # Progress bar\
        login = Login()
        self.insta_username = login.get_username()
        self.insta_cookies = pickle.load(open("../instagram_cookies.pkl", "rb"))
        self.chrome_service = login.chrome_service
    
    def metadata(self, video_url):
        try:
            metadata = ffmpeg.probe(video_url)
            bitrate = {'video': 0, 'audio': 0}
            for stream in metadata["streams"]:
                if stream["codec_type"] == "video":
                    bitrate['video'] = int(stream.get('bit_rate', '0'))
                elif stream["codec_type"] == "audio":
                    bitrate['audio'] = int(stream.get('bit_rate', '0'))
            return bitrate
        except Exception as e:
            print(f"Error fetching metadata: {e}")
            return {'video': 0, 'audio': 0}
    
    def show_progress(self, block_num, block_size, total_size):
        if self.pbar is None:
            self.pbar = progressbar.ProgressBar(maxval=total_size)
            self.pbar.start()
        downloaded = block_num * block_size
        if downloaded < total_size:
            self.pbar.update(downloaded)
        else:
            self.pbar.finish()
            self.pbar = None

    def title(self, url):
        match = re.search(r"instagram\\.com/p/([^/?]+)", url)
        return match.group(1) if match else "instagram_video"

    def download(self, url, video_only=False, audio_only=False):
        try:
            chrome_options = Options()
            # chrome_options.add_argument("--headless=new")
            chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
            
            driver = webdriver.Chrome(options=chrome_options,service=self.chrome_service)
            driver.get('https://www.instagram.com')
            for cookie in self.insta_cookies:
                driver.add_cookie(cookie)
            driver.refresh()
            driver.get(url.strip())
            time.sleep(5)  # Wait for page load
            
            logs = driver.get_log("performance")
            driver.quit()
            
            # print(f'fetched logs successfully starting to Inspect the logd to extract urls......')

            # TODO Delete the following lines
            # Delete this ------------------------
            
            # with open('logs.json','w') as f:
            #     # print(f'Writing logs to logs.json file......')
            #     json.dump(log_file, f, indent=4)
            #     # print(f'Writing logs to logs.json file : Successful')
            #     f.close()
            # Delete this -------------------------
            video_urls = []
            log_file = [json.loads(log["message"]) for log in logs 
                        if "Network.requestWillBeSent" in json.loads(log["message"])["message"]["method"]]
            
            for log_message in log_file:
                try:
                    url = log_message['message']['params']['request']['url']
                    if '.mp4' in url:
                        video_urls.append(url)
                except:
                    continue

            print(f' url extraction successfull. starting to download the videos from extracted urls......')

            if not video_urls:
                with self.lock:
                    self.no_video_url_count += 1
                print(f"No video URL found for {url}. Count: {self.no_video_url_count}")
                return
            
            cleaned_urls = set(re.sub(r"&bytestart=.*&byteend=.*", "", u) for u in video_urls)
            max_video_bitrate, max_audio_bitrate = 0, 0
            final_video_url, final_audio_url = None, None

            print(f'celaned urls are :{cleaned_urls}')
            for u in cleaned_urls:
                bitrate = self.metadata(u)
                if bitrate['video'] > max_video_bitrate:
                    max_video_bitrate, final_video_url = bitrate['video'], u
                if bitrate['audio'] > max_audio_bitrate:
                    max_audio_bitrate, final_audio_url = bitrate['audio'], u
            
            print(f'extracted urls with highest resolution which is {max_video_bitrate} and {max_audio_bitrate}......')
            
            print(f'Extracting Title......')
            file_name = self.title(url)
            print(f'Extracting Title successful {file_name}. Starting to download..........')
            if final_video_url and not audio_only:
                urllib.request.urlretrieve(final_video_url, file_name + '.mp4', self.show_progress)
            if final_audio_url and not video_only:
                urllib.request.urlretrieve(final_audio_url, file_name + '.mp3', self.show_progress)

            self.merge(file_name)
        except Exception as e:
            print(f"Error processing {url}: {e}")

    def threaded_download(self, urls, video_only=False, audio_only=False):
        urls = ["https://www.instagram.com/p/" + u for u in urls]
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            executor.map(self.download, urls, itertools.repeat(video_only), itertools.repeat(audio_only))
    
    def list_vid_aud(self, converted=False):
        files = os.listdir('./')
        videos = [re.sub(".mp4", "", file) for file in files if ".mp4" in file]
        audios = [re.sub(".mp3", "", file) for file in files if ".mp3" in file]
        return videos, audios
    
    def merge(self, title):
        try:
            video_file, audio_file, output_file = f'./{title}.mp4', f'./{title}.mp3', f'./{title}_converted.mp4'
            if not os.path.exists(video_file) or not os.path.exists(audio_file):
                raise FileNotFoundError(f"Missing files for {title}: {video_file}, {audio_file}")
            (
                ffmpeg
                .output(ffmpeg.input(video_file).video, ffmpeg.input(audio_file).audio, output_file, vcodec="copy", acodec="aac", loglevel="error")
                .run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
            )
            if os.path.exists(output_file):
                os.remove(video_file)
                os.remove(audio_file)
                print(f"Merged and deleted: {title}")
        except Exception as e:
            print(f"Error merging {title}: {e}")

    def mass_download(self):
        with open('./savedVideosLinks.txt', 'r') as f:
            savedLinks = [link.strip() for link in f.readlines()]
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            executor.map(self.download, savedLinks)
        print(f"Total failed downloads: {self.no_video_url_count}")
    
    def mass_merge(self):
        videos, audios = self.list_vid_aud()
        common = set(videos) & set(audios)
        with tqdm(total=len(common), desc="Merging & Cleaning Up", unit="file") as pbar:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {executor.submit(self.merge, title): title for title in common}
                for future in concurrent.futures.as_completed(futures):
                    pbar.update(1)
        print(f"All files merged and cleaned up using {self.max_workers} workers!")

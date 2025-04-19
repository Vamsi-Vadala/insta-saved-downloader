import tkinter as tk
from tkinter import messagebox
import threading
from InstaDownloader import InstagramDownloader  # Assuming your class is in downloader.py

class InstaGUI:
    def __init__(self, master):
        self.master = master
        master.title("Instagram Video Downloader")
        master.geometry("400x150")
        master.resizable(False, False)

        self.label = tk.Label(master, text="Enter Instagram Post URL:")
        self.label.pack(pady=(15, 5))

        self.url_entry = tk.Entry(master, width=50)
        self.url_entry.pack(pady=5)

        self.download_button = tk.Button(master, text="Download", command=self.download_video)
        self.download_button.pack(pady=(10, 5))

        self.status_label = tk.Label(master, text="", fg="blue")
        self.status_label.pack()

        self.downloader = InstagramDownloader()

    def download_video(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Error", "Please enter a URL.")
            return

        self.status_label.config(text="Downloading...")
        threading.Thread(target=self.run_download, args=(url,), daemon=True).start()

    def run_download(self, url):
        try:
            self.downloader.download(url)
            self.status_label.config(text="Download complete!", fg="green")
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    gui = InstaGUI(root)
    root.mainloop()

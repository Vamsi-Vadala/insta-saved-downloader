import tkinter as tk
from tkinter import ttk, messagebox
import threading
from InstaDownloader import InstagramDownloader

class InstaGUI:
    def __init__(self, master):
        self.master = master
        master.title("Instagram Video Downloader")
        master.geometry("450x180")
        master.resizable(False, False)
        
        style = ttk.Style()
        style.configure("TButton", padding=6, font=('Helvetica', 10))
        style.configure("TLabel", font=('Helvetica', 10))
        style.configure("TEntry", padding=4, font=('Helvetica', 10))

        self.frame = ttk.Frame(master, padding="10 10 10 10")
        self.frame.pack(expand=True, fill=tk.BOTH)

        self.label = ttk.Label(self.frame, text="Enter Instagram Post URL:")
        self.label.grid(row=0, column=0, sticky=tk.W, pady=(5, 2))

        self.url_entry = ttk.Entry(self.frame, width=50)
        self.url_entry.grid(row=1, column=0, columnspan=2, pady=(0, 10))

        self.download_button = ttk.Button(self.frame, text="Download", command=self.download_video)
        self.download_button.grid(row=2, column=0, columnspan=2, pady=(0, 10))

        self.status_label = ttk.Label(self.frame, text="", foreground="blue")
        self.status_label.grid(row=3, column=0, columnspan=2)

        self.progress = ttk.Progressbar(self.frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=2, sticky='ew', pady=(5, 0))
        self.progress.grid_remove()

        self.downloader = InstagramDownloader()

    def download_video(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Error", "Please enter a URL.")
            return

        self.status_label.config(text="Downloading...", foreground="blue")
        self.progress.grid()
        self.progress.start()
        threading.Thread(target=self.run_download, args=(url,), daemon=True).start()

    def run_download(self, url):
        try:
            self.downloader.download(url)
            self.status_label.config(text="Download complete!", foreground="green")
            self.url_entry.delete(0, tk.END)
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", foreground="red")
        finally:
            self.progress.stop()
            self.progress.grid_remove()

if __name__ == "__main__":
    root = tk.Tk()
    app = InstaGUI(root)
    root.mainloop()

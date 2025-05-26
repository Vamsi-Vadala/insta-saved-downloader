# Insta Saved Downloader

Insta Saved Downloader helps you **batch download saved Instagram videos** from your account with a clean UI and simple setup. It supports both manual and playlist-based downloads via a modern web interface.

---

## 🚀 Features

- 🌐 Web-based interface (Flask)
- ✅ Supports both single URL and bulk playlist downloads
- 🎞️ Automatic merging of video and audio with ffmpeg
- 🧪 Smart setup: auto-create virtual environment & dependencies
- 🎨 Dark theme UI with futuristic styling

---

## 🖥️ How to Run

### ✅ Requirements

- Python 3.10+
- [Google Chrome](https://www.google.com/chrome/) (latest)
- `ffmpeg` installed and added to PATH

---

## 🐧 For Linux

### 🔧 Step-by-Step

1. **Give execute permission to the launcher**

```bash
chmod +x launch_app
```

2. **Run the app**

```bash
./launch_app
```

> This will:
> - Check/install Python & venv
> - Install dependencies from `requirements.txt`
> - Launch a web server
> - Open the app in your default browser

---

## 🪟 For Windows

Still in Development stage. Your are welcome to try the raw code for windows but you have to install all the required dependies youself.

---

## 📁 Project Structure

```
project/
├── launch_app            # Linux executable
├── launch_app.bat        # Windows batch launcher
├── requirements.txt
├── README.md
├── src/
│   ├── InstaWebDownloader.py
│   └── templates/
│       └── index.html
└── savedVideosLinks.txt
```

---

## ⚠️ Disclaimer

This tool is intended for **educational and personal use only**. Downloading or distributing content from Instagram may violate their [Terms of Service](https://help.instagram.com/581066165581870).

> 🛑 The author is not responsible for any misuse of this software. Use at your own risk.

---

## 💬 Contributing / Issues

Want to improve or add features? Pull requests are welcome.

If you find bugs or want to request features, [open an issue](https://github.com/your-repo/issues).

---

## 📜 License

MIT License. See `LICENSE` file for details.

from flask import Flask, render_template, request, redirect, url_for, flash
from InstaDownloader import InstagramDownloader
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
downloader = InstagramDownloader()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        if not url:
            flash("Please enter a URL.", "warning")
        else:
            try:
                downloader.download(url)
                flash("Download complete!", "success")
            except Exception as e:
                flash(f"Error: {e}", "danger")
        return redirect(url_for('index'))
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

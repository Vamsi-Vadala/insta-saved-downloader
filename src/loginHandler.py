import WebdriverDownloader as wd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import pickle
import os

USER_NAME = 'your_username_here'  # Replace with your Instagram username

class InstaLoginHandler:

    def __init__(self):
        self.chrome_service = Service(wd.get_driver())

    def login_handler(self):
        chrome_options = Options()
        driver = webdriver.Chrome(service=self.chrome_service, options=chrome_options)
        driver.get("https://www.instagram.com/accounts/login/")  
        time.sleep(5)  # Wait for the login page to load

        # Wait until the user is redirected after logging in manually
        while driver.current_url not in [
            "https://www.instagram.com/",
            "https://www.instagram.com/accounts/onetap/?next=%2F"
        ]:
            time.sleep(1)

        time.sleep(2)  # Additional wait for cookies to settle
        pickle.dump(driver.get_cookies(), open("../instagram_cookies.pkl", "wb"))
        print("Login successful!")
        driver.quit()

    def get_username(self):
        cookie_path = "../instagram_cookies.pkl"
        if not os.path.exists(cookie_path):
            print("No cookies found. Please log in first.")
            self.login_handler()
        else:
            print(f"Using cookies from {os.path.abspath(cookie_path)}")
        return USER_NAME

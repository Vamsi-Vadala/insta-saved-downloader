import WebdriverDownloader as wd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import pickle
import os
import bs4


USER_NAME = 'vamsi._.vadala'

class InstaLoginHandler:

    def __init__(self):
        # chrome_options.add_argument("--headless")  # Run in headless mode
        self.chrome_service = Service(wd.get_driver())

    def login_handler(self):
        chrome_options = Options()
        driver = webdriver.Chrome(service=self.chrome_service, options=chrome_options)
        driver.get("https://www.instagram.com/accounts/login/")  
        time.sleep(5)  # Wait for the page to load
        # input("Press Enter after login...")  # Wait for manual login
        while True:
            if driver.current_url == "https://www.instagram.com/" or driver.current_url == f"https://www.instagram.com/accounts/onetap/?next=%2F":
                time.sleep(2)
                break
            time.sleep(1)
        pickle.dump(driver.get_cookies(), open("instagram_cookies.pkl", "wb"))
        print("Login successful!")
        # print(driver.title)  # Print the title of the page
        driver.quit()  # Close the browser

    def get_username(self):
        if not os.path.exists("../instagram_cookies.pkl"):
            print(f"No cookies found. Please log in first.")
            self.login_handler()
        print(f'Using cookies from {os.path.abspath("instagram_cookies.pkl")}')
        # chrome_options = Options()
        # driver = webdriver.Chrome(service=self.chrome_service, options=chrome_options)
        # cookies = pickle.load(open("../instagram_cookies.pkl", "rb"))
        # driver.get("https://www.instagram.com")
        # time.sleep(5)
        # for cookie in cookies:
        #     driver.add_cookie(cookie)
        # driver.refresh()
        # time.sleep(5)
        # driver.get("https://www.instagram.com/accounts/edit/")
        # time.sleep(5)
        # bs4_obj = bs4.BeautifulSoup(driver.page_source, "html.parser")
        # with open("username.html", "wb") as f:
        #     f.write(bs4_obj.prettify("utf-8"))
        #     f.close()
        # driver.quit()

        return USER_NAME
    

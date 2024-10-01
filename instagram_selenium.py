import os
import re
import shutil
import requests
import traceback
import time

from dotenv import load_dotenv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


load_dotenv()


def parse_instagram_page(profile_name):
    try:
        service = Service("chromedriver.exe")
        driver = webdriver.Chrome(service = service)

        url = f"https://www.instagram.com/{profile_name}/"
        driver.get(url)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "meta[property='og:description']"))
        )

        full_name_meta = driver.find_element(By.CSS_SELECTOR, "meta[property='og:title']").get_attribute("content")
        match = re.match(r"^(.*?) \(@", full_name_meta)
        full_name = match.group(1) if match else ""

        profile_pic_url = driver.find_element(By.CSS_SELECTOR, "meta[property='og:image']").get_attribute("content")

        os.makedirs(profile_name, exist_ok=True)

        name_file_path = os.path.join(profile_name, f"{profile_name}_name.txt")
        with open(name_file_path, 'w', encoding = 'utf-8') as name_file:
            name_file.write(full_name)

        profile_pic_path = os.path.join(profile_name, f"{profile_name}_profile_pic.jpg")
        download_image(profile_pic_url, profile_pic_path)

        driver.quit()
        return full_name

    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())


def download_image(url, path):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(path, 'wb') as f:
                f.write(response.content)
    except Exception as e:
        print(f"Error downloading image: {e}")



def delete_folder_if_exists(folder_name):
    if os.path.isdir(folder_name):
        shutil.rmtree(folder_name)


if __name__ == '__main__':

    profiles_data = pd.read_excel("target_accounts.xlsx")

    ts = time.perf_counter()

    for index, row in profiles_data.iterrows():
        parse_instagram_page(str(row["username"]))

    tf = time.perf_counter()
    print(f"Parsed {len(profiles_data)} accounts in {round(tf - ts, 0)/60} minutes.")

import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as BS
import time
import random

from utils import get_total_page_number, read_page

# Replace with the path to your web driver
#  'C:/Users/jossl/Downloads/chromedriver_win32/chromedriver.exe'
driver = webdriver.Chrome()

# Replace with the URL of the login page
driver.get('login_url')

# Find the username and password fields
username_field = driver.find_element(
    By.XPATH, '//*[@id="ctl01_ctl00_CphBody_CphWizardBody_ctl00_ctl01_TextBox"]')
password_field = driver.find_element(By.XPATH,
                                     '//*[@id="ctl01_ctl00_CphBody_CphWizardBody_ctl00_ctl02_TextBox"]')

# Input the username and password
username_field.send_keys('username')
password_field.send_keys('password')

# Click the login button
login_button = driver.find_element(By.XPATH,
                                   '//*[@id="ctl01_ctl00_CphBody_BtnContinue"]')
login_button.click()

# Go to Directory
driver.get('directory_url')

# Set panda DataFrame
kol = pd.DataFrame()

# Init BeautifulSoup on page source
soup = BS(driver.page_source, 'lxml')

# Find total page number
total_page_number = get_total_page_number(soup)

""" 
Index indicating when the "relative page number" start incrementing again
index = total_page_number - range(8, 12) - 1 (because index start from 0)
 """
count_down = int(total_page_number) - 5

# Iterate over page indeces and click navigation links
for page in range(int(total_page_number)):
    print(page)
    time.sleep(1.5)
    if page == 0:
        print("skip")
    elif page == 1:
        driver.find_element(By.XPATH,
                            '//*[@id="ctl00_CphBody_LnkPage1_1"]').click()

    elif page > 1 and page < 7:
        driver.find_element(By.XPATH,
                            '//*[@id="ctl00_CphBody_LnkPage1_' + str(page + 1) + '"]').click()

    elif page >= 7 and page <= count_down:
        driver.find_element(By.XPATH,
                            '//*[@id="ctl00_CphBody_LnkPage1_' + "7" + '"]').click()

    else:
        for last in range(8, 12):
            driver.find_element(
                By.XPATH, '//*[@id="ctl00_CphBody_LnkPage1_' + str(last) + '"]').click()
            kol = read_page(kol, soup)
        break

    kol = read_page(kol, soup)

driver.quit()
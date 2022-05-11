#selenium_icook_1.py 登入帳號
from time import sleep
import datetime
import loguru
import configparser

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from captcha_solver import CaptchaSolver

def main():
    login()

#登入
def login():
    #進入 iCook 登入頁面
    driver.get(config['icook']['Login'])
    login_email = driver.find_element_by_name('current-email')
    login_pass = driver.find_element_by_name('current-password')
    login_button = driver.find_element_by_xpath('//button[contains(@class,"mdc-button")]')

    #填入帳密並送出
    login_email.send_keys(config['icook']['Mail'])
    login_pass.send_keys(config['icook']['Password'])
    login_button.click()

if __name__ == '__main__':
    loguru.logger.add(
        f'{datetime.date.today():%Y%m%d}.log',
        rotation='1 day',
        retention='7 days',
        level='DEBUG'
    )

    config = configparser.ConfigParser()
    config.read("config.ini")

    #Selenium with webdriver
    options = Options()
    options.binary_location = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
    webdriver_path = 'C:\\chromedriver_win32\\chromedriver.exe'
    driver = webdriver.Chrome(executable_path=webdriver_path, options=options)

    main()

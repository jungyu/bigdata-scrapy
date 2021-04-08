import sys
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
    hasNext = search('素食')
    print(hasNext)
    while hasNext == True:
        hasNext = fetch_list()
        #fetch_detail()
        #insert_update_db()

    sys.exit('爬蟲結束')

#登入
def login():
    #進入 iCook 登入頁面
    driver.get(config['icook']['Login'])
    login_email = driver.find_element_by_name('current-email')
    login_pass = driver.find_element_by_name('current-password')
    login_button = driver.find_element_by_xpath('//button[contains(@class,"mdc-button")]')

    #填入帳密並送出
    sleep(2)
    login_email.send_keys(config['icook']['Mail'])
    login_pass.send_keys(config['icook']['Password'])
    sleep(2)
    login_button.click()
    sleep(5)

#搜尋
def search(keyword):
    search_input = driver.find_element_by_name('q')
    search_input.clear()
    search_input.send_keys(keyword)
    sleep(2)

    search_button = driver.find_element_by_xpath('//button[contains(@class,"btn-search")]')
    search_button.click()
    sleep(3)

    results = driver.find_element_by_xpath('//ul[contains(@class,"result-browse-layout")]').get_attribute('innerHTML')
    if results == None:
        sys.exit('程式中止：搜尋無回應')

    return True

#取得列表
def fetch_list():
    print('fetch_list()')
    return False

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

    #列表需要的參數
    hasNext = False

    main()
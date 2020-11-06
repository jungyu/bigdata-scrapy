import time
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup
from captcha_solver import CaptchaSolver

domain = 'https://cart.books.com.tw'
login_url = 'https://cart.books.com.tw/member/login'
username = '博客來書局帳號'
password = '博客來書局密碼'

solver = CaptchaSolver('2captcha', api_key='密碼')

options = Options()
options.binary_location = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
webdriver_path = 'C:\\chromedriver_win32\\chromedriver.exe'

driver = webdriver.Chrome(executable_path=webdriver_path, options=options)

#登入
def login():
    login_id = driver.find_element_by_name('login_id')
    login_pswd = driver.find_element_by_name('login_pswd')
    captcha = driver.find_element_by_name('captcha')
    captcha_img = driver.find_element_by_id('captcha_img')
    login_button = driver.find_element_by_id('books_login')

    captcha_img.screenshot('captcha_image.png')

    #以下圖片下載方法在「博客來網站」會失敗
    #驗證圖片有時會比較慢出來，所以需要用迴圈試到出來為止
    '''
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    downloadFile = download_file(domain + soup.find(id='captcha_img').img['src'])
    
    while downloadFile == 0:
        downloadFile = download_file(domain + soup.find(id='captcha_img').img['src'])
        time.sleep(1)
    '''
    raw_data = open('captcha_image.png', 'rb').read()
    captcha_code = solver.solve_captcha(raw_data)

    login_id.clear()
    login_pswd.clear()
    captcha.clear()

    login_id.send_keys(username)
    login_pswd.send_keys(password)
    captcha.send_keys(captcha_code)
    login_button.click()

#下載驗證圖檔
def download_file(url):
    local_filename = 'captcha_image.png'
    # NOTE the stream=True parameter below
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    if chunk: 
                        f.write(chunk)

        return local_filename
    except:
        print("Error")
        return 0

driver.get(login_url)
login()
#driver.close()

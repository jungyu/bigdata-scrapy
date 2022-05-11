import requests
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup
from captcha_solver import CaptchaSolver

#台鐵訂票登入
domain = 'https://www.railway.gov.tw/'
login_url = 'https://www.railway.gov.tw/tra-tip-web/tip/tip008/tip811/memberLogin'
#request_url = 'https://www.railway.gov.tw/tra-tip-web/tip/login'
username = '帳號'
password = '密碼'

#2captcha
API_KEY = '2captcha密碼'

#Selenium with webdriver
options = Options()
options.binary_location = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
webdriver_path = 'C:\\chromedriver_win32\\chromedriver.exe'
driver = webdriver.Chrome(executable_path=webdriver_path, options=options)

#進入台鐵登入頁面
driver.get(login_url)
#取得 google recaptcha 的 data-sitekey
soup = BeautifulSoup(driver.page_source, 'html.parser')
site_key = soup.find(class_='g-recaptcha')['data-sitekey']

#https://github.com/2captcha/2captcha-api-examples/tree/master/ReCaptcha%20v2%20API%20Examples
s = requests.Session()
captcha_id = s.post("http://2captcha.com/in.php?key={}&method=userrecaptcha&googlekey={}&pageurl={}".format(
    API_KEY, site_key, login_url)).text.split('|')[1]
# then we parse gresponse from 2captcha response
recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id)).text
print("solving ref captcha...")

while 'CAPCHA_NOT_READY' in recaptcha_answer:
    sleep(5)
    recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id)).text

recaptcha_answer = recaptcha_answer.split('|')[1]

print("g-recaptcha-response:" + recaptcha_answer)

#填寫登入資訊
form_username = driver.find_element_by_name('username')
form_password = driver.find_element_by_name('password')
#grr = driver.find_element_by_name('g-recaptcha-response')
submit = driver.find_element_by_id('submitBtn')

form_username.clear()
form_password.clear()

form_username.send_keys(username)
form_password.send_keys(password)
driver.execute_script('document.querySelector("textarea.g-recaptcha-response").innerText = "' + recaptcha_answer + '"')

submit.click()

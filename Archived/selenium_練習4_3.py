from time import sleep

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from captcha_solver import CaptchaSolver

solver = CaptchaSolver('2captcha', api_key='金鑰')

options = Options()
options.binary_location = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
webdriver_path = 'C:\\chromedriver_win32\\chromedriver.exe'

#解決使用 AJAX 動態載入資料的 Single Page Application 應用問題
url = 'https://lvr.land.moi.gov.tw/login.action'

driver = webdriver.Chrome(executable_path=webdriver_path, options=options)
driver.get(url)

#1.關閉說明浮動選單
sleep(2)
dialog_close = driver.find_element_by_class_name('ui-dialog-titlebar-close').click()

#2.選不動產買買
sleep(2)
land_sale = driver.find_element_by_xpath('//div[@class="main_menu"]/ul[@class="sale"]/li/a[@id="land"]').click()

#3.通過圖形驗證
sleep(2)
checknum = driver.find_element_by_xpath('//span[@id="checknum_pan"]/img')
checknum.screenshot('captcha_image.png')
raw_data = open('captcha_image.png', 'rb').read()
captcha_code = solver.solve_captcha(raw_data)

code = driver.find_element_by_xpath('//input[@name="rand_code"]')
code.clear()
code.send_keys(captcha_code)

confirm = driver.find_element_by_xpath('//img[@name="Image2"]').click()

#關閉提示
sleep(2)
dialog_close = driver.find_element_by_class_name('close_btn').click()

#進入區域查詢畫面
sleep(2)
city = Select(driver.find_element_by_name('Qry_city'))
area = Select(driver.find_element_by_name('Qry_area_office'))

#city.select_by_index(16)
#city.select_by_visible_text("屏東縣")
city.select_by_value("T")
sleep(2)
area.select_by_value("T13")

cat_house = driver.find_element_by_name('Chkb_Qry_paytype').click()
cat_land = driver.find_element_by_name('Chkb_Qry_paytype').click()

start_year = driver.find_element_by_name('Qry_p_yyy_s')
start_year.clear()
start_year.send_keys('107')
start_month = Select(driver.find_element_by_id('Qry_season_s'))
start_month.select_by_value("1")

seach_button = driver.find_element_by_name('search_s_btn').click()

#關閉提示
sleep(10)
dialog_close = driver.find_element_by_xpath('//button[@role="button"][1]').click()

#選擇排序依據／升降冪
sleep(2)
sort_order = Select(driver.find_element_by_xpath('//select[@id="Order"]'))
sort_increase = driver.find_element_by_xpath('//a[@class="sort_btn"][1]').click()

#交易筆數選項
total = Select(driver.find_element_by_xpath('//select[@id="page_tol"]'))
for i in range(1,1000):
    try:
        print(i)
        total.select_by_index(i)
        sleep(5)
    except:
        break


#driver.close()

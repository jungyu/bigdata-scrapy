"""
說明：使用 Selenium 在 UberEats 模擬訂餐操作，未來可整合對話機器人互動操作
作者：Jung-Yu Yu jungyuyu@gmail.com 2022-05-04
授權：本著作係採用創用 CC 姓名標示 4.0 國際 授權條款授權
"""
__author__ = "Jung-Yu Yu"
__email__ = "jungyuyu@gmail.com"
__copyright__ = "Copyright 2022, The Big Data Scrapy for Python Project"
__license__ = "Creative Common 4.0"
__github__ = "https://github.com/jungyu/bigdata-scrapy"
__version__ = "0.1"
__status__ = "Beta"

from lxml import etree
from time import sleep

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()

# 找 user-agent 的網站： https://www.whatsmyua.info/
userAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36";

# 許多網站會檢查 user-agent 
options.add_argument("user-agent={}".format(userAgent))

# 不讓瀏覽器執行在前台，而是在背景執行。
# 開發前期(或在本機執行)，將以下參數註解 # 不使用，才能看的到畫面
# options.add_argument('--headless')

# 在非沙盒測試環境下，可以 root 權限運行
options.add_argument('--no-sandbox')

# 不採用 /dev/shm 作為暫存區(系統會改使用 /tmp)
options.add_argument('--disable-dev-shm-usage')

# 設定瀏覽器的解析度
# options.add_argument('--window-size=1920,1080')

# 關閉 GPU ，Google 文件提到需要加上這個參數來解決部份的 bug
# options.add_argument('--disable-gpu')

# open it, go to a website, and get results
wd = webdriver.Chrome(options=options)

#UberEats 大量的動態使用 AJAX 彈出選項，因此適合使用 Selenium (注意：它的 class 也會動態改變)
baseUrl = 'https://www.ubereats.com'
address = '屏東縣內埔鄉學府路1號'
want = '咖啡'
wantStore = '啡藏潮咖啡製造所'
wantCategory = "人氣精選"
wantItem = "經典拿鐵咖啡"
wantOption = "熱飲"

wd.get(baseUrl+'/tw')
#隱式等待：嘗試發現某個元素，如果沒能發現就等待固定長度的時間，預設設定是0秒。
wd.implicitly_wait(5)

#第一次進入，要輸入取餐地址
wd.find_element(By.ID, 'location-typeahead-home-input').send_keys(address)
wd.implicitly_wait(5)
wd.find_element(By.ID, 'location-typeahead-home-item-0').click()
wd.implicitly_wait(3)

### 進入主頁，選擇外帶，畫面會帶到「附近可自取的餐廳」###
wd.find_element(By.XPATH, '//div[@aria-label="外帶"]').click()

### 在「想吃點什麼」搜尋框，輸入want變數 ###
searchInput = WebDriverWait(wd, 10).until(expected_conditions.presence_of_element_located((By.ID, 'search-suggestions-typeahead-input')))
searchInput.send_keys(want)
searchInput.send_keys(Keys.ENTER)

### 搜尋結果列表 ###
wd.implicitly_wait(8)
results = wd.find_element(By.XPATH, '//h3/parent::a/parent::div/parent::div/parent::div/parent::div').get_attribute('innerHTML')
dom = etree.HTML(results)

#TODO:基於隱藏細節原則，應該將 function 往上移
def composeStores(dom):
    links = dom.xpath('//a/@href')
    titles = dom.xpath('//a/h3/text()')
    images = dom.xpath('//img/@src')
    stores = []

    for idx, title in enumerate(titles):
        try:
            stores.append({
                'title': titles[idx],
                'link': links[idx],
                'image': images[idx]
            })
        except:
            print("Error index:" + str(idx))

    return stores

stores = composeStores(dom)
print(stores)

### 進入使用者指定的商店 ###

#基本寫法：搜尋比對 List of dictionaries 裡的字串方法
def parseWantStore(stores, wantStore):
    for store in stores:
        for key in store:
            if key == "title" and store[key] == wantStore:
                return baseUrl + store['link']
                
#storeUrl = parseWantStore(stores, wantStore)
#高效精簡寫法： https://peps.python.org/pep-0289/
idx = next((i for i, item in enumerate(stores) if item["title"] == wantStore), None)
storeUrl = baseUrl + stores[idx]['link']
wd.get(storeUrl)
wd.implicitly_wait(5)

### 回傳商品分類，供使用者選擇 ###
results = wd.find_element(By.XPATH, '//nav[@role="navigation"]').get_attribute('innerHTML')
dom = etree.HTML(results)
categories = dom.xpath('//button/div/text()')

for category in categories:
    print(category)

### 回傳使用者指定分類裡的商品，供使用者選擇 ###
results = wd.find_element(By.XPATH, '//li/div[contains(text(),"' + wantCategory + '")]/parent::li').get_attribute('innerHTML')
dom = etree.HTML(results)

products = dom.xpath('//span/text()')
for idx in range(0, len(products), 2):
    print(products[idx] + ' ... ' + products[idx+1])

### 選購指定商品 ###
itemButton = wd.find_element(By.XPATH, '//li/div[contains(text(),"' + wantCategory + '")]/parent::li//span[contains(text(),"' + wantItem + '")]/parent::div/parent::div/following::div[1]/button')
itemButton.click()

### 在 Dialog 對話視窗內選購 ###
sleep(5)
WebDriverWait(wd, 10).until(expected_conditions.presence_of_element_located((By.XPATH, '//div[@role="dialog"]//h1')))

#等待能定位到選項按鈕(一般選項按鈕應是使用 input ，但此處使用 input 無法定位座標，應該是元素在螢幕上的座標位置不正確，由此推估操作 AJAX 點擊對應的是螢幕上的座標位置，而不是元素本身)
optionButton = WebDriverWait(wd, 10).until(expected_conditions.presence_of_element_located((By.XPATH, '//div[@role="dialog"]//label//div[contains(text(),"' + wantOption + '")]/ancestor::label')))
#將捲軸捲到 optionButton 的定位點
wd.execute_script("arguments[0].scrollIntoView()", optionButton)
optionButton.click()
wd.implicitly_wait(2)

orderButton = wd.find_element(By.XPATH, '//div[@role="dialog"]//button/div[contains(text(), "商品至訂單")]/parent::button')
orderButton.click()

# TODO:結帳->登入...
# TODO:使用 ngrok 對外提供 API 或 webhook


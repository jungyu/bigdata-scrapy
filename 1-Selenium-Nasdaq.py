"""
說明：此程式為爬取 Nasdaq 即時價格，因此需在其營運時間內爬取，部份的時段該網站並未提供即時交易行情
作者：Jung-Yu Yu jungyuyu@gmail.com 2022-05-02
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

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
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

#此網址是 Nasdaq 網站的 Tesla 即時股價，此股價在換頁時，網址並不會更動，因此適合使用 Selenium
baseUrl = 'https://www.nasdaq.com/market-activity/stocks/tsla/latest-real-time-trades'
dayTrades = []

"""
NLS Time(ET): Nasdaq 最新銷售時間(美東時區)
NLS Price: Nasdaq 最新銷售單價
NLS Share Volume: Nasdaq 交易量
"""
def composeTrade(dom):
    trades = []
    rows = dom.xpath('(//tr[@class="latest-real-time-trades__row"])')
    for row in rows:
        trades.append({
            "nlsTime": row[0].text,
            "nlsPrice": row[1].text,
            "nlsVolume": row[2].text
        })
    return trades


#第一頁
wd.get(baseUrl)
#隱式等待：嘗試發現某個元素，如果沒能發現就等待固定長度的時間，預設設定是0秒。
wd.implicitly_wait(5)

results = wd.find_element(By.XPATH, '//table[@class="latest-real-time-trades__table"]').get_attribute('innerHTML')
dom = etree.HTML(results)

#交易日
tradeDate = wd.find_element(By.XPATH, '//div[@class="symbol-page-header__timestamp"]/span[@class="symbol-page-header__status"]').text
print(tradeDate)

dayTrades = composeTrade(dom)
#持續點擊下一頁
nextButton = wd.find_element(By.XPATH, '//button[@class="pagination__next"]')
while nextButton.get_attribute('disabled') is None:
    nextButton.click()
    # 顯示等待：等待目標元素的出現，最多等待20秒
    WebDriverWait(wd, 20).until(expected_conditions.presence_of_element_located((By.XPATH, '//table[@class="latest-real-time-trades__table"]')))

    results = wd.find_element(By.XPATH, '//table[@class="latest-real-time-trades__table"]').get_attribute('innerHTML')
    dom = etree.HTML(results)
    dayTrades.extend(composeTrade(dom))
    nextButton = wd.find_element(By.XPATH, '//button[@class="pagination__next"]')
  
print(dayTrades)
wd.close()
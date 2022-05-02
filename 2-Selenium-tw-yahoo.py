"""
Windows 環境:


MacOSX 環境:
  安裝 macOS 缺少套件的管理工具 brew: https://brew.sh/index_zh-tw
  $ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

  安裝 Chrome-driver
  $ brew install cask chromedriver

  安裝 python3 (新版本預設已內含 pip)
  $ brew install python3

  安裝 pip 虛擬環境
  $ python3 -m venv myenv

  切換到指定的 pip 虛擬環境，此處為 myenv
  $ source ~/myenv/bin/activate

  安裝 selenium
  $ python3 -m pip install selenium

  安裝lxml
  $ python3 -m pip install lxml
"""

from lxml import etree

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException

import time

options = webdriver.ChromeOptions()
# 找 user-agent 的網站： https://www.whatsmyua.info/
userAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36";
# 許多網站會檢查 user-agent
options.add_argument("user-agent={}".format(userAgent))
# 不讓瀏覽器執行在前台，而是在背景執行，開發前期(或在本機執行)先不加才看的到畫面
# options.add_argument('--headless')
# 在非沙盒測試環境下，可以 root 權限運行
options.add_argument('--no-sandbox')
# 不以 /dev/shm 作為暫存區(使用 /tmp)
options.add_argument('--disable-dev-shm-usage')
# 設定瀏覽器的解析度
#options.add_argument('--window-size=1920,1080')
# 關閉 GPU ，Google 文件提到需要加上這個參數以解決部份的 bug
# options.add_argument('--disable-gpu')

# open it, go to a website, and get results
wd = webdriver.Chrome(options=options)

#此網址是 Yahoo!股市網站的中鋼2002即時股價，收錄當日成交彙整資料時，會發現其使用「載入更多」，而網址並不會更動，因此適合使用 Selenium
#股市原始資料來自：https://mis.twse.com.tw/stock/fibest.jsp?stock=2002 ，但它的介面如果要隨時盯著它的價格刷新，需要另外技巧來達成
baseUrl = 'https://tw.stock.yahoo.com/quote/2002/time-sales'
dayTrades = {}

def composeTrade(dom):
    rows = dom.xpath('(//div[@class="table-body-wrapper"]/ul/li/div)')

    for row in rows:
        if row[0].text is not None:
            dayTrades[row[0].text] = [
                row[1].xpath('./span')[0].text,
                row[3].xpath('./span')[0].text
             ]

#第一頁
wd.get(baseUrl)
#隱式等待：是在嘗試發現某個元素的時候，如果沒能立刻發現，就等待固定長度的時間。預設設定是0秒。
wd.implicitly_wait(5)

#交易日
#//div[@id="main-0-QuoteHeader-Proxy"]/div/div[2]/div/span
tradeDate = wd.find_element(By.XPATH, '//div[contains(@class, "qsp-ts-price-by-volumes")]/div/span').text
print(tradeDate)

#持續點擊「載入更多」
nextButton = wd.find_element(By.XPATH, '//span[contains(text(),"載入更多")]/parent::*/parent::button')
while nextButton:
    #等待能定位到新的「載入更多」按鈕
    bottom = WebDriverWait(wd, 10).until(expected_conditions.presence_of_element_located((By.XPATH, '//span[contains(text(),"載入更多")]/parent::*/parent::button')))
    #將捲軸捲到 bottom 的定位點
    wd.execute_script("arguments[0].scrollIntoView()", bottom)
    #要視實際載入內容的速度，進行秒數的調整
    time.sleep(1)
    results = wd.find_element(By.XPATH, '//section[@id="qsp-ts-price-by-time"]').get_attribute('innerHTML')
    dom = etree.HTML(results)
    composeTrade(dom)

    try:
        nextButton.click()
        nextButton = wd.find_element(By.XPATH, '//span[contains(text(),"載入更多")]/parent::*/parent::button')
        print('.',end = '')
    except TimeoutException:
        break
    except StaleElementReferenceException:
        break

print(dayTrades)
wd.close()
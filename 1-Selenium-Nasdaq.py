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
# options.add_argument('--window-size=1920,1080')
# 關閉 GPU ，Google 文件提到需要加上這個參數以解決部份的 bug
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
#隱式等待：是在嘗試發現某個元素的時候，如果沒能立刻發現，就等待固定長度的時間。預設設定是0秒。
wd.implicitly_wait(5)

results = wd.find_element(By.XPATH, '//table[@class="latest-real-time-trades__table"]').get_attribute('innerHTML')
dom = etree.HTML(results)
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
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

"""
安裝相依套件：
 python -m pip install lxml
 python -m pip install webdriver-manager
 python -m pip install selenium
"""

from lxml import etree

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import time

#此網址是 Nasdaq 網站的 Tesla 即時股價，此股價在換頁時，網址並不會更動，因此適合使用 Selenium
__baseUrl__ = 'https://www.nasdaq.com/market-activity/stocks/tsla/latest-real-time-trades'

def main():
    dayTrades = []

    #第一頁
    wd.get(__baseUrl__)
    #隱式等待：嘗試發現某個元素，如果沒能發現就等待固定長度的時間，預設設定是0秒。
    wd.implicitly_wait(5)

    # 禁用動畫
    wd.execute_script("document.body.style.webkitAnimationPlayState='paused'")

    results = wd.find_element(By.XPATH, '//table[@class="latest-real-time-trades__table"]').get_attribute('innerHTML')
    dom = etree.HTML(results)

    #交易日
    tradeDate = wd.find_element(By.XPATH, '//div[@class="symbol-page-header__timestamp"]/span[@class="symbol-page-header__status"]').text
    print(tradeDate)

    dayTrades = composeTrade(dom)
    #持續點擊下一頁
    # nextButton = wd.find_element(By.XPATH, '//button[@class="pagination__next"]')
    nextButtonXpath = '//button[@class="pagination__next"]'
    while True:
        try:
            # 顯示等待：等待目標元素的出現，最多等待20秒
            wait = WebDriverWait(wd, 10)
            element = wait.until(EC.element_to_be_clickable((By.XPATH, nextButtonXpath)))

            #將捲軸捲到 bottom 的定位點
            wd.execute_script("arguments[0].scrollIntoView()", element)

            # 移動到該元素上方再進行點擊
            actions = ActionChains(wd)
            actions.move_to_element(element)

            #要視實際載入內容的速度，進行秒數的調整
            time.sleep(5)
            results = wd.find_element(By.XPATH, '//table[@class="latest-real-time-trades__table"]').get_attribute('innerHTML')
            dom = etree.HTML(results)
            dayTrades.extend(composeTrade(dom))

            # 使用 JavaScript 點擊該元素
            wd.execute_script("arguments[0].click();", element)
            print('.',end = '')
        except TimeoutException:
            break
        except StaleElementReferenceException:
            break
  
    print(dayTrades)
    wd.close()    

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

if __name__ == '__main__':

    options = Options()

    # 排除項目： 1. automation 自動軟體正在控制您的瀏覽器 2. logging 日誌記錄 3. Extension 擴展
    options.add_experimental_option("excludeSwitches", ["enable-automation", 'enable-logging'])
    options.add_experimental_option('useAutomationExtension', False)
    # 暫先停用密碼管理員及憑證服務
    options.add_experimental_option("prefs", {"profile.password_manager_enabled": False, "credentials_enable_service": False})
    # 預設使用 chromium 核心
    options.use_chromium = True

    # 許多網站會檢查 user-agent 
    # 找 user-agent 的網站： https://www.whatsmyua.info/
    userAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36";
    options.add_argument("user-agent={}".format(userAgent))

    # 不讓瀏覽器執行在前台，而是在背景執行。
    # 開發前期(或在本機執行)，將以下參數註解 # 不使用，才能看的到畫面
    # options.add_argument('--headless')

    # 在非沙盒測試環境下，可以 root 權限運行
    options.add_argument('--no-sandbox')

    # 不採用 /dev/shm 作為暫存區(系統會改使用 /tmp)
    options.add_argument('--disable-dev-shm-usage')

    # 設定瀏覽器的解析度
    options.add_argument("--start-maximized")
    # options.add_argument('--window-size=1920,1080')

    # 關閉 GPU ，Google 文件提到需要加上這個參數來解決部份的 bug
    # options.add_argument('--disable-gpu')

    # 宣告 webdriver 實體
    wd = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    main()

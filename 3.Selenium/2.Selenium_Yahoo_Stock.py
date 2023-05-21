"""
說明：使用 Selenium 從 Yahoo 股市，擷取台灣上市股票之成交彙整資料，以中鋼為例
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

#此網址是 Yahoo!股市網站的中鋼2002即時股價，收錄當日成交彙整資料時，會發現其使用「載入更多」，而網址並不會更動，因此適合使用 Selenium
#股市原始資料來自：https://mis.twse.com.tw/stock/fibest.jsp?stock=2002 ，但它的介面如果要隨時盯著它的價格刷新，需要另外技巧來達成
__baseUrl__ = 'https://tw.stock.yahoo.com/quote/2002/time-sales'
dayTrades = {}

def main():

    #第一頁
    wd.get(__baseUrl__)
    #隱式等待：是在嘗試發現某個元素的時候，如果沒能立刻發現，就等待固定長度的時間。預設設定是0秒。
    wd.implicitly_wait(5)

    # 禁用動畫
    wd.execute_script("document.body.style.webkitAnimationPlayState='paused'")

    #交易日
    tradeDate = wd.find_element(By.XPATH, '//div[contains(@class, "qsp-ts-price-by-volumes")]/div/span').text
    print(tradeDate)

    nextButtonXpath = '//span[contains(text(),"載入更多")]/parent::*/parent::button'
    #新增CloseAD,以避免64行及小螢幕出現無法偵測的問題
    closeAD = wd.find_element(By.XPATH, '//button[@class="Fxs(0) H(24px) B(n) Mt(20px) P(0) As(fs)"]')
    closeAD.click()
    #持續點擊「載入更多」
    while wd.find_element(By.XPATH, nextButtonXpath):
        # 等待元素可被點擊
        wait = WebDriverWait(wd, 10)
        element = wait.until(EC.element_to_be_clickable((By.XPATH, nextButtonXpath)))

        # 移動到該元素上方再進行點擊
        actions = ActionChains(wd)
        actions.move_to_element(element).click().perform()

        #將捲軸捲到 bottom 的定位點
        wd.execute_script("arguments[0].scrollIntoView()", element)

        #要視實際載入內容的速度，進行秒數的調整
        time.sleep(5)
        results = wd.find_element(By.XPATH, '//section[@id="qsp-ts-price-by-time"]').get_attribute('innerHTML')
        dom = etree.HTML(results)
        composeTrade(dom)

        try:
            # 使用 JavaScript 點擊該元素
            wd.execute_script("arguments[0].click();", element)
            print('.',end = '')
        except TimeoutException:
            break
        except StaleElementReferenceException:
            break

    print(dayTrades)
    wd.close()

def composeTrade(dom):
    rows = dom.xpath('(//div[@class="table-body-wrapper"]/ul/li/div)')

    for row in rows:
        if row[0].text is not None:
            dayTrades[row[0].text] = [
                row[1].xpath('./span')[0].text,
                row[3].xpath('./span')[0].text
            ]


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

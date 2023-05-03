"""
說明：使用 Selenium 擷取指定蝦皮賣場內的全部商品及價格，寫到 SQL 資料庫
作者：Jung-Yu Yu jungyuyu@gmail.com 2022-05-05
授權：本著作係採用創用 CC 姓名標示 4.0 國際 授權條款授權
"""
__author__ = "Jung-Yu Yu"
__email__ = "jungyuyu@gmail.com"
__copyright__ = "Copyright 2022, The Big Data Scrapy for Python Project"
__license__ = "Creative Common 4.0"
__github__ = "https://github.com/jungyu/bigdata-scrapy"
__version__ = "0.1"
__status__ = "Beta"

import random
import json
import re

from datetime import datetime
from bs4 import BeautifulSoup
from lxml import etree
from time import sleep

import loguru

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

#蝦皮使用 js 載入商品列表，因此適合使用 Selenium
__baseUrl__ = 'https://shopee.tw'
__storeUrl__ = '/hsu6666'
__storeName__ = '娜娜正版專賣'

#2023年4月之後欲檢視蝦皮商品詳細頁，需先登入才行。
__user__ = ''
__password__ = ''

def main():
    productList = fetchProductList()
    # 登入蝦皮帳號(2023.4 Shopee 設定商品內頁需登入才能檢視)
    login()
    sleep(random.randint(5000, 8000)/1000)
    # 去除重複的連結
    productList = [dict(t) for t in {tuple(d.items()) for d in productList}] 
    products = fetchProducts(productList)
    saveJsonFile(products)

def fetchProductList():
    # 第一頁
    wd.get(__baseUrl__ + __storeUrl__ + '?sortBy=ctime&page=0#product_list')
    
    # 取得全部頁數
    totalPageElement = '//span[@class="shopee-mini-page-controller__total"]'
    WebDriverWait(wd, 10).until(EC.presence_of_element_located((By.XPATH, totalPageElement)))
    totalPage = wd.find_element(By.XPATH, totalPageElement).text
    productList = []
    #測試時，若筆數太多造成處理時間冗長，建議註解以下分頁迴圈處理
    for pageNumber in range(0, int(totalPage), 1):
        print('Feteching Page: ' + str(pageNumber))
        productList += fetchProductListByPage(pageNumber)
        
    print(productList)
    return productList

def fetchProductListByPage(pageNumber):
    wd.get(__baseUrl__ + __storeUrl__ + '?sortBy=ctime&page=' + str(pageNumber) + '#product_list')
    sleep(random.randint(500, 8000)/1000)
    # ResultView = WebDriverWait(wd, 20).until(EC.presence_of_element_located((By.XPATH, '//div[@class="shop-search-result-view"]')))
    ResultView = WebDriverWait(wd, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.shop-search-result-view')))

    try:
        #滾動到指定元素底部
        wd.execute_script("arguments[0].scrollIntoView(false)", ResultView)
        sleep(random.randint(5000, 8000)/1000)
        # results = WebDriverWait(wd, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="shop-search-result-view"]'))).get_attribute('innerHTML')
        results = WebDriverWait(wd, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.shop-search-result-view'))).get_attribute('innerHTML')
        dom = etree.HTML(results)
    # 若發生錯誤，再重新執行一次
    except TimeoutException:
        fetchProductListByPage(pageNumber)
    except StaleElementReferenceException:
        fetchProductListByPage(pageNumber)

    return composeProducts(dom)

def login():
    wd.get(__baseUrl__ + '/buyer/login')
    # sleep(random.randint(5000, 8000)/1000)
    userInput = WebDriverWait(wd, 5).until(EC.presence_of_element_located((By.XPATH, '//input[@name="loginKey"]')))
    userInput.send_keys(__user__)
    passInput = WebDriverWait(wd, 5).until(EC.presence_of_element_located((By.XPATH, '//input[@name="password"]')))
    passInput.send_keys(__password__)
    loginButton = WebDriverWait(wd, 5).until(EC.element_to_be_clickable((By.XPATH, '//button[text()="登入"]')))
    # 移動到該元素上方再進行點擊
    actions = ActionChains(wd)
    actions.move_to_element(loginButton).click().perform()


def fetchProducts(productList):
    products = []
    for idx, list in enumerate(productList):
        print('Feteching Product Index: ' + str(idx))
        try:
            wd.get(__baseUrl__ + list['link'])
            # wd.execute_script('document.cookie = "af-ac-enc-dat=null"')
            sleep(random.randint(8000, 10000)/1000)
            # etree.HTML(results) 回傳 None，可能是 Shopee 的 html 有誤，裡頭可能夾雜了無法正確解析的字元，所以改用 BeautifulSoup 來解析
            results = WebDriverWait(wd, 20).until(EC.presence_of_element_located((By.ID, "main"))).get_attribute('innerHTML')
            soup = cleanHTMLTag(results)
            # dom = etree.HTML(results)
            if soup is not None:
                products.append(parseProductDetail(soup, list))
        except TimeoutException:
            continue
    
    return products

def cleanHTMLTag(html):
    # 將 HTML 字串轉換成 BeautifulSoup 物件
    soup = BeautifulSoup(html, 'html.parser')
    # 刪除所有 <style> 標籤
    for tag in soup.find_all('style'):
        tag.extract()
    # 刪除所有 <path> 標籤
    for tag in soup.find_all('path'):
        tag.extract()
    # 刪除所有 <polygon> 標籤
    for tag in soup.find_all('polygon'):
        tag.extract() 
    # 刪除所有 <svg> 標籤
    for tag in soup.find_all('svg'):
        tag.extract()
    # 刪除所有 <g> 標籤
    for tag in soup.find_all('g'):
        tag.extract()

    # 使用 prettify() 函式進行格式整齊化
    prettified_html = soup.prettify()
    soup = BeautifulSoup(prettified_html, 'html.parser')
    return soup

def parseProductDetail(soup, list):

    # '//div[contains(text(), "$")][1]/text()'
    price = ''
    price_elem = soup.find('div', {'class': 'product-briefing'}).find(string=re.compile('\$'))
    if price_elem:
        price = price_elem.text.strip()
    price = price.replace("$", "")

    # '//label[contains(text(), "商品數量")]/following::div[1]/text()'
    stock = ''
    stock_elem = soup.select_one('label:-soup-contains("商品數量") + div')
    if stock_elem:
        stock = stock_elem.text.strip()

    # '//label[contains(text(), "出貨地")]/following::div[1]/text()'
    fromAddress = ''
    fromAddress_elem = soup.select_one('label:-soup-contains("出貨地") + div')
    if fromAddress_elem:
        fromAddress = fromAddress_elem.text.strip()

    # '//div[contains(text(), "商品詳情")]/following::div[1]'
    detail = ''
    detail_elem = soup.select_one('div:-soup-contains("商品詳情") + div')
    if detail_elem:
        detail = detail_elem.prettify()
        # 將 HTML 解析成 BeautifulSoup 物件
        detail_soup = BeautifulSoup(detail, 'html.parser')
        # 取得所有內容文字
        detail = detail_soup.get_text()
        # 不管是斷行幾次，都改成只斷行1次
        detail = re.sub(r'\n+', '\n', detail)

    # '//div[contains(text(), "商品規格")]/following::div[1]'
    spec = ''
    spec_elem = soup.select_one('div:-soup-contains("商品規格") + div')
    if spec_elem:
        spec = etree.HTML(spec_elem.prettify())
    
    length = ''
    try:
        length = parseProductSpec(spec, "長度")
        length = handleList(length)
    except:
        print("長度：解析錯誤")

    width = ''
    try:
        width = parseProductSpec(spec, "寬")
        width = handleList(width)
    except:
        print("寬：解析錯誤")

    # '//label[contains(text(),"分類")]/following::a/text()'
    tag_elems = soup.select('label:-soup-contains("分類") + div a')
    tags = [tag_elem.text.strip() for tag_elem in tag_elems if tag_elem.text.strip() != '蝦皮購物']

    # '//div[contains(@style,"background-image: ")]/@style'
    images = parseProductImages(soup.select('div[style*="background-image:"]'))

    return {
        'title': list['title'],
        'link': list['link'], 
        'price': price,
        'stock': stock,
        'tags': tags,
        'length': length,
        'width': width,
        'fromAddress': fromAddress,
        'detail': detail,
        'images': images
    }

def parseProductSpec(spec, text):
    try:
        return spec.xpath('//label[contains(text(),"' + text + '")]/following::div[1]/text()')
    except:
        return ''

def parseProductImages(styles):
    imageUrls = []
    for style in styles:
        style_str = style['style']
        match = re.search(r'url\((.*)\)', style_str)
        if match:
            image = match.group(1)
            if image:
                imageUrls.append(image.split("\"")[1])
    return imageUrls
    
def handleList(object):
    if isinstance(object, list) and len(object) > 0:
        object = object[0]
    else:
        object = ''
    return object

def composeProducts(dom):
    if dom is None:
        return []
    links = dom.xpath('//div[contains(@class, "shop-search-result-view__item")]/a/@href')
    titles = dom.xpath('//div[contains(@class, "shop-search-result-view__item")]/a//img/@alt')
    products = []
    for idx, link in enumerate(links):
        try:
            products.append({
                'title': titles[idx],
                'link': links[idx]
            })
        except:
            print("Error index:" + str(idx))

    return products

def saveJsonFile(products):
    with open(__storeName__ + datetime.now().strftime("_%Y%m%d") + ".json", "w", encoding='utf-8') as outfile:
        json.dump(products, outfile, ensure_ascii=False)    

#清空字串內全部的 html tag，只留下內文
TAG_RE = re.compile(r'<[^>]+>')
def remove_tags(text):
    return TAG_RE.sub('', text)

if __name__ == '__main__':
    loguru.logger.add(
        f'./logs/{datetime.now().strftime("%Y%m%d%m%H%M%S")}.log',
        rotation='1 day',
        retention='7 days',
        level='DEBUG'
    )

    options = Options()

    # 排除項目： 1. automation 自動軟體控制您的瀏覽器 2. logging 日誌記錄 3. Extension 擴展
    options.add_experimental_option("excludeSwitches", ["enable-automation", 'enable-logging'])
    options.add_experimental_option('useAutomationExtension', False)
    # 暫先停用密碼管理員及憑證服務
    options.add_experimental_option("prefs", {"profile.password_manager_enabled": False, "credentials_enable_service": False, "profile.default_content_setting_values.notifications" : 2})
    # Selenium 執行完後不關閉瀏覽器
    # options.add_experimental_option('detach', True)
    # 最小化瀏覽器視窗
    # options.add_argument('headless') 
    # 設置瀏覽器視窗大小為 1920x1080
    # options.add_argument('window-size=1920x1080') 
    # 不載入圖片，提升爬蟲速度
    options.add_argument('blink-settings=imagesEnabled=false') 

    # 預設使用 chromium 核心
    options.use_chromium = True

    # 許多網站會檢查 user-agent 
    # 找 user-agent 的網站： https://www.whatsmyua.info/
    userAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    options.add_argument("user-agent={}".format(userAgent))

    # 不讓瀏覽器執行在前台，而是在背景執行。
    # 開發前期(或在本機執行)，將以下參數註解 # 不使用，才能看的到畫面
    # options.add_argument('--headless')

    # 在非沙盒測試環境下，可以 root 權限運行
    options.add_argument('--no-sandbox')

    # 不採用 /dev/shm 作為暫存區(系統會改使用 /tmp)
    options.add_argument('--disable-dev-shm-usage')

    # 設定瀏覽器的解析度
    # options.add_argument("--start-maximized")
    # options.add_argument('--window-size=1920,1080')

    # 關閉 GPU ，Google 文件提到需要加上這個參數來解決部份的 bug
    # options.add_argument('--disable-gpu')

    # 宣告 webdriver 實體
    wd = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # 禁用動畫
    # wd.execute_script("document.body.style.webkitAnimationPlayState='paused'")

    # 偵測是否已載入
    main()

    # 關閉瀏覽器
    wd.quit()

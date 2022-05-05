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
import html
import urllib
import configparser
import re

from datetime import datetime
from lxml import etree
from time import sleep

import loguru
import sqlalchemy
import sqlalchemy.ext.automap
import sqlalchemy.orm
import sqlalchemy.schema

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()
# 找 user-agent 的網站： https://www.whatsmyua.info/
userAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
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

#蝦皮使用 js 載入商品列表，因此適合使用 Selenium
baseUrl = 'https://shopee.tw'
storeUrl = '/hsu6666'
storeName = '娜娜正版專賣'

def main():
    wd.get(baseUrl + storeUrl + '?sortBy=ctime&page=0#product_list')
    sleep(random.randint(5000, 8000)/1000)
    productList = fetchProductList()
    #去除重複的連結
    productList = [dict(t) for t in {tuple(d.items()) for d in productList}] 
    products = fetchProducts(productList)
    saveJsonFile(products)

def fetchProductList():
    #Shopee 的商品列表是採取 AJAX 延遲載入(疑似無法擷取到全部商品)
    ResultView = WebDriverWait(wd, 10).until(expected_conditions.presence_of_element_located((By.XPATH, '//div[@class="shop-search-result-view"]')))
    #滾動到指定元素底部
    wd.execute_script("arguments[0].scrollIntoView(false)", ResultView)
    sleep(random.randint(5000, 8000)/1000)
    results = WebDriverWait(wd, 10).until(expected_conditions.presence_of_element_located((By.XPATH, '//div[@class="shop-search-result-view"]'))).get_attribute('innerHTML')
    dom = etree.HTML(results)
    list = composeProducts(dom)
    totalPage = wd.find_element(By.XPATH, '//span[@class="shopee-mini-page-controller__total"]').text
    '''
    for pageNumber in range(1, int(totalPage), 1):
        print('Feteching Page: ' + str(pageNumber))
        list += fetchProductListByPage(pageNumber)
    '''
    return list

def fetchProductListByPage(pageNumber):
    wd.get(baseUrl + storeUrl + '?sortBy=ctime&page=' + str(pageNumber) + '#product_list')
    sleep(random.randint(5000, 8000)/1000)
    ResultView = WebDriverWait(wd, 10).until(expected_conditions.presence_of_element_located((By.XPATH, '//div[@class="shop-search-result-view"]')))
    #滾動到指定元素底部
    wd.execute_script("arguments[0].scrollIntoView(false)", ResultView)
    sleep(random.randint(5000, 8000)/1000)
    results = WebDriverWait(wd, 10).until(expected_conditions.presence_of_element_located((By.XPATH, '//div[@class="shop-search-result-view"]'))).get_attribute('innerHTML')
    dom = etree.HTML(results)
    return composeProducts(dom)

def fetchProducts(productList):
    products = []
    for idx, list in enumerate(productList):
        print('Feteching Product Index: ' + str(idx))
        wd.get(baseUrl + list['link'])
        sleep(random.randint(5000, 8000)/1000)
        results = WebDriverWait(wd, 10).until(expected_conditions.presence_of_element_located((By.XPATH, '//div[@class="page-product"]'))).get_attribute('innerHTML')
        dom = etree.HTML(results)
        products.append(parseProductDetail(dom, list))
    
    return products

def parseProductDetail(dom, list):
    price = dom.xpath('//div[contains(text(), "$")][1]/text()')
    price = handleList(price)
    price = price.replace("$", "")

    stock = dom.xpath('//label[contains(text(), "商品數量")]/following::div[1]/text()')
    stock = handleList(stock)

    fromAddress = dom.xpath('//label[contains(text(), "出貨地")]/following::div[1]/text()')
    fromAddress = handleList(fromAddress)

    detail = dom.xpath('//div[contains(text(), "商品詳情")]/following::div[1]')
    if len(detail) > 0:
        detail = detail[0]
        detail = remove_tags(etree.tostring(detail, encoding='unicode', pretty_print=True))
    else:
        detail = ''

    spec = dom.xpath('//div[contains(text(), "商品規格")]/following::div[1]')
    if len(spec) > 0:
        spec = spec[0]

    length = parseProductSpec(spec, "長度")
    length = handleList(length)

    width = parseProductSpec(spec, "寬")
    width = handleList(width)

    tags = dom.xpath('//label[contains(text(),"分類")]/following::a/text()')
    if len(tags) > 0:
        tags.remove('蝦皮購物')
    else:
        tags = []

    images = parseProductImages(dom.xpath('//div[contains(@style,"background-image: ")]/@style'))

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

def parseProductImages(images):
    imageUrls = []
    for image in images:
        imageUrls.append(image.split("\"")[1])
    return imageUrls
    
def handleList(object):
    if isinstance(object, list) and len(object) > 0:
        object = object[0]
    else:
        object = ''
    return object

def composeProducts(dom):
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
    with open(storeName + datetime.now().strftime("_%Y%m%d%m") + ".json", "w", encoding='utf-8') as outfile:
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

    main()

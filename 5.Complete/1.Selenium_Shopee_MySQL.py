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
import time
import html
import urllib
import configparser
from datetime import datetime
from time import sleep

from lxml import etree

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import loguru
import sqlalchemy
import sqlalchemy.ext.automap
import sqlalchemy.orm
import sqlalchemy.schema

__wp_posts_table__ = 'wp_posts'
__wp_postmeta_table__ = 'wp_postmeta'
__wp_term_relationships_table__ = 'wp_term_relationships'
__wp_term_taxonomy_table__ = 'wp_term_taxonomy'
__wp_termmeta_table__ = 'wp_termmeta'
__wp_terms_table__ = 'wp_terms'

__post_type__ = 'product'
__taxonomy_name__ = 'product_cat'
__category_name__ = 'NaNa正版專賣'


#蝦皮使用 js 載入商品列表，因此適合使用 Selenium
__baseUrl__ = 'https://shopee.tw'
__storeUrl__ = '/hsu6666'
__storeName__ = '娜娜正版專賣'

def main():
    wd.get(__baseUrl__ + __storeUrl__ + '?sortBy=ctime&page=0#product_list')
    sleep(random.randint(5000, 8000)/1000)
    productList = fetchProductList()
    #去除重複的連結
    productList = [dict(t) for t in {tuple(d.items()) for d in productList}] 
    products = fetchProducts(productList)
    saveJsonFile(products)

    data = parse_JSON()
    #寫入資料庫
    to_wordpress(data)    

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
    #測試時，若筆數太多造成處理時間冗長，建議註解以下分頁迴圈處理
    for pageNumber in range(1, int(totalPage), 1):
        print('Feteching Page: ' + str(pageNumber))
        list += fetchProductListByPage(pageNumber)

    return list

def fetchProductListByPage(pageNumber):
    wd.get(__baseUrl__ + __storeUrl__ + '?sortBy=ctime&page=' + str(pageNumber) + '#product_list')
    sleep(random.randint(5000, 8000)/1000)
    ResultView = WebDriverWait(wd, 20).until(expected_conditions.presence_of_element_located((By.XPATH, '//div[@class="shop-search-result-view"]')))
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
        wd.get(__baseUrl__ + list['link'])
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
    with open(__storeName__ + datetime.now().strftime("_%Y%m%d") + ".json", "w", encoding='utf-8') as outfile:
        json.dump(products, outfile, ensure_ascii=False)  

# 讀取 JSON 格式資料
def parse_JSON():
    with open(__filename__) as json_file:
        return json.load(json_file)

def to_wordpress(posts):
    loguru.logger.info('寫入 WordPress 資料結構')
    termIds = find_or_insert_term(__taxonomy_name__, __category_name__)
    insert_or_update_posts(termIds, posts)

def insert_or_update_posts(termIds, posts):
    loguru.logger.info('新增或更新商品')

    current_time = datetime.now().timetuple()

    sqlalchemy.Table(__wp_posts_table__, metadata, autoload=True)
    Poststable = automap.classes[__wp_posts_table__] 

    for post in posts:
        post = Struct(**post)
        loguru.logger.info(post.title)

        slug = urllib.parse.quote(post.title, encoding="utf8")
        slug = 'shop_' + str(termIds) + '_' + slug[:120]
        loguru.logger.info(slug)

        if find_duplicate(slug) == False:


            poststable = Poststable()
            poststable.post_author = '1'
            poststable.post_date = current_time
            poststable.post_date_gmt = current_time
            poststable.post_content = post.detail
            poststable.post_title = post.title
            poststable.post_excerpt = ''
            poststable.post_status = 'publish'
            poststable.comment_status = 'closed'
            poststable.ping_status = 'closed'
            poststable.post_password = ''
            poststable.post_name = slug
            poststable.to_ping = ''
            poststable.pinged = ''
            poststable.post_modified =  current_time
            poststable.post_modified_gmt = current_time
            poststable.post_content_filtered = ''
            poststable.post_parent = '0'
            poststable.guid = ''
            poststable.menu_order = 0
            poststable.post_type = __post_type__
            poststable.post_mime_type = ''
            poststable.comment_count = '0'
            session.add(poststable)
            session.flush()

            process_postmeta(poststable.ID, post)
            process_categories(poststable.ID, termIds)

    try:
        session.commit()
    except Exception as e:
        loguru.logger.error('新增資料失敗')
        loguru.logger.error(e)
        session.rollback()
    finally:
        session.close()


def process_postmeta(ID, post):
    loguru.logger.info('process_postmeta')
    sqlalchemy.Table(__wp_postmeta_table__, metadata, autoload=True)
    Postmetatable = automap.classes[__wp_postmeta_table__]

    #link
    postmetatable = Postmetatable()
    postmetatable.post_id = ID
    postmetatable.meta_key = 'link'
    postmetatable.meta_value = post.link
    session.add(postmetatable)
    session.flush()

    #price
    postmetatable = Postmetatable()
    postmetatable.post_id = ID
    postmetatable.meta_key = 'price'
    postmetatable.meta_value = post.price
    session.add(postmetatable)
    session.flush()

    #stock
    postmetatable = Postmetatable()
    postmetatable.post_id = ID
    postmetatable.meta_key = 'stock'
    postmetatable.meta_value = post.stock
    session.add(postmetatable)
    session.flush()

    #images
    postmetatable = Postmetatable()
    postmetatable.post_id = ID
    postmetatable.meta_key = 'images'
    postmetatable.meta_value = ",".join(str(x) for x in post.images)
    session.add(postmetatable)
    session.flush()

    #tags
    postmetatable = Postmetatable()
    postmetatable.post_id = ID
    postmetatable.meta_key = 'tags'
    postmetatable.meta_value = ",".join(str(x) for x in post.tags)
    session.add(postmetatable)
    session.flush()

def process_categories(ID, termIds):
    loguru.logger.info('process_categories')
    find_or_insert_relation(ID, termIds)
    #TOFIX: count to taxonomy

def find_duplicate(slug):
    sqlalchemy.Table(__wp_posts_table__, metadata, autoload=True)
    Poststable = automap.classes[__wp_posts_table__] 

    post = session.query(
        Poststable
    ).filter(
        Poststable.post_name == slug
    ).first()

    if post:
        loguru.logger.info('Find duplicate id: ' + str(post.ID))
        return True
    else:
        return False

def find_or_insert_term(taxonomy, topics):
    loguru.logger.info('find_or_insert_term')
    slug = urllib.parse.quote(topics, encoding="utf8")
    loguru.logger.info(slug)

    sqlalchemy.Table(__wp_terms_table__, metadata, autoload=True)
    Termstable = automap.classes[__wp_terms_table__]

    sqlalchemy.Table(__wp_term_taxonomy_table__, metadata, autoload=True)
    Taxonomytable = automap.classes[__wp_term_taxonomy_table__]

    #查詢是不是已有同名的分類或標籤
    term = session.query(
        Termstable, Taxonomytable
    ).filter(
        Termstable.name == topics,
        Taxonomytable.taxonomy == taxonomy,
        Termstable.term_id == Taxonomytable.term_id
    ).with_entities(
        Termstable.term_id,
        Taxonomytable.term_taxonomy_id
    ).first()

    if term:
        loguru.logger.info('Find exist term id: ' + str(term.term_taxonomy_id))
        return term.term_taxonomy_id


    termstable = Termstable()
    termstable.name = topics
    termstable.slug = slug
    termstable.term_group = '0'
    session.add(termstable)
    session.flush()

    term_id = termstable.term_id
        
    taxonomytable = Taxonomytable()
    taxonomytable.term_id = term_id
    taxonomytable.taxonomy = __taxonomy_name__
    taxonomytable.description = ''
    taxonomytable.parent = '0'
    session.add(taxonomytable)
    session.flush()

    try:
        session.commit()
    except Exception as e:
        loguru.logger.error('新增分類失敗')
        loguru.logger.error(e)
        session.rollback()
        return 0
    finally:
        return term_id

def find_or_insert_relation(ID, termIds):
    loguru.logger.info('find_or_insert_relation')
    sqlalchemy.Table(__wp_term_relationships_table__, metadata, autoload=True)
    Relationtable = automap.classes[__wp_term_relationships_table__]
    relationtable = Relationtable()
    relationtable.object_id = ID
    relationtable.term_taxonomy_id = termIds
    relationtable.term_order = '0'
    session.add(relationtable)
    session.flush()

#將 dict 轉物件
class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)

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

    #取得資料庫連線設定
    config = configparser.ConfigParser()
    config.read("config.ini")

    host = config['mysql']['Host']
    port = int(config['mysql']['Port'])
    username = config['mysql']['User']
    password = config['mysql']['Password']
    database = config['mysql']['Database']
    chartset = config['mysql']['Charset']

    # 建立連線引擎
    connect_string = connect_string = 'mysql+mysqlconnector://{}:{}@{}:{}/{}?charset={}'.format(username, password, host, port, database, chartset)
    connect_args = {'connect_timeout': 10}
    engine = sqlalchemy.create_engine(connect_string, connect_args=connect_args, echo=False)
    
    # 取得資料庫元資料
    metadata = sqlalchemy.schema.MetaData(engine)
    # 產生自動對應參照
    automap = sqlalchemy.ext.automap.automap_base()
    automap.prepare(engine, reflect=True)
    # 準備 ORM 連線
    session = sqlalchemy.orm.Session(engine)

    main()

#selenium_icook_5.py 完成寫入資料庫
#pip install SQLAlchemy
#pip install mysql-connector-python
import sys
import time
import random
import re
import ntpath
import loguru
import configparser
import json

from datetime import datetime
from lxml import etree

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

import sqlalchemy
import sqlalchemy.ext.automap
import sqlalchemy.orm
import sqlalchemy.schema

from captcha_solver import CaptchaSolver

def main():
    global pageLinks
    #登入
    login()
    hasNext = search(keyword) 
    while hasNext == True:
        #取得列表資訊
        hasNext = fetch_list()

    #排序連結
    pageLinks = sorted(pageLinks, key=lambda k: k['link']) 
    #去除重複的連結
    pageLinks = [dict(t) for t in {tuple(d.items()) for d in pageLinks}]  
    #print(pageLinks)

    #分批查詢寫入
    totalCount = len(pageLinks)
    start = 0
    step = 10
    end = step
    while end < totalCount:
        end = start + step
        if end > totalCount:
            end = totalCount
        #取得內頁
        articles = fetch_detail(pageLinks[start:end])
        #寫入資料庫
        create_db_scrapy(articles)
        start = end

    session.close()
    loguru.logger.info('爬蟲結束')
    sys.exit('爬蟲結束')

#登入
def login():
    #進入 iCook 登入頁面
    driver.get(config['icook']['Login'])
    login_email = driver.find_element_by_name('current-email')
    login_pass = driver.find_element_by_name('current-password')
    login_button = driver.find_element_by_xpath('//button[contains(@class,"mdc-button")]')

    #填入帳密並送出
    time.sleep(random.randint(1000, 2000)/1000)
    login_email.send_keys(config['icook']['Mail'])
    login_pass.send_keys(config['icook']['Password'])
    time.sleep(random.randint(1000, 2000)/1000)
    login_button.click()
    time.sleep(random.randint(1000, 3000)/1000)

#搜尋(關鍵字，材料)
def search(keyword):
    search_input = driver.find_element_by_name('q')
    search_input.clear()
    search_input.send_keys(keyword)

    time.sleep(random.randint(1000, 2000)/1000)

    search_button = driver.find_element_by_xpath('//button[contains(@class,"btn-search")]')
    search_button.click()
    time.sleep(random.randint(1000, 2000)/1000)

    return True

#取得列表
def fetch_list():
    print('fetch_list()')
    results = driver.find_element_by_xpath('//ul[contains(@class,"result-browse-layout")]').get_attribute('innerHTML')
    if results == None:
        sys.exit('程式中止：無回應指定內容元素')

    dom = etree.HTML(results)
    links = dom.xpath('//li[@class="browse-recipe-item"]/a[@class="browse-recipe-link"]/@href')
    titles = dom.xpath('//li[@class="browse-recipe-item"]//h2[@class="browse-recipe-name"]/@data-title')
    composeItems(links, titles)

    #利用下一頁按鈕，判讀有無下一頁
    try:
        nextPage = driver.find_element_by_xpath('//li[contains(@class,"page--next")]').get_attribute('innerHTML')
        nextPageUrl = etree.HTML(nextPage)
        driver.get(config['icook']['Url'] + nextPageUrl.xpath('//a/@href')[0])
        time.sleep(random.randint(1000, 3000)/1000)
    except NoSuchElementException as e:
        print('無下一頁')
        return False

    return True

#取得內容
def fetch_detail(items):
    articles = []
    for item in items:
        try:
            print('讀取 >>> ' + item['link'])
            driver.get(item['link'])
            results = driver.find_element_by_tag_name('article').get_attribute('innerHTML')
            if results == None:
                print('忽略本頁：無回應指定內容元素')
                return
            dom = etree.HTML(results)
            articles.append(parseDetail(item, dom))
        except:
            print('內容頁面錯誤。')

        time.sleep(random.randint(1000, 3000)/1000)
    
    return articles


#組合列表中的標題
def composeItems(links, titles):
    global pageLinks
    for idx, link in enumerate(links):
        print(link)
        print(titles[idx])
        pageLinks.append({"title":titles[idx], "link":config['icook']['Url'] + link})

#解析內容頁
def parseDetail(pageLink, dom):
    global articles

    #作者
    author = 'None'
    authorLink = ''
    try:
        author = dom.xpath('//div[@class="author-name"]/a/text()')[0]
        authorLink = dom.xpath('//div[@class="author-name"]/a/@href')[0]
    except:
        print('找不到：作者')

    #發文日期：以 int(10) 格式儲存
    postDate = 0
    try:
        postDate = dom.xpath('//time[@class="recipe-detail-meta-item"][1]/@datetime')[0]
        postDate = int(datetime.strptime(postDate, '%Y-%m-%d').timestamp())
        print(postDate)
    except:
        print('無法解析：發文日期')

    #簡述
    description = ''
    try:
        description = dom.xpath('//div[@class="description"]')[0]
        description = etree.tostring(description, encoding='unicode', pretty_print=True)
    except:
        print('找不到：簡述')

    #封面網址
    cover = ''
    filename = ''
    try:
        cover = dom.xpath('//div[@class="recipe-cover"]/a/@href')[0]
        filename = path_leaf(cover)
    except:
        print('找不到：封面網址')

    #份量
    servings = ''
    try:
        servings = dom.xpath('//div[@class="info-content"]/div[@class="servings"]/span[@class="num"]/text()')[0]
    except:
        print('找不到：份量')

    #花費時間
    timeInfo = ''
    try:
        timeInfo = dom.xpath('//div[@class="time-info info-block"]/div[@class="info-content"]/span[@class="num"]/text()')[0]
    except:
        print('找不到：花費時間')

    #食材
    ingredients = ''
    try:
        ingredients = dom.xpath('//div[@class="ingredients-groups"]')[0]
        ingredients = etree.tostring(ingredients, encoding='unicode', pretty_print=True)
        #print(ingredients)
    except:
        print('找不到：食材')

    #步驟
    howto = ''
    try:
        howto = dom.xpath('//div[@class="recipe-details-howto"]')[0]
        howto = etree.tostring(howto, encoding='unicode', pretty_print=True)
        #print(howto)
    except:
        print('找不到：步驟')

    return {
            'title':str(pageLink['title']), 
            'link':str(pageLink['link']), 
            'author':str(author), 
            'author_link':str(authorLink),
            'post_date':str(postDate), 
            'description':str(description), 
            'cover':str(cover), 
            'filename':str(filename),
            'servings':str(servings),
            'time_info':str(timeInfo),
            'ingredients':str(ingredients),
            'howto':str(howto)
            #'images':json.dumps(images, ensure_ascii=False).encode('utf-8').decode('utf-8'), #解決 HTML Entity 編碼問題
        }

#清空字串內全部的 html tag，只留下內文
TAG_RE = re.compile(r'<[^>]+>')
def remove_tags(text):
    return TAG_RE.sub('', text)

#解析檔案路徑及檔名
def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail #or ntpath.basename(head)

#以分包的方法下載檔案
def download_file(url, filename):
    # NOTE the stream=True parameter below
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    #if chunk: 
                    f.write(chunk)

        files.download(filename)
        return filename
    except:
        print("Error")
        return 0

#發現重複的列表項目，若有不再予以新增
def find_duplicate_db_list(item):
    sqlalchemy.Table(__listtable__, metadata, autoload=True)
    Alist = automap.classes[__listtable__]

    aList = session.query(
        Alist
    ).filter(
        Alist.source_id == 1, #item['source_id'],
        Alist.article_title == item['title'],
        Alist.article_url == item['link']
    ).first()

    if aList:
        loguru.logger.info('Find duplicate source article: ' + str(aList.id))
        return aList.id
    else:
        return False

def create_db_list_item(item):
    loguru.logger.info(item['title'])

    itemDuplicateId = find_duplicate_db_list(item)
    if itemDuplicateId != False:
        return itemDuplicateId

    created = int(time.mktime(datetime.now().timetuple()))
    sqlalchemy.Table(__listtable__, metadata, autoload=True)
    Alist = automap.classes[__listtable__]

    alist = Alist()
    alist.source_id = 1
    alist.topic = keyword
    alist.article_title = item['title']
    alist.article_url = item['link']
    alist.created = created
    session.add(alist)
    session.flush()
    return alist.id


def create_db_article(item, listId):
    created = int(time.mktime(datetime.now().timetuple()))
    sqlalchemy.Table(__articletable__, metadata, autoload=True)
    Article = automap.classes[__articletable__]

    sourceContent = {
        'keyword': keyword, 
        'author': item['author'], 
        'author_link': item['author_link'],  
        'description': item['description'],
        'cover': item['cover'],
        'filename': item['filename'],
        'servings': item['servings'],
        'time_info': item['time_info'],
        'ingredients': item['ingredients'],
        'howto': item['howto'],
        'post_date': item['post_date']
    }
    sourceContent = json.dumps(sourceContent, ensure_ascii=False).encode('utf-8').decode('utf-8')
    print(sourceContent)

    article = Article()
    article.list_id = listId
    article.source_url = item['link']
    article.title = item['title']
    article.source_content = sourceContent
    #article.source_media = item['images']
    article.created = created
    session.add(article)
    session.flush()
    return

def create_db_scrapy(articles):
    for item in articles:
        listId = create_db_list_item(item)
        create_db_article(item, listId)
        try:
            session.commit()
            loguru.logger.info('新增資料成功')
        except Exception as e:
            loguru.logger.error('新增資料失敗')
            loguru.logger.error(e)
            session.rollback()
    return

def get_db_articles():
    loguru.logger.info('get_db_articles')
    #TODO:從資料庫合併查詢 list ,article, articlemeta 及 article_media
    sqlalchemy.Table(__listtable__, metadata, autoload=True)
    Listtable = automap.classes[__listtable__]

    sqlalchemy.Table(__articletable__, metadata, autoload=True)
    Articletable = automap.classes[__articletable__]

    articles = session.query(
        Listtable, Articletable
    ).filter(
        Listtable.source_id == 1,
        Listtable.id == Articletable.list_id
    ).with_entities(
        Listtable.id,
        Listtable.topic,
        Listtable.article_url,
        Articletable.title,
        Articletable.source_content
    ).all()

    return articles


if __name__ == '__main__':
    loguru.logger.add(
        f'{datetime.today().strftime("%Y%m%d")}.log',
        rotation='1 day',
        retention='7 days',
        level='DEBUG'
    )

    config = configparser.ConfigParser()
    config.read("config.ini")

    #Selenium with webdriver
    options = Options()
    options.binary_location = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
    webdriver_path = 'C:\\chromedriver_win32\\chromedriver.exe'
    driver = webdriver.Chrome(executable_path=webdriver_path, options=options)

    #資料庫定義
    __articletable__ = 'crawler_article'
    __articlemetatable__ = 'crawler_articlemeta'
    __fieldstable__ = 'crawler_fields'
    __listtable__ = 'crawler_list'
    __mediatable__ = 'crawler_media'

    __wp_posts_table__ = 'wp_posts'
    __wp_postmeta_table__ = 'wp_postmeta'
    __wp_term_relationships_table__ = 'wp_term_relationships'
    __wp_term_taxonomy_table__ = 'wp_term_taxonomy'
    __wp_termmeta_table__ = 'wp_termmeta'
    __wp_terms_table__ = 'wp_terms'

    __post_type__ = 'scrapy'
    __taxonomy_name__ = 'scrapies'

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

    #全域變數
    pageLinks = []

    #關鍵字：「無蛋素食」只有回傳12筆，可測試沒有下一頁
    #關鍵字：「無蛋蛋糕」有38筆 ，可以測試翻頁又不會太長
    keyword = '空姐鍋' 

    main()
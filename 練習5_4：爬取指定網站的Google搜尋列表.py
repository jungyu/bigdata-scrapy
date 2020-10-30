# 練習5_4：爬取指定網站的Google搜尋列表

import time
import random
from datetime import datetime
import configparser

import loguru
import sqlalchemy
import sqlalchemy.ext.automap
import sqlalchemy.orm
import sqlalchemy.schema

import re
import ntpath
import requests
from lxml import etree

#請求網頁
def requestHtml(url):
  s = requests.Session()
  r = s.get(url, headers=headers_Get)
  return etree.HTML(r.text)

#組合列表中的標題
def composeItems(pageLinks, links, titles):
  for idx, link in enumerate(links):
    print(link)
    print(titles[idx])
    pageLinks.append({"title":titles[idx], "link":link})

  return pageLinks

#取得最後一頁
def findLastPage(searchPages):
  lastPage = 1
  for searchPage in searchPages:
    try:
      lastPage = int(searchPage)
      print(lastPage)
    except ValueError:
      print(searchPage + " is not integer")
  return lastPage

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

def fetch_item_link(pageLinks, startItem):
    fullUrl = baseUrl + queryString + startParam + str(startItem) + suffix
    dom = requestHtml(fullUrl)
    links = dom.xpath('//div[@class="yuRUbf"]/a/@href')
    titles = dom.xpath('//div[@class="yuRUbf"]//h3/span/text()')
    #取得最後一頁的數值
    searchPages = dom.xpath('//td/a/text()')
    lastPage = findLastPage(searchPages)

    return composeItems(pageLinks, links, titles)

def crawl_google_list():
    startItem = 0
    #解析回傳的列表標題及連結
    pageLinks = []
    pageLinks = fetch_item_link(pageLinks, startItem)

    #等待數秒(1~5秒間)
    time.sleep(random.randint(1000, 5000)/1000)
    #逐頁爬取文章連結及標題
    ''' TOFIX
    for i in range(2, lastPage):
        #print(i)
        startItem = (i-1)*10
        pageLinks = fetch_item_link(pageLinks, startItem)
        time.sleep(random.randint(1000, 5000)/1000)
    '''
    #去除重複的內容
    print(len(pageLinks))
    pageLinks = [dict(t) for t in {tuple(d.items()) for d in pageLinks}]
    print(len(pageLinks))

    #排序連結
    print(pageLinks)
    sortedPageLinks = sorted(pageLinks, key=lambda k: k['link']) 
    print(sortedPageLinks)
    return sortedPageLinks

def parse_article_element(dom, label, element_xpath, keepSpace):
    try:
        element = dom.xpath(element_xpath)[0]
        #清除空白字元
        if keepSpace is False:
            element = element.replace(' ', '')
        return element
    except:
        print('找不到：'+label)
        return ''
     
def crawl_article(pageLinks):
    #讀取內容頁
    contain = 'article'
    articles = []
    for pageLink in pageLinks:
        try:
            print('讀取 >>> ' + pageLink['link'])
            dom = requestHtml(pageLink['link'])
        except:
            print('頁面錯誤。')

        #標題
        articleTitle = pageLink['title']
        articleTitle = parse_article_element(dom, '標題', '//div[@class="article__head"]//h1/text()', True)

        #作者
        #TOFIX 還有另一個 xpath '//div[@class="author--item"]/a/text()'，要想辦法將2者合一
        author = parse_article_element(dom, '作者', '//div[@class="author--item"]/span/text()', False)
       
        #發文日期
        postDate = parse_article_element(dom, '發文日期', '//time[@class="mt5"]/text()', False)
  
        #前言
        preface =  parse_article_element(dom, '前言', '//div[@class="preface"]/p/text()', True)
  
        #內文
        content =  parse_article_element(dom, '內文', '//div[contains(@class, "article__content")]', True)
        content = etree.tostring(content, encoding='unicode')
        content = remove_tags(content)
        content = content.replace('廣告', '')

        #關鍵字
        keywords = parse_article_element(dom, '關鍵字', '//meta[@name="keywords"]/@content', True)
  
        #相關圖檔
        images = []
        try:
            urls = dom.xpath('//span[contains(@class, "imgzoom")]/@data-zoom')
            for url in urls:
                filename = 'images/' + path_leaf(url)
                images.append({'url':url, 'filename': filename})
                #download_file(url, filename)
            #print(images)
        except:
            print('沒有附圖')

        articles.append({'title':articleTitle, 'link':pageLink['link'], 'keywords':keywords, 'author':author, 'preface':preface, 'content':content, 'images':images, 'post_date':postDate})
        time.sleep(1)
        break #TOFIX
    return articles

def main():
    pageLinks = crawl_google_list()
    articles = crawl_article(pageLinks)
    print(articles)

if __name__ == '__main__':
    loguru.logger.add(
        f'./logs/{datetime.now().strftime("%Y%m%d%m%H%M%S")}.log',
        rotation='1 day',
        retention='7 days',
        level='DEBUG'
    )

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

    #可以從瀏覽器的開發者工具取得 request 的 header 資訊
    headers_Get = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    #爬取指定網站的 Google 列表搜尋
    baseUrl = 'https://www.google.com/search?q='
    #商業智慧+site:www.cw.com.tw
    keyword = "商業智慧"
    site = 'site:www.cw.com.tw'
    queryString = keyword + '+' + site
    startParam = '&start='
    suffix = '&aqs=chrome..69i57j0i333.5056j0j7&sourceid=chrome&ie=UTF-8'

    lastPage = 0

    main()
# -*- coding: utf-8 -*-
"""練習3-4：爬取新聞類型網站(匯出CSV).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1K1_ZzIafTnpTslYBiBRuRedzXKgSQaGm
"""

#安裝相關函式庫
#!pip install requests
#!pip install beautifulsoup4

#匯入必要函式庫
import time
import re
import ntpath
import requests
import csv
from lxml import etree
from google.colab import files

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

#使用 Google 新聞，缺點是可能取到不是內容頁面
baseUrl = 'https://www.google.com/search?q='
#商業智慧+site:www.cw.com.tw
keyword = "商業智慧"
site = 'site:www.cw.com.tw'
queryString = keyword + '+' + site
startItem = 0
startParam = '&start='
suffix = '&aqs=chrome..69i57j0i333.5056j0j7&sourceid=chrome&ie=UTF-8'

#解析回傳的列表標題及連結
pageLinks = []
contain = 'article'

#請求網頁
def requestHtml(url):
  s = requests.Session()
  r = s.get(url, headers=headers_Get)
  return etree.HTML(r.text)

#組合列表中的標題
def composeItems(links, titles):
  for idx, link in enumerate(links):
    print(link)
    print(titles[idx])
    pageLinks.append({"title":titles[idx], "link":link})

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

#爬取第一頁列表中的標題及數值
fullUrl = baseUrl + queryString + startParam + str(startItem) + suffix
dom = requestHtml(fullUrl)
links = dom.xpath('//div[@class="yuRUbf"]/a/@href')
titles = dom.xpath('//div[@class="yuRUbf"]//h3/span/text()')
composeItems(links, titles)

#取得最後一頁的數值
searchPages = dom.xpath('//td/a/text()')
lastPage = findLastPage(searchPages)

#逐頁爬取文章連結及標題
for i in range(2, lastPage):
  #print(i)
  startItem = (i-1)*10
  fullUrl = baseUrl + queryString + startParam + str(startItem) + suffix
  dom = requestHtml(fullUrl)
  links = dom.xpath('//div[@class="yuRUbf"]/a/@href')
  titles = dom.xpath('//div[@class="yuRUbf"]//h3/span/text()')
  composeItems(links, titles)

#去除重複的內容
print(len(pageLinks))
pageLinks = [dict(t) for t in {tuple(d.items()) for d in pageLinks}]
print(len(pageLinks))

#排序連結
print(pageLinks)
newPageLinks = sorted(pageLinks, key=lambda k: k['link']) 
print(newPageLinks)

#讀取內容頁
articles = []
for pageLink in newPageLinks:
  try:
    print('讀取 >>> ' + pageLink['link'])
    dom = requestHtml(pageLink['link'])
  except:
    print('頁面錯誤。')

  #標題
  articleTitle = pageLink['title']
  try:
    articleTitle = dom.xpath('//div[@class="article__head"]//h1/text()')[0]
    #print(articleTitle)
  except:
    print('找不到：標題')

  #作者
  author = 'None'
  try:
    author = dom.xpath('//div[@class="author--item"]/span/text()')[0]
    #print(author)
  except:
    try:
      author = dom.xpath('//div[@class="author--item"]/a/text()')[0]
      author = author.replace(' ', '')
      #print(author)
    except:
      print('找不到：作者')
  
  #發文日期
  postDate = ''
  try:
    postDate = dom.xpath('//time[@class="mt5"]/text()')[0]
    postDate = postDate.replace(' ', '')
    #print(postDate)
  except:
    print('找不到：發文日期')
  
  #前言
  preface = ''
  try:
    preface = dom.xpath('//div[@class="preface"]/p/text()')[0]
    #print(preface)
  except:
    print('找不到：前言')
  
  #內文
  content = ''
  try:
    content = dom.xpath('//div[contains(@class, "article__content")]')[0] #soup.find(class_='article__content').text
  
    content = etree.tostring(content, encoding='unicode')
    content = remove_tags(content)
    content = content.replace('廣告', '')
    #print(content)
  except:
    print('找不到：內文')

  #關鍵字
  keywords = ''
  try:
    keywords = dom.xpath('//meta[@name="keywords"]/@content')[0]
    #print(keywords)
  except:
    print('找不到：關鍵字')
  
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
  #break

#輸出CSV
csv_columns = ['title','link','keywords', 'author', 'preface', 'content', 'images', 'post_date']
csv_file = keyword + ".csv"
try:
    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for article in articles:
            writer.writerow(article)
except IOError:
    print("CSV 檔案寫入發生錯誤")


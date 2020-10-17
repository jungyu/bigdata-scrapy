!pip install requests
!pip install beautifulsoup4

import requests
from bs4 import BeautifulSoup

headers_Get = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

#天下雜誌搜尋結果頁(分類頁是 Lazy-load 模式，不適合一般爬蟲取得分頁)
#https://www.cw.com.tw/search/doSearch.action?key=%E4%BA%BA%E5%B7%A5%E6%99%BA%E6%85%A7&channel=all&sort=desc
#改使用 Google 新聞，缺點是可能取到不是內容頁面
baseUrl = 'https://www.google.com/search?q='
#商業智慧+site:www.cw.com.tw
keyword = "商業智慧"
site = 'site:www.cw.com.tw'
queryString = keyword + '+' + site
startItem = 0
startParam = '&start='
suffix = '&aqs=chrome..69i57j0i333.5056j0j7&sourceid=chrome&ie=UTF-8'

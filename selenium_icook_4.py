#selenium_icook_4.py 解析內頁
import sys
import random
import re
import ntpath
import loguru
import configparser

from datetime import datetime
from time import sleep
from lxml import etree

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from captcha_solver import CaptchaSolver

def main():
    global pageLinks
    #登入
    login()
    #關鍵字：「無蛋素食」只有回傳12筆，可測試沒有下一頁
    hasNext = search('無蛋蛋糕') #有38筆 ，可以測試翻頁又不會太長
    while hasNext == True:
        #取得列表資訊
        hasNext = fetch_list()

    #排序連結
    pageLinks = sorted(pageLinks, key=lambda k: k['link']) 
    #去除重複的連結
    pageLinks = [dict(t) for t in {tuple(d.items()) for d in pageLinks}]  
    print(pageLinks)

    fetch_detail()
    print(articles)
    #insert_update_db()

    sys.exit('爬蟲結束')

#登入
def login():
    #進入 iCook 登入頁面
    driver.get(config['icook']['Login'])
    login_email = driver.find_element_by_name('current-email')
    login_pass = driver.find_element_by_name('current-password')
    login_button = driver.find_element_by_xpath('//button[contains(@class,"mdc-button")]')

    #填入帳密並送出
    sleep(random.randint(1000, 2000)/1000)
    login_email.send_keys(config['icook']['Mail'])
    login_pass.send_keys(config['icook']['Password'])
    sleep(random.randint(1000, 2000)/1000)
    login_button.click()
    sleep(random.randint(1000, 3000)/1000)

#搜尋(關鍵字，材料)
def search(keyword):
    search_input = driver.find_element_by_name('q')
    search_input.clear()
    search_input.send_keys(keyword)

    sleep(random.randint(1000, 2000)/1000)

    search_button = driver.find_element_by_xpath('//button[contains(@class,"btn-search")]')
    search_button.click()
    sleep(random.randint(1000, 2000)/1000)

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
        sleep(random.randint(1000, 3000)/1000)
    except NoSuchElementException as e:
        print('無下一頁')
        return False

    return True

#取得內容
def fetch_detail():
    for pageLink in pageLinks:
        try:
            print('讀取 >>> ' + pageLink['link'])
            driver.get(config['icook']['Url'] + pageLink['link'])
            results = driver.find_element_by_tag_name('article').get_attribute('innerHTML')
            if results == None:
                print('忽略本頁：無回應指定內容元素')
                return
            dom = etree.HTML(results)
            parseDetail(pageLink, dom)
        except:
            print('內容頁面錯誤。')

        sleep(random.randint(1000, 3000)/1000)


#組合列表中的標題
def composeItems(links, titles):
    global pageLinks
    for idx, link in enumerate(links):
        print(link)
        print(titles[idx])
        pageLinks.append({"title":titles[idx], "link":link})

#清空字串內全部的 html tag，只留下內文
TAG_RE = re.compile(r'<[^>]+>')
def remove_tags(text):
    return TAG_RE.sub('', text)

#解析檔案路徑及檔名
def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail #or ntpath.basename(head)

#解析內容頁
def parseDetail(pageLink, dom):
    global articles

    #作者
    author = 'None'
    authoLink = ''
    try:
        author = dom.xpath('//div[@class="author-name"]/a/text()')[0]
        authoLink = dom.xpath('//div[@class="author-name"]/a/@href')[0]
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

    articles.append({
            'title':str(pageLink['title']), 
            'link':str(pageLink['link']), 
            'author':str(author), 
            'autho_link':str(authoLink),
            'post_date':str(postDate), 
            'description':str(description), 
            'cover':str(cover), 
            'filename':str(filename),
            'servings':str(servings),
            'time_info':str(timeInfo),
            'ingredients':str(ingredients),
            'howto':str(howto)
            #'images':json.dumps(images, ensure_ascii=False).encode('utf-8').decode('utf-8'), #解決 HTML Entity 編碼問題
        })

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

    #全域變數
    pageLinks = []
    articles = []

    main()
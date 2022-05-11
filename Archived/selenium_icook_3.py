#selenium_icook_3.py 取得列表
import sys
import re
import ntpath
import datetime
import loguru
import configparser

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

    login()
    hasNext = search('無蛋蛋糕')  #關鍵字：「無蛋素食」只有回傳12筆，可測試沒有下一頁
    print(hasNext)
    while hasNext == True:
        hasNext = fetch_list()
        
    #排序連結
    pageLinks = sorted(pageLinks, key=lambda k: k['link']) 
    #去除重複的連結
    print(len(pageLinks))
    pageLinks = [dict(t) for t in {tuple(d.items()) for d in pageLinks}]
    print(len(pageLinks))
    
    print(pageLinks)
    #fetch_detail()
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
    sleep(2)
    login_email.send_keys(config['icook']['Mail'])
    login_pass.send_keys(config['icook']['Password'])
    sleep(2)
    login_button.click()
    sleep(3)

#搜尋(關鍵字，材料)
def search(keyword):
    search_input = driver.find_element_by_name('q')
    search_input.clear()
    search_input.send_keys(keyword)

    sleep(2)

    search_button = driver.find_element_by_xpath('//button[contains(@class,"btn-search")]')
    search_button.click()
    sleep(2)

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
        sleep(3)
    except NoSuchElementException as e:
        print('無下一頁')
        return False

    return True

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



if __name__ == '__main__':
    loguru.logger.add(
        f'{datetime.date.today():%Y%m%d}.log',
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

    main()

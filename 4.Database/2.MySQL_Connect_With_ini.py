#MySQL 連線原型 + 環境檔 ini
import configparser
import pymysql

config = configparser.ConfigParser()
config.read("config.ini")

host = config['mysql']['Host']
port = int(config['mysql']['Port'])
user = config['mysql']['User']
passwd = config['mysql']['Password']
db = config['mysql']['Database']
charset = config['mysql']['Charset']

#資料庫連線設定
#可縮寫db = pymysql.connect("localhost","root","root","30days" )
db = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
#建立操作游標
cursor = db.cursor()

#查詢 crawler_source
sourceSQL = str("SELECT * FROM crawler_source;")

#執行語法
try:
    cursor.execute(sourceSQL)
    sources = cursor.fetchall()
    for source in sources:
        print(source)

finally:
    cursor.close()
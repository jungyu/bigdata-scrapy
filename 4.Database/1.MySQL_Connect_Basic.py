#MySQL 連線原型範例
import pymysql

#資料庫連線設定
#可縮寫db = pymysql.connect("localhost","root","root","30days" )
db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd= '密碼', db='wordpress', charset='utf8')
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
# SQLAlchemy ORM 
# 安裝指令： python -m pip install sqlalchemy
import datetime
import configparser

import loguru
import sqlalchemy
import sqlalchemy.ext.automap
import sqlalchemy.orm
import sqlalchemy.schema

def main():
    config = configparser.ConfigParser()
    config.read("config.ini")

    host = config['mysql']['Host']
    port = int(config['mysql']['Port'])
    username = config['mysql']['User']
    password = config['mysql']['Password']
    database = config['mysql']['Database']

    # 建立連線引擎
    engine = sqlalchemy.create_engine(
        f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}'
    )
    # 取得資料庫元資料
    metadata = sqlalchemy.schema.MetaData(engine)
    # 產生自動對應參照
    automap = sqlalchemy.ext.automap.automap_base()
    automap.prepare(engine, reflect=True)
    # 準備 ORM 連線
    session = sqlalchemy.orm.Session(engine)

    # 載入 crawler_source 資料表資訊
    sqlalchemy.Table('crawler_source', metadata, autoload=True)
    # 取出對應 crawler_source 資料表的類別
    Source = automap.classes['crawler_source']

    try:
        loguru.logger.info('取出資料表所有資料')
        results = session.query(Source).all()
        for source in results:
            loguru.logger.info(f'{source.name} {source.source_domain}')
    except Exception as e:
        # 發生例外錯誤，還原交易
        session.rollback()
        loguru.logger.error('查詢資料失敗')
        loguru.logger.error(e)
    finally:
        session.close()

if __name__ == '__main__':
    loguru.logger.add(
        f'{datetime.date.today():%Y%m%d}.log',
        rotation='1 day',
        retention='7 days',
        level='DEBUG'
    )
    main()
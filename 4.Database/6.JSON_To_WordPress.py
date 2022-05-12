# 6.讀入 JSON 檔案寫到資料庫
import time
import json
import urllib
import configparser
from datetime import datetime

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

__filename__ = r'Shopee_NaNa.json'

def main():
    data = parse_JSON()
    to_wordpress(data)

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

    main()
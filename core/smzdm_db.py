# coding:utf-8
import time
import traceback
from functools import wraps

from lib import db
from smzdm_logger import *

log_db = logging.getLogger('[db]')
log_db.setLevel(logging.INFO)


def with_connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with db.connection():
            result = func(*args, **kwargs)
            return result

    return wrapper


# 对于数据库里面的int一定要在插入数据库之前验证，否则int()函数可能会因此出错

def import_db(flag, to_import_list):
    try:
        if flag == 'youhui' or flag == 'haitao':
            for each in to_import_list:
                if db.select_one(r'select * from smzdm_item where article_id=?', each['article_id']):
                    # 每次获取都要更新
                    db.update(
                            r'update smzdm_item set article_comment=?, article_collection=?,article_worthy=?,article_unworthy=? ,worthy_percentage=? where article_id=?',
                            each['article_comment'], each['article_collection'], each['article_worthy'],
                            each['article_unworthy'], each['worthy_percentage'], each['article_id'])
                else:
                    db.insert('smzdm_item', **each)

        elif flag == 'faxian':
            for each in to_import_list:
                if db.select_one(r'select * from smzdm_item where article_id=?', each['article_id']):
                    db.update(
                            r'update smzdm_item set article_comment=?, article_collection=? where article_id=?',
                            each['article_comment'], each['article_collection'], each['article_id'])
                else:
                    db.insert('smzdm_item', **each)
        log_db.info("import_db ok. ")
    except Exception as e:
        log_db.warning("ErrInfo: " + str(e))


def import_push_his(pushed_item_list, case_id, count, user_email):
    with db.with_connection():
        for each_pushed_item in pushed_item_list:
            temp = {'article_id': each_pushed_item['article_id'], 'timesort': each_pushed_item['timesort'],
                    'case_id': case_id, 'user_email': user_email, 'inserted_timesort': int(time.time())}
        try:
            db.insert(r'smzdm_his', **temp)
            db.update(r'update smzdm_case_info set count=? where case_id=?', count + 1, case_id)
            log_db.info("import smzdm_his" + '|Push id:' + str(case_id))
        except Exception as e:
            # 这个错误已经不能忍，要退出；否则，不能更新smzdm_his表的话，会一直在推送
            traceback.print_exc()
            log_db.error("ErrInfo:" + str(e))
            exit()

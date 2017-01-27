# coding:utf-8
import time
import traceback
from functools import wraps

from lib import db
from smzdm_logger import UsualLogging
import threading

SMZDMDBLogger = UsualLogging('SMZDMDB')


def with_connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with db.connection():
            result = func(*args, **kwargs)
            return result

    return wrapper


# 对于数据库里面的int一定要在插入数据库之前验证，否则int()函数可能会因此出错

def import_db(item_dict):
    try:
        with db.connection():
            for name, item in item_dict.items():
                if name == 'youhui' or name == 'haitao':
                    for each in item:
                        if db.select_one(r'select * from smzdm_item where article_id=?', each['article_id']):
                            # 每次获取都要更新
                            db.update(
                                r'update smzdm_item set article_comment=?, article_collection=?,article_worthy=?,article_unworthy=? ,worthy_percentage=? where article_id=?',
                                each['article_comment'], each['article_collection'], each['article_worthy'],
                                each['article_unworthy'], each['worthy_percentage'], each['article_id'])
                        else:
                            db.insert('smzdm_item', **each)

                elif name == 'faxian':
                    for each in item:
                        if db.select_one(r'select * from smzdm_item where article_id=?', each['article_id']):
                            db.update(
                                r'update smzdm_item set article_comment=?, article_collection=? where article_id=?',
                                each['article_comment'], each['article_collection'], each['article_id'])
                        else:
                            db.insert('smzdm_item', **each)
        SMZDMDBLogger.info("Import db ok. ")
    except Exception as e:
        traceback.print_exc()
        SMZDMDBLogger.warning("ErrInfo: " + str(e))


def import_push_his(pushed_item_list, each_case):
    case_id = each_case[u'case_id']
    count = each_case[u'count']
    user_email = each_case[u'e_mail']

    with db.connection():
        for each_pushed_item in pushed_item_list:
            temp = {'article_id': each_pushed_item['article_id'],
                    'case_id': case_id, 'user_email': user_email, 'inserted_timesort': int(time.time())}
            try:
                count += 1
                db.insert(r'smzdm_his', **temp)
                db.update(r'update smzdm_case_info set count=? where case_id=?', count, case_id)
                SMZDMDBLogger.info("Import pushed item push_id:{} articlel_id:{}".format(case_id,each_pushed_item['article_id']))
            except Exception as e:
                # 这个错误已经不能忍，要退出；否则，不能更新smzdm_his表的话，会一直在推送
                traceback.print_exc()
                SMZDMDBLogger.error("ErrInfo:" + str(e))
                exit()


class SMZDMDBPush(threading.Thread):
    def __init__(self, in_q=None, out_q=None):
        """

        :param in_q:        tuple    ([发送成功的item],case)
        """
        super(SMZDMDBPush, self).__init__()
        self.in_q = in_q
        self.out_q = out_q

    def run(self):
        while True:
            sent_item_list, each_case = self.in_q.get()
            import_push_his(sent_item_list, each_case)


class SMZDMDBImport(threading.Thread):
    def __init__(self, in_q=None, out_q=None):
        """
        :param in_q:        json    爬取回来的数据

        """
        super(SMZDMDBImport, self).__init__()
        self.in_q = in_q
        self.out_q = out_q

    def run(self):
        while True:
            item_dict = self.in_q.get()
            import_db(item_dict)
            self.out_q.put(item_dict)

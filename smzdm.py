#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import *
from lib import db

if __name__ == "__main__":
    db.create_engine(db_username, db_password, db_name)

    from Queue import Queue
    from core.smzdm_search import SMZDMSearch
    from core.smzdm_db import SMZDMDBImport, SMZDMDBPush
    from core.smzdm_spider import SMZDMSpider
    from core.smzdm_email import SMZDMEmail

    smzdm_spider_out_q = Queue()
    smzdm_db_import_out_q = Queue()
    smzdm_search_out_q = Queue()
    smzdm_email_out_q = Queue()
    smzdm_email_list = []

    smzdm_spider = SMZDMSpider(smzdm_spider_out_q)
    smzdm_db_import = SMZDMDBImport(smzdm_spider_out_q, smzdm_db_import_out_q)
    smzdm_search = SMZDMSearch(smzdm_db_import_out_q, smzdm_search_out_q)
    for i in range(4):
        smzdm_email_list.append(SMZDMEmail(smzdm_search_out_q, smzdm_email_out_q))
    smzdm_db_push = SMZDMDBPush(smzdm_email_out_q)

    smzdm_spider.start()
    smzdm_db_import.start()
    smzdm_search.start()
    for i in smzdm_email_list:
        i.start()
    smzdm_db_push.start()

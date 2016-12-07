#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

from config import *
from core.smzdm_case import *
from core.smzdm_db import import_db, import_push_his
from core.smzdm_email import send_email
from core.smzdm_filter import *
from core.smzdm_scrapy import SMZDMScrapy
from lib.my_request import *

# to debug
test_list = []
t2 = 0.0
t1 = 0.0

cases = [TitleCase(), CommentCase(), CatesstrCase(), ArticleMallCase(), RmbPriceSmallCase(),
         RmbPriceBigCase(), ArticleWorthyCase(), ArticleUnworthyCase(), WorthyPrecentageCase(),
         ArticleCollectionCase(), ArticlePriceCase()]

filters = [TitleFilter(), CommentFilter(), CatesstrFilter(), ArticlemallFilter(), RMBPriceSmallFilter(),
           RMBPriceBigFilter(), ArticleWorthyFilter(), ArticleUnworthyFilter(), WorthyPrecentageFilter(),
           ArticleCollectionFilter(), ArticlePriceFilter()]


def filter_send_import(case_list, target, item_dict):
    # TODO
    # 有一个小bug，当该send_mail或者import_his失败的时候，会再send一次
    # 举个例子，一个优惠海涛发现都有的case，再优惠阶段没有import_his的话，海涛阶段会继续send
    name = [('youhui', 1), ('haitao', 2), ('faxian', 3)]
    all_task = []

    # do case
    for each_case in case_list:
        push_item_list = []
        for k, v in name:
            if target == k:
                if each_case[u'fromwhere'] != v and each_case[u'fromwhere'] != 0:
                    break
            for case in cases:
                if case.test(each_case):
                    case.act(item_dict[k], each_case, push_item_list)

        case_id = int(each_case[u'case_id'])

        # do filter
        if push_item_list:
            filter_list = db.select(r'select * from smzdm_filter where filter_id=?', case_id)
            if filter_list:
                for each_filter in filter_list:
                    for the_filter in filters:
                        if the_filter.test(each_filter):
                            the_filter.act(push_item_list, each_filter, push_item_list)

        if push_item_list:
            all_task.append((push_item_list, each_case))

    # do send
    if all_task:
        return_queue = send_email(all_task)
        # do import
        while return_queue.qsize() > 0:
            case_info, each_pushed_item, is_send = return_queue.get()

            if is_send is False:

                for i, j in all_task:
                    if case_info[u'case_id'] == j[u'case_id']:
                        for index, each_item in enumerate(i):
                            if each_pushed_item[u'article_id'] == each_item[u'article_id']:
                                i.pop(index)

        for push_item_list, each_info in all_task:
            import_push_his(push_item_list, case_info[u'case_id'], case_info[u'count'], case_info[u'e_mail'])


def smzdm_start(the_spider):
    db.create_engine(db_username, db_password, db_name)
    case_list = db.select(r'select * from smzdm_case_info')
    item_dict = {}

    for name, url in [('faxian', r'http://faxian.smzdm.com/json_more?timesort='),
                      ('haitao', r'http://haitao.smzdm.com/json_more?timesort='),
                      ('youhui', r'http://www.smzdm.com/youhui/json_more?timesort=')]:
        the_spider.url = url
        the_spider.flag = name
        item_dict[name] = the_spider.parse_item()

    with db.connection():
        import_db('youhui', item_dict['youhui'])
        import_db('faxian', item_dict['faxian'])
        import_db('haitao', item_dict['haitao'])

    for each in ['youhui', 'faxian', 'haitao']:
        filter_send_import(case_list, each, item_dict)


if __name__ == "__main__":
    while True:
        smzdm = SMZDMScrapy()
        smzdm_start(smzdm)
        hours = int(time.strftime("%H"))

        while hours >= stop and hours <= stop + 8:
            time.sleep(long_sleep_time)
            hours = int(time.strftime("%H"))

        time.sleep(random.randint(sleep_time[0], sleep_time[1]) - (t2 - t1))

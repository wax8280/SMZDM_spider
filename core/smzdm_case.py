#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from lib import db
from smzdm_logger import *
log_cases = logging.getLogger('[cases]')
log_cases.setLevel(logging.INFO)

class CaseOperate(object):
    @staticmethod
    def search_keyword(push_item_list, keyword_list, item_list, target):
        keyword_len = len(keyword_list)
        # 关键词搜索，并将结果item放入列表中
        for each_item in item_list:
            try:
                # 搜索每一个keyword
                for index, each_keyword in enumerate(keyword_list):
                    if not re.search(each_keyword, each_item[target], re.IGNORECASE):
                        break

                    if index == keyword_len - 1:
                        push_item_list.append(each_item)
            except Exception, e:
                log_cases.warning("ErrInfo:" + str(e))

    @staticmethod
    def search_keynum(push_item_list, keynum_num, item_list, target, rev=False):
        try:
            for each_item in item_list:
                if rev:
                    if each_item[target] < keynum_num:
                        push_item_list.append(each_item)
                else:
                    if each_item[target] > keynum_num:
                        push_item_list.append(each_item)
        except Exception, e:
            log_cases.warning("ErrInfo:" + str(e))

    @staticmethod
    def push_filter(push_item_list, case_id, user_email):
        delete_list = []
        try:
            push_his_list = db.select(r'select * from smzdm_his where case_id=?', case_id)
            # 过滤已经在push_his，即已经推送过的物品
            for each_push_item in push_item_list:
                for each_push_his in push_his_list:
                    if int(each_push_item['article_id']) == int(each_push_his[u'article_id']) and abs(
                                    each_push_item['timesort'] - each_push_his[u'timesort']) < 1000:
                        delete_list.append(each_push_item)
                        break

            for each in delete_list:
                push_item_list.remove(each)
        except Exception, e:
            log_smzdm_scrapy.warning("ErrInfo:" + str(e))


class BaseCase(object):
    def test(self, each_push, type_num):
        return True if each_push[u'type'] == type_num else False

    def act(self, item_list, each_push, push_item_list, type_key, rev=False):
        case_id = each_push[u'case_id']
        user_email = each_push[u'e_mail']
        if type_key in ['article_title', 'cates_str', 'article_mall', 'article_price']:
            keyword_list = each_push[u'keyword'].split()
            # 搜索完所有物品
            CaseOperate.search_keyword(push_item_list, keyword_list, item_list, type_key)
        elif type_key in ['article_comment', 'rmb_price', 'article_worthy', 'article_unworthy', 'worthy_percentage',
                          'article_collection']:
            comment_num = int(each_push[u'keyword'])
            CaseOperate.search_keynum(push_item_list, comment_num, item_list, type_key, rev)
        # 如果物品符合要求，查询物品是否已经推送过
        if push_item_list:
            CaseOperate.push_filter(push_item_list, case_id, user_email)


class TitleCase(BaseCase):
    TYPE_NUM = 1
    TYPE_KEY = 'article_title'

    def test(self, each_push, type_num=TYPE_NUM):
        return super(TitleCase, self).test(each_push, type_num)

    def act(self, item_list, each_push, push_item_list, type_key=TYPE_KEY, rev=False):
        super(TitleCase, self).act(item_list, each_push, push_item_list, type_key)


class CommentCase(BaseCase):
    TYPE_NUM = 2
    TYPE_KEY = 'article_comment'

    def test(self, each_push, type_num=TYPE_NUM):
        return super(CommentCase, self).test(each_push, type_num)

    def act(self, item_list, each_push, push_item_list, type_key=TYPE_KEY, rev=False):
        super(CommentCase, self).act(item_list, each_push, push_item_list, type_key)


class CatesstrCase(BaseCase):
    TYPE_NUM = 3
    TYPE_KEY = 'cates_str'

    def test(self, each_push, type_num=TYPE_NUM):
        return super(CatesstrCase, self).test(each_push, type_num)

    def act(self, item_list, each_push, push_item_list, type_key=TYPE_KEY, rev=False):
        super(CatesstrCase, self).act(item_list, each_push, push_item_list, type_key)


class ArticleMallCase(BaseCase):
    TYPE_NUM = 4
    TYPE_KEY = 'article_mall'

    def test(self, each_push, type_num=TYPE_NUM):
        return super(ArticleMallCase, self).test(each_push, type_num)

    def act(self, item_list, each_push, push_item_list, type_key=TYPE_KEY, rev=False):
        super(ArticleMallCase, self).act(item_list, each_push, push_item_list, type_key)


class RmbPriceSmallCase(BaseCase):
    TYPE_NUM = 5
    TYPE_KEY = 'rmb_price'

    def test(self, each_push, type_num=TYPE_NUM):
        return super(RmbPriceSmallCase, self).test(each_push, type_num)

    def act(self, item_list, each_push, push_item_list, type_key=TYPE_KEY, rev=True):
        super(RmbPriceSmallCase, self).act(item_list, each_push, push_item_list, type_key, rev=rev)


class RmbPriceBigCase(BaseCase):
    TYPE_NUM = 6
    TYPE_KEY = 'rmb_price'

    def test(self, each_push, type_num=TYPE_NUM):
        return super(RmbPriceBigCase, self).test(each_push, type_num)

    def act(self, item_list, each_push, push_item_list, type_key=TYPE_KEY, rev=False):
        super(RmbPriceBigCase, self).act(item_list, each_push, push_item_list, type_key, rev=rev)


class ArticleWorthyCase(BaseCase):
    TYPE_NUM = 7
    TYPE_KEY = 'article_worthy'

    def test(self, each_push, type_num=TYPE_NUM):
        return super(ArticleWorthyCase, self).test(each_push, type_num)

    def act(self, item_list, each_push, push_item_list, type_key=TYPE_KEY, rev=False):
        super(ArticleWorthyCase, self).act(item_list, each_push, push_item_list, type_key, rev=rev)


class ArticleUnworthyCase(BaseCase):
    TYPE_NUM = 8
    TYPE_KEY = 'article_unworthy'

    def test(self, each_push, type_num=TYPE_NUM):
        return super(ArticleUnworthyCase, self).test(each_push, type_num)

    def act(self, item_list, each_push, push_item_list, type_key=TYPE_KEY, rev=True):
        super(ArticleUnworthyCase, self).act(item_list, each_push, push_item_list, type_key, rev=rev)


class WorthyPrecentageCase(BaseCase):
    TYPE_NUM = 9
    TYPE_KEY = 'worthy_percentage'

    def test(self, each_push, type_num=TYPE_NUM):
        return super(WorthyPrecentageCase, self).test(each_push, type_num)

    def act(self, item_list, each_push, push_item_list, type_key=TYPE_KEY, rev=False):
        super(WorthyPrecentageCase, self).act(item_list, each_push, push_item_list, type_key, rev=rev)


class ArticleCollectionCase(BaseCase):
    TYPE_NUM = 10
    TYPE_KEY = 'article_collection'

    def test(self, each_push, type_num=TYPE_NUM):
        return super(ArticleCollectionCase, self).test(each_push, type_num)

    def act(self, item_list, each_push, push_item_list, type_key=TYPE_KEY, rev=False):
        super(ArticleCollectionCase, self).act(item_list, each_push, push_item_list, type_key, rev=rev)


class ArticlePriceCase(BaseCase):
    TYPE_NUM = 11
    TYPE_KEY = 'article_price'

    def test(self, each_push, type_num=TYPE_NUM):
        return super(ArticlePriceCase, self).test(each_push, type_num)

    def act(self, item_list, each_push, push_item_list, type_key=TYPE_KEY, rev=False):
        super(ArticlePriceCase, self).act(item_list, each_push, push_item_list, type_key, rev=rev)

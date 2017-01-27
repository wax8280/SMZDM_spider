#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from smzdm_logger import UsualLogging

SMZDMFilterLogger = UsualLogging('SMZDMFilter')


class FilterOperate(object):
    @staticmethod
    def search_keynum(push_item_list, keynum_num, target, rev=False):
        try:
            delete_list = []
            for each_item in push_item_list:
                if rev:
                    if not each_item[target] < keynum_num:
                        delete_list.append(each_item)
                else:
                    if not each_item[target] > keynum_num:
                        delete_list.append(each_item)

            for each_del in delete_list:
                push_item_list.remove(each_del)

            del delete_list
        except Exception, e:
            SMZDMFilterLogger.warning("ErrInfo:" + str(e))

    @staticmethod
    def search_keyword(push_item_list, keyword_list, target):
        keyword_len = len(keyword_list)
        # 关键词搜索，并将结果item放入列表中
        delete_list = []
        try:
            for each_item in push_item_list:

                for index, each_keyword in enumerate(keyword_list):
                    if re.search(each_keyword, each_item[target], re.IGNORECASE):
                        break

                    if index == keyword_len - 1:
                        delete_list.append(each_item)

            for each_del in delete_list:
                push_item_list.remove(each_del)

        except Exception, e:
            SMZDMFilterLogger.warning("ErrInfo:" + str(e))


class FilterBase(object):
    def test(self, each_push, type_num):
        return True if each_push[u'type'] == type_num else False

    def act(self, item_list, each_filter, type_key, rev=False):
        if type_key in ['article_title', 'cates_str', 'article_mall', 'article_price']:
            keyword_list = each_filter[u'keyword'].split()
            FilterOperate.search_keyword(item_list, keyword_list, type_key)

        elif type_key in ['article_comment', 'rmb_price', 'article_worthy', 'article_unworthy', 'worthy_percentage',
                          'article_collection']:
            num = int(each_filter[u'keyword'])
            FilterOperate.search_keynum(item_list, num, type_key, rev)


class TitleFilter(FilterBase):
    TYPE_NUM = 1
    TYPE_KEY = 'article_title'

    def test(self, each_push, type_num=TYPE_NUM):
        return super(TitleFilter, self).test(each_push, type_num)

    def act(self, item_list, each_filter, type_key=TYPE_KEY, rev=False):
        super(TitleFilter, self).act(item_list, each_filter, type_key)


class CommentFilter(FilterBase):
    TYPE_NUM = 2
    TYPE_KEY = 'article_comment'

    def test(self, each_push, type_num=TYPE_NUM):
        return super(CommentFilter, self).test(each_push, type_num)

    def act(self, item_list, each_filter, type_key=TYPE_KEY, rev=False):
        super(CommentFilter, self).act(item_list, each_filter, type_key)


class CatesstrFilter(FilterBase):
    TYPE_NUM = 3
    TYPE_KEY = 'cates_str'

    def test(self, each_push, type_num=TYPE_NUM):
        return super(CatesstrFilter, self).test(each_push, type_num)

    def act(self, item_list, each_filter, type_key=TYPE_KEY, rev=False):
        super(CatesstrFilter, self).act(item_list, each_filter, type_key)


class ArticlemallFilter(FilterBase):
    TYPE_NUM = 4
    TYPE_KEY = 'article_mall'

    def test(self, each_push, type_num=TYPE_NUM):
        return super(ArticlemallFilter, self).test(each_push, type_num)

    def act(self, item_list, each_filter, type_key=TYPE_KEY, rev=False):
        super(ArticlemallFilter, self).act(item_list, each_filter, type_key)


class RMBPriceSmallFilter(FilterBase):
    # 过滤小的
    TYPE_NUM = 5
    TYPE_KEY = 'rmb_price'

    def test(self, each_push, type_num=TYPE_NUM):
        return super(RMBPriceSmallFilter, self).test(each_push, type_num)

    def act(self, item_list, each_filter, type_key=TYPE_KEY, rev=True):
        super(RMBPriceSmallFilter, self).act(item_list, each_filter, type_key)


class RMBPriceBigFilter(FilterBase):
    TYPE_NUM = 6
    TYPE_KEY = 'rmb_price'

    def test(self, each_push, type_num=TYPE_NUM):
        return super(RMBPriceBigFilter, self).test(each_push, type_num)

    def act(self, item_list, each_filter, type_key=TYPE_KEY, rev=False):
        super(RMBPriceBigFilter, self).act(item_list, each_filter, type_key)


class ArticleWorthyFilter(FilterBase):
    TYPE_NUM = 7
    TYPE_KEY = 'article_worthy'

    def test(self, each_push, type_num=TYPE_NUM):
        return super(ArticleWorthyFilter, self).test(each_push, type_num)

    def act(self, item_list, each_filter, type_key=TYPE_KEY, rev=False):
        super(ArticleWorthyFilter, self).act(item_list, each_filter, type_key)


class ArticleUnworthyFilter(FilterBase):
    TYPE_NUM = 8
    TYPE_KEY = 'article_unworthy'

    def test(self, each_push, type_num=TYPE_NUM):
        return super(ArticleUnworthyFilter, self).test(each_push, type_num)

    def act(self, item_list, each_filter, type_key=TYPE_KEY, rev=True):
        super(ArticleUnworthyFilter, self).act(item_list, each_filter, type_key)


class WorthyPrecentageFilter(FilterBase):
    TYPE_NUM = 9
    TYPE_KEY = 'worthy_percentage'

    def test(self, each_push, type_num=TYPE_NUM):
        return super(WorthyPrecentageFilter, self).test(each_push, type_num)

    def act(self, item_list, each_filter, type_key=TYPE_KEY, rev=False):
        super(WorthyPrecentageFilter, self).act(item_list, each_filter, type_key)


class ArticleCollectionFilter(FilterBase):
    TYPE_NUM = 10
    TYPE_KEY = 'article_collection'

    def test(self, each_push, type_num=TYPE_NUM):
        return super(ArticleCollectionFilter, self).test(each_push, type_num)

    def act(self, item_list, each_filter, type_key=TYPE_KEY, rev=False):
        super(ArticleCollectionFilter, self).act(item_list, each_filter, type_key)


class ArticlePriceFilter(FilterBase):
    TYPE_NUM = 11
    TYPE_KEY = 'article_price'

    def test(self, each_push, type_num=TYPE_NUM):
        return super(ArticlePriceFilter, self).test(each_push, type_num)

    def act(self, item_list, each_filter, type_key=TYPE_KEY, rev=False):
        super(ArticlePriceFilter, self).act(item_list, each_filter, type_key)

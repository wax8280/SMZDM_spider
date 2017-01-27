# !/usr/bin/env python
# coding: utf-8
import threading
from lib import db
from smzdm_case import TitleCase, CommentCase, CatesstrCase, ArticleMallCase, RmbPriceSmallCase, RmbPriceBigCase, \
    ArticleWorthyCase, ArticleUnworthyCase, WorthyPrecentageCase, ArticleCollectionCase, ArticlePriceCase
from smzdm_filter import TitleFilter, CommentFilter, CatesstrFilter, ArticlemallFilter, RMBPriceSmallFilter, \
    RMBPriceBigFilter, ArticleWorthyFilter, ArticleUnworthyFilter, WorthyPrecentageFilter, ArticleCollectionFilter, \
    ArticlePriceFilter
from smzdm_logger import UsualLogging
import threading

SMZDMSearchLogger = UsualLogging('SMZDMSearch')


class SMZDMSearch(threading.Thread):
    cases = [TitleCase(), CommentCase(), CatesstrCase(), ArticleMallCase(), RmbPriceSmallCase(),
             RmbPriceBigCase(), ArticleWorthyCase(), ArticleUnworthyCase(), WorthyPrecentageCase(),
             ArticleCollectionCase(), ArticlePriceCase()]

    filters = [TitleFilter(), CommentFilter(), CatesstrFilter(), ArticlemallFilter(), RMBPriceSmallFilter(),
               RMBPriceBigFilter(), ArticleWorthyFilter(), ArticleUnworthyFilter(), WorthyPrecentageFilter(),
               ArticleCollectionFilter(), ArticlePriceFilter()]

    name = [('youhui', 1), ('haitao', 2), ('faxian', 3)]

    def __init__(self, in_q, out_q):
        """

        :param in_q:        json    爬取回来的数据
        :param out_q:       tuple   ([符合case的json数据],case)
        """
        super(SMZDMSearch, self).__init__()
        self.in_q = in_q
        self.out_q = out_q

    def run(self):
        while True:
            item_dict = self.in_q.get()

            case_list = db.select(r'select * from smzdm_case_info')
            for each_case in case_list:

                # 符合一个case的item
                will_push_item_list = []
                for k, v in SMZDMSearch.name:
                    if each_case[u'fromwhere'] == v or each_case[u'fromwhere'] == 0:
                        for case in SMZDMSearch.cases:
                            if case.test(each_case):
                                case.act(item_dict[k], each_case, will_push_item_list)

                case_id = int(each_case[u'case_id'])

                # do filter
                if will_push_item_list:
                    filter_list = db.select(r'select * from smzdm_filter where filter_id=?', case_id)

                    if filter_list:
                        for each_filter in filter_list:
                            for the_filter in self.filters:
                                if the_filter.test(each_filter):
                                    the_filter.act(will_push_item_list, each_filter)

                # SMZDMSearchLogger.info(message="Will push item:{} | Case:{}".format(will_push_item_list,each_case))
                if will_push_item_list:
                    self.out_q.put((will_push_item_list, each_case))

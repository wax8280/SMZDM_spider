# coding:utf-8
import traceback

from common.collections import get_or_return_default, remove_a_tag_from_text
from core.smzdm_filter import *
from lib.my_request import *
from smzdm_logger import UsualLogging
from config import urls, sleep_time, working_time
import threading
import random

SMZDMSpiderLogger = UsualLogging('SMZDMSpider')


class SMZDMSpider(threading.Thread):
    urls = urls

    def __init__(self, out_q):
        super(SMZDMSpider, self).__init__()
        self.out_q = out_q

    @staticmethod
    def _unpackup_common(item, each):
        item['article_id'] = get_or_return_default(each, u'article_id')
        item['article_url'] = get_or_return_default(each, u'article_url')
        item['article_mall'] = get_or_return_default(each, u'article_mall')
        item['article_link'] = get_or_return_default(each, u'article_link')
        item['article_price'] = get_or_return_default(each, u'article_price')
        item['timesort'] = get_or_return_default(each, u'timesort', 0)
        item['article_title'] = get_or_return_default(each, u'article_title')
        item['article_comment'] = int(get_or_return_default(each, u'article_comment', 0))
        item['article_collection'] = int(get_or_return_default(each, u'article_collection', 0))
        item['article_worthy'] = int(get_or_return_default(each, u'article_worthy', 0))
        item['article_unworthy'] = int(get_or_return_default(each, u'article_unworthy', 0))
        item['price_dimension'] = get_or_return_default(each[u'gtm'], u'dimension4')
        item['cates_str'] = get_or_return_default(each[u'gtm'], u'cates_str')
        item['rmb_price'] = get_or_return_default(each[u'gtm'], u'rmb_price')
        item['brand'] = get_or_return_default(each[u'gtm'], u'brand')
        item['article_rating'] = get_or_return_default(each, u'article_rating')
        item['article_data'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(item['timesort']))
        item['article_download_pic'] = u'0'
        item['worthy_percentage'] = int(float(item['article_worthy']) / float(
            item['article_worthy'] + item['article_unworthy']) * 100) if int(
            item['article_worthy'] + item['article_unworthy']) != 0 else 0.0
        remove_a_tag_from_text(item, each)

    @staticmethod
    def _unpackup_youhui(item_json):
        item_list = []
        for each in item_json:
            item = {}
            SMZDMSpider._unpackup_common(item, each)
            item['article_pic'] = re.match(r'(.*?.(jpeg|gif|png|jpg|bmp))', each[u'article_pic']).group()
            item['channel_dimension'] = get_or_return_default(each[u'gtm'], u'channel_dimension', u'youhui')
            item_list.append(item)
        return item_list

    @staticmethod
    def _unpackup_faxian(item_json):
        item_list = []
        for each in item_json:
            item = {}
            SMZDMSpider._unpackup_common(item, each)
            item['article_pic'] = re.match(r'(.*?.(jpeg|gif|png|jpg|bmp))', each[u'article_pic_url']).group()
            item['channel_dimension'] = u'faxian'
            item_list.append(item)
        return item_list

    @staticmethod
    def _unpackup_haitao(item_json):
        item_list = []
        for each in item_json:
            item = {}
            SMZDMSpider._unpackup_common(item, each)
            item['article_pic'] = re.match(r'(.*?.(jpeg|gif|png|jpg|bmp))', each[u'article_pic_url']).group()
            item['channel_dimension'] = get_or_return_default(each[u'gtm'], u'channel_dimension', u'haitao')
            item_list.append(item)
        return item_list

    @staticmethod
    def _parse_item(name, item_json):

        try:
            if name == 'youhui':
                item_list = SMZDMSpider._unpackup_youhui(item_json)

            elif name == 'faxian':
                item_list = SMZDMSpider._unpackup_faxian(item_json)

            elif name == 'haitao':
                item_list = SMZDMSpider._unpackup_haitao(item_json)

            is_parse_ok = True if len(item_list) else False
            if is_parse_ok:
                SMZDMSpiderLogger.info(message="Parse OK.Flag:{}".format(name))
            else:
                SMZDMSpiderLogger.warning(message='Cant parsing item(not found any items?) ')
        except Exception as e:
            traceback.print_exc()
            SMZDMSpiderLogger.warning(message="Error in SMZDMScrapy.parse_item.ErrInfo: {}".format(str(e)))
            is_parse_ok = False

        finally:
            return item_list

    @staticmethod
    def _spdier(url):
        item_json = {}
        try:
            common.session_init()
            response = common.common_get(url + str(int(time.time()) + 100000))
            item_json = response.json()
        except Exception as e:
            SMZDMSpiderLogger.warning(message="Error in crawling SMZDM API.ErrInfo: {}".format(str(e)))

        return item_json

    def run(self):
        while True:
            if int(time.strftime("%H")) in working_time:
                item_dict = {}
                for name, url in self.urls:
                    item_json = self._spdier(url)
                    item_dict[name] = self._parse_item(name, item_json)
                self.out_q.put(item_dict)
                time.sleep(random.randint(sleep_time[0], sleep_time[1]))
            else:
                SMZDMSpiderLogger.info(message="Not in working time slepping...")
                time.sleep(180)


if __name__ == '__main__':
    from Queue import Queue

    item_q = Queue()
    smzdm_spider = SMZDMSpider(item_q)
    smzdm_spider.start()
    while True:
        print item_q.get().keys()

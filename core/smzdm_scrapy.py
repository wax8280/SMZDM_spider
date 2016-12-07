# coding:utf-8
import traceback

from common.collections import get_or_return_default, remove_a_tag_from_text
from core.smzdm_filter import *
from lib.my_request import *


class SMZDMScrapy(object):
    def __init__(self):
        common.session_init()
        self.url = r''
        self.flag = ''
        self.is_parse_ok = False

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
            SMZDMScrapy._unpackup_common(item, each)
            item['article_pic'] = re.match(r'(.*?.(jpeg|gif|png|jpg|bmp))', each[u'article_pic']).group()
            item['channel_dimension'] = get_or_return_default(each[u'gtm'], u'channel_dimension', u'youhui')
            item_list.append(item)
        return item_list

    @staticmethod
    def _unpackup_faxian(item_json):
        item_list = []
        for each in item_json:
            item = {}
            SMZDMScrapy._unpackup_common(item, each)
            item['article_pic'] = re.match(r'(.*?.(jpeg|gif|png|jpg|bmp))', each[u'article_pic_url']).group()
            item['channel_dimension'] = u'faxian'
            item_list.append(item)
        return item_list

    @staticmethod
    def _unpackup_haitao(item_json):
        item_list = []
        for each in item_json:
            item = {}
            SMZDMScrapy._unpackup_common(item, each)
            item['article_pic'] = re.match(r'(.*?.(jpeg|gif|png|jpg|bmp))', each[u'article_pic_url']).group()
            item['channel_dimension'] = get_or_return_default(each[u'gtm'], u'channel_dimension', u'haitao')
            item_list.append(item)
        return item_list

    def parse_item(self):
        self.is_parse_ok = False
        item_list = []
        response = common.common_get(self.url + str(int(time.time()) + 100000))
        item_json = response.json()

        try:
            if self.flag == 'youhui':
                item_list = self._unpackup_youhui(item_json)

            elif self.flag == 'faxian':
                item_list = self._unpackup_faxian(item_json)

            elif self.flag == 'haitao':
                item_list = self._unpackup_haitao(item_json)

            self.is_parse_ok = True if len(item_list) else False
            if self.is_parse_ok:
                log_smzdm_scrapy.info("parse ok.")
            else:
                log_smzdm_scrapy.warning('cant parsing item(lack of article_id) ')
        except Exception as e:
            traceback.print_exc()
            log_smzdm_scrapy.warning("ErrInfo: " + str(e))
            self.is_parse_ok = False

        finally:
            return item_list

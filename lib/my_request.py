# -*- coding: utf-8 -*-
import time

import requests
import requests.exceptions

from config import ShouldTryTime
from smzdm_logger import *

log_requests = logging.getLogger('[requests]')
log_requests.setLevel(logging.INFO)


class common(object):
    my_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36'
    }
    _last_get_page_fail = False

    @staticmethod
    def session_init():
        common._session = requests.Session()

    @staticmethod
    def get_session():
        return common._session

    @staticmethod
    def common_get(url):
        try_time = 0

        while try_time <= ShouldTryTime:
            # 上一次get页面失败，暂停10秒
            if common._last_get_page_fail:
                time.sleep(10)

            try:
                try_time += 1
                response = common.get_session().get(url, headers=common.my_header, timeout=30)
                common._last_get_page_fail = False
                return response
            except Exception as e:
                common._last_get_page_fail = True
                log_requests.warning("fail to get " + url + " try_time " + str(try_time) + " ErrInfo: " + str(e))
                common._last_fail_url = url
        else:
            raise

    @staticmethod
    def common_post(url, post_thing):
        try_time = 0

        while try_time <= ShouldTryTime:
            # 上一次get页面失败，暂停10秒
            if common._last_get_page_fail:
                time.sleep(10)

            try:
                try_time += 1
                response = common.get_session().post(url, post_thing, headers=common.my_header, timeout=30)
                common._last_get_page_fail = False
                return response
            except Exception as e:
                log_requests.warning("fail to get " + url + " try_time " + str(try_time) + " ErrInfo: " + str(e))
                common._last_get_page_fail = True
                common._last_fail_url = url
        else:
            raise

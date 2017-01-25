import logging
import os
from functools import partial
from logging.handlers import WatchedFileHandler
from config import LOG_PATH


class VLogging(object):
    logger_dict = {}

    @staticmethod
    def log(name, message):
        VLogging.get_logger(name).info(message)

    @staticmethod
    def get_logger(name):

        failed_path = os.path.join(LOG_PATH, name)

        if not os.path.exists(failed_path):
            os.makedirs(failed_path)

        if name not in VLogging.logger_dict:
            logger = logging.getLogger(name)

            formatter = logging.Formatter(
                '[%(asctime)s][' + name + '] %(message)s')
            file_handler = WatchedFileHandler(
                os.path.join(failed_path, name + '.log'))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logger.setLevel(logging.INFO)

            VLogging.logger_dict[name] = logger
        return VLogging.logger_dict[name]


class UsualLogging(VLogging):
    info_mes = '[INFO] {}'
    error_mes = '[ERROR] {}'
    waring_mes = '[WARING] {}'

    def __init__(self, name):
        self._name = name
        self._logger = partial(VLogging.log, name=self._name)

    def info(self, message):
        self._logger(
            message=self.info_mes.format(message)
        )

    def error(self, message):
        self._logger(
            message=self.error_mes.format(message)
        )

    def warning(self, message):
        self._logger(
            message=self.waring_mes.format(message)
        )

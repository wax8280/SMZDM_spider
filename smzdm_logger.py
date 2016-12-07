import logging
formatter = logging.Formatter('%(asctime)s - [%(module)s][%(funcName)s]  - [%(levelname)s]%(message)s')
logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - [%(module)s][%(funcName)s]  - [%(levelname)s]%(message)s')

log_smzdm_scrapy = logging.getLogger('[smzdm_scrapy]')
log_smzdm_scrapy.setLevel(logging.INFO)
# ch = logging.StreamHandler()
# ch.setFormatter(formatter)
# log_smzdm.addHandler(ch)
# fh = logging.FileHandler('./tmp/smzdm.log')
# fh.setFormatter(formatter)
# log_smzdm.addHandler(fh)

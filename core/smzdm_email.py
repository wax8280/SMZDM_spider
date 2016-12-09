# coding:utf-8
import codecs
import smtplib
import threading
from Queue import Queue
from email.header import Header
from email.mime.text import MIMEText

from config import mail_host, mail_pass, mail_user, EmailTryTime, sender,sender_worker
from lib.templite import Templite
from smzdm_logger import *

log_send_mail = logging.getLogger('[send_mail]')
log_send_mail.setLevel(logging.INFO)


class LazyEmailConnection(object):
    def __init__(self):
        self.smtpobj = smtplib.SMTP(mail_host, 25)

    def __enter__(self):
        self.smtpobj.login(mail_user, mail_pass)
        return self.smtpobj

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.smtpobj.quit()


with codecs.open(r'./templates/e_mail.html', 'r', 'utf-8') as f:
    lines = f.readlines()

template_email_body = Templite(u"".join(c for c in lines))


def _make_content(push_item_list, each_case):
    receivers = each_case[u'e_mail']
    user_name = receivers
    case_id = str(each_case[u'case_id'])
    to_send_list = []
    for each_item in push_item_list:

        context_ = {'case_id': case_id}
        for _ in ['article_title', 'article_price', 'article_mall', 'article_pic', 'article_url', 'article_content',
                  'cates_str', 'article_comment', 'article_collection', 'worthy_percentage', 'article_data']:
            context_[_] = each_item[_]
        text = template_email_body.render(context_)

        message = MIMEText(text, 'html', 'utf-8')
        message['From'] = Header(u"快人一步", 'utf-8')
        message['To'] = Header(user_name, 'utf-8')
        message['Subject'] = Header(context_['article_title'], 'utf-8')
        to_send_list.append(
                (each_item, str(each_item['article_id']), case_id, user_name, receivers, message.as_string()))

    return to_send_list


def _send_mail(context_queue, return_queue):
    with LazyEmailConnection() as smtpobj:
        while context_queue.qsize() > 0:
            try_time, sended = 0, False
            # article_id, case_id, user_name, receivers, message = context_queue.get()
            case_item, case_info = context_queue.get()
            each_irem, article_id, case_id, user_name, receivers, message = case_item

            # 重试
            while try_time < EmailTryTime and not sended:
                try:
                    log_send_mail.info(threading.current_thread().name + ' is sending.')
                    smtpobj.sendmail(sender, receivers, message)
                    sended = True
                except Exception as e:
                    log_send_mail.warning(
                            "Failed send to:" + user_name + '|E-Mail:' + receivers + '|Push id:' + str(
                                    case_id) + '|Article ID:' + article_id + "|ErrInfo:" + str(e))

                    try_time += 1
                    # 最后一次重试
                    if try_time == EmailTryTime:
                        return return_queue.put((case_info, each_irem, False))

                else:
                    log_send_mail.info(
                            "Send to:" + user_name + '|E-Mail:' + receivers + '|Push id:' + str(
                                    case_id) + '|Article ID:' + article_id)
                    return return_queue.put((case_info, each_irem, True))


def send_email(all_task):
    # each_task[0]:list 为每个case的item
    # each_task[1]:dict 为每个case的信息
    context_list = [(each_item, each_task[1]) for each_task in all_task
                    for each_item in _make_content(each_task[0], each_task[1])]

    context_queue = Queue()
    return_queue = Queue()

    for i in context_list:
        context_queue.put(i)

    worker_count = sender_worker
    worker_list = []

    for i in range(worker_count):
        worker_list.append(threading.Thread(target=_send_mail, args=(context_queue, return_queue)))

    for j in range(worker_count):
        worker_list[j].start()

    for j in range(worker_count):
        worker_list[j].join()

    return return_queue

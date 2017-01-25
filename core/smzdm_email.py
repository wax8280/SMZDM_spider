# coding:utf-8
import codecs
import smtplib
import threading
from Queue import Queue
from email.header import Header
from email.mime.text import MIMEText

from config import mail_host, mail_pass, mail_user, EmailTryTime, sender, sender_worker
from lib.templite import Templite
from smzdm_logger import UsualLogging
import threading

SMZDMEmailLogger = UsualLogging('SMZDMEmail')


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

template_email_body = Templite(u"".join(lines))


def _make_content(will_push_item_list, each_case):
    receivers = each_case[u'e_mail']
    user_name = receivers
    case_id = str(each_case[u'case_id'])
    to_send_list = []
    for each_item in will_push_item_list:

        context_ = {'case_id': case_id}
        for _ in ['article_title', 'article_price', 'article_mall', 'article_pic', 'article_url', 'article_content',
                  'cates_str', 'article_comment', 'article_collection', 'worthy_percentage', 'article_data']:
            context_[_] = each_item[_]
        text = template_email_body.render(context_)

        content = MIMEText(text, 'html', 'utf-8')
        content['From'] = Header(u"快人一步", 'utf-8')
        content['To'] = Header(user_name, 'utf-8')
        content['Subject'] = Header(context_['article_title'], 'utf-8')
        to_send_list.append(
            (each_item, str(each_item['article_id']), case_id, user_name, receivers, content.as_string()))

    return to_send_list


def _send_mail(to_send_list):
    sent_id_list = set()
    sent_item_list = []
    with LazyEmailConnection() as smtpobj:
        for each_to_send in to_send_list:

            each_item, article_id, case_id, user_name, receivers, content = each_to_send

            if article_id in sent_id_list:
                sent_item_list.append((each_item, case_id))
                break

            try_time, sended = 0, False
            # 重试
            while try_time < EmailTryTime and not sended:
                try:
                    SMZDMEmailLogger.info(threading.current_thread().name + ' is sending.')
                    smtpobj.sendmail(sender, receivers, content)
                    sended = True
                except Exception as e:
                    SMZDMEmailLogger.warning(
                        "Failed send to:" + user_name + '|E-Mail:' + receivers + '|Push id:' + str(
                            case_id) + '|Article ID:' + article_id + "|ErrInfo:" + str(e))

                    try_time += 1
                else:
                    SMZDMEmailLogger.info(
                        "Send to:" + user_name + '|E-Mail:' + receivers + '|Push id:' + str(
                            case_id) + '|Article ID:' + article_id)
                    sent_id_list.add(article_id)
                    sent_item_list.append((each_item, case_id))

        return sent_item_list


class SMZDMEmail(threading.Thread):
    def __init__(self, in_q, out_q):
        super(SMZDMEmail, self).__init__()
        self.in_q = in_q
        self.out_q = out_q

    def run(self):
        while True:
            will_push_item_list, each_case = self.in_q.get()
            to_send_list = _make_content(will_push_item_list, each_case)
            sent_item_list = _send_mail(to_send_list)
            self.out_q.put(sent_item_list)

# coding:utf-8
import re


def get_or_return_default(dict_, key_, default=u'0'):
    try:
        v_ = dict_[key_]
    except:
        v_ = default
    finally:
        return v_


# 移除article_content中的<a>标签
def remove_a_tag_from_text(item, each):
    s = ''
    reObj2 = re.compile(r'<a', re.S | re.U)
    a_len_ = len(re.findall(reObj2, each[u'article_content']))
    patten = str(r'(?:(.*?)<a.*?/a>){' + str(a_len_) + r'}(.*)$')
    reObj1 = re.compile(patten, re.S | re.U)
    b = re.findall(reObj1, each[u'article_content'])
    if b == []:
        item['article_content'] = each[u'article_content']
    else:
        for each_ in b:
            for each2_ in each_:
                s += each2_
            item['article_content'] = s

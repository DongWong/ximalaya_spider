# -*- coding: utf-8 -*-
# by nan gong er gou
import hashlib
import random
import time


def get_server_time(session, time_api,header):
    '''
    获取服务器时间戳
    '''
    r = session.get(time_api, headers=header)
    print('服务器时间戳：', r.text)
    return r.text


def get_xml_sign(session, time_api,header):
    '''
    获取sign： md5(himalaya-服务器时间戳)(100以内随机数)服务器时间戳(100以内随机数)现在时间戳
    :return: xm_sign
    '''
    nowtime = str(round(time.time() * 1000))
    servertime = session.get(time_api, headers=header).text
    # 构造 xm-sign
    sign = str(hashlib.md5('himalaya-{}'.format(servertime).encode()).hexdigest()) + '({})'.format(
        str(round(random.random() * 100))) + servertime + '({})'.format(str(round(random.random() * 100))) + nowtime
    return sign

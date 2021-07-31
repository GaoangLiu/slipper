#!/usr/bin/env python
import base64
import hmac
import os
import random
import re
import sys
import time
from collections import defaultdict

import codefast as cf

from dofast.config import decode


def generate_token(key: str, expire=3) -> str:
    """
    :param key:  str (用户给定的key，需要用户保存以便之后验证token,每次产生token时的key都可以是同一个key)
    :param expire: int(最大有效时间，单位为s)
    :return:  state: str
    refer https://zhuanlan.zhihu.com/p/141623990
    """
    ts_str = str(time.time() + expire)
    ts_byte = ts_str.encode("utf-8")
    sha1_hex = hmac.new(key.encode("utf-8"), ts_byte, 'sha1').hexdigest()
    token = ts_str + ':' + sha1_hex
    b64_token = base64.urlsafe_b64encode(token.encode("utf-8"))
    return b64_token.decode("utf-8")


def certify_token(key: str, token: str) -> bool:
    """
    :param key: str
    :param token: str
    :return:  boolean
    """
    token_str = base64.urlsafe_b64decode(token).decode('utf-8')
    token_list = token_str.split(':')
    if len(token_list) != 2:
        return False
    ts_str = token_list[0]
    if float(ts_str) < time.time():
        return False
    known_sha1_ts_str = token_list[1]
    sha1 = hmac.new(key.encode("utf-8"), ts_str.encode('utf-8'), 'sha1')
    calc_sha1_ts_str = sha1.hexdigest()
    if calc_sha1_ts_str != known_sha1_ts_str:
        return False
    return True



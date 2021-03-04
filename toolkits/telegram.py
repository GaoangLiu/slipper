"""Telegram bot"""
import os
import json
import requests

import dofast.utils as du
from dofast.utils import p, pp
from dofast.config import HEMA_BOT, AUTH, HTTP_PROXY, TELEGRAM_KEY
from .endecode import short_decode, decode_with_keyfile as dkey

proxies = {'http': dkey(AUTH, HTTP_PROXY)}

def bot_say(api_token: str, text: str, bot_name: str = 'PlutoShare'):
    url = f"https://api.telegram.org/bot{api_token}/sendMessage?chat_id=@{bot_name}&text={text}"
    res = requests.get(url, proxies=proxies)
    p(res)


def read_hema_bot():
    bot_updates = dkey(TELEGRAM_KEY, HEMA_BOT)
    resp = du.client.get(bot_updates, proxies=proxies)
    pp(json.loads(resp.text))

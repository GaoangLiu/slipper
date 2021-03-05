"""Telegram bot"""
import os
import json
import requests

import app.utils as du
from app.utils import p, pp
from app.config import HEMA_BOT, AUTH, HTTP_PROXY, TELEGRAM_KEY
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

def download_file_by_id(file_id:str)->None:
    bot_updates = dkey(TELEGRAM_KEY, HEMA_BOT)
    file_url = bot_updates.replace('getUpdates', f'getFile?file_id={file_id}')
    json_res = du.client.get(file_url, proxies=proxies).text
    file_name = json.loads(json_res)['result']['file_path']
    p('File name is: ', file_name)

    file_url = bot_updates.replace('getUpdates', file_name).replace('/bot', '/file/bot')
    du.download(file_url, proxy=dkey(AUTH, HTTP_PROXY))    

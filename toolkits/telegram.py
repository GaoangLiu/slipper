"""Telegram bot"""
import os
import json
import requests


def bot_say(api_token: str, text: str, bot_name:str='PlutoShare'):
    proxies = json.load(open(
        '/etc/proxy.json', 'r')) if os.path.exists('/etc/proxy.json') else None
    url = f"https://api.telegram.org/bot{api_token}/sendMessage?chat_id=@{bot_name}&text={text}"
    res = requests.get(url, proxies=proxies)
    print(res)

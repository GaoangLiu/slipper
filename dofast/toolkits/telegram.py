"""Telegram bot"""
import functools
import json
import smtplib
from email.mime.text import MIMEText

import codefast as cf
import requests
from codefast.utils import retry

import dofast.utils as du
from dofast.config import decode, SALT

proxies = {'https': decode('HTTP_PROXY')}


@retry()
def bot_say(api_token: str,
            text: str,
            bot_name: str = 'PlutoShare',
            use_proxy: bool = False):
    url = f"https://api.telegram.org/bot{api_token}/sendMessage?chat_id=@{bot_name}&text={text}"
    res = requests.get(url, proxies=proxies if use_proxy else None)
    print(res, res.content)


def tg_bot(use_proxy: bool = True):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _msg = func(*args, **kwargs)
            _token = decode('mess_alert')
            url = f"https://api.telegram.org/bot{_token}/sendMessage?chat_id=@messalert&text={_msg}"
            res = requests.get(
                url, proxies=proxies) if use_proxy else requests.get(url)
            return res, res.content

        return wrapper

    return decorator


def bot_messalert(msg: str) -> None:
    bot_say(decode('mess_alert'), msg, bot_name='messalert')


@retry()
def messalert(msg: str) -> None:
    '''send Telegram message via remote consumer'''
    from dofast.security._hmac import generate_token    
    key = io.read(SALT, '')
    res = cf.net.post('http://a.ddot.cc:6363/messalert',
                      json={
                          'token': generate_token(key),
                          'text': msg
                      })
    assert res.text == 'SUCCESS', 'Telegram message failed to send.'


def read_hema_bot():
    bot_updates = decode('pluto_share')
    resp = du.client.get(bot_updates, proxies=proxies)
    print(json.loads(resp.text))


def download_file_by_id(file_id: str) -> None:
    bot_updates = decode('pluto_share')
    file_url = bot_updates.replace('getUpdates', f'getFile?file_id={file_id}')
    json_res = du.client.get(file_url, proxies=proxies).text
    file_name = json.loads(json_res)['result']['file_path']

    file_url = bot_updates.replace('getUpdates',
                                   file_name).replace('/bot', '/file/bot')
    du.download(file_url, proxy=proxies)


def mail2foxmail(subject: str, message: str):
    r = decode('FOXMAIL')
    YahooMail().send(r, subject, message)


def mail2gmail(subject: str, message: str):
    r = decode('GMAIL2')
    YahooMail().send(r, subject, message)


class YahooMail:
    def __init__(self):
        self.smtp_server = "smtp.mail.yahoo.com"
        self.smtp_port = 587
        self.username = decode('YAHOO_USER_NAME')
        self.password = decode('YAHOO_USER_PASSWORD')
        self.email_from = self.username + "@yahoo.com"
        mail = smtplib.SMTP(self.smtp_server, self.smtp_port)
        mail.set_debuglevel(debuglevel=True)
        mail.starttls()
        mail.login(self.username, self.password)
        self.mail = mail

    def send(self, receiver: str, subject: str, message: str) -> bool:
        msg = MIMEText(message.strip())
        msg['Subject'] = subject
        msg['From'] = self.email_from
        msg['To'] = receiver

        try:
            du.info("Yahoo mail login success")
            self.mail.sendmail(self.email_from, receiver, msg.as_string())
            du.info(f'SUCCESS[YahooMail.send()]'
                    f'{Message(receiver, subject, message)}')
            # self.mail.quit()
            return True
        except Exception as e:
            du.error("Yahoo mail sent failed" + repr(e))
            return False


class Message:
    def __init__(self, receiver: str, subject: str, message: str):
        self.r = receiver
        self.s = subject
        self.m = message

    def __repr__(self) -> str:
        return '\nReceiver: {}\nSubject : {}\nMessage : {}'.format(
            self.r, self.s, self.m)

import random
import sys
import time

import codefast as cf
import requests
from bs4 import BeautifulSoup
from faker import Faker

from .consumer import Consumer
from dofast.utils import download

cf.logger.level = 'info'
cf.info('Go.')


class ds:
    DOMAINS = io.read('/tmp/cnlist.txt')
    HEADERS = io.read('/tmp/headers.txt')


def fake_headers():
    h = jsn.read(random.sample(ds.HEADERS, 1)[0])
    h['User-Agent'] = Faker().user_agent()
    res = dict(
        (k, h[k]) for k in list(h) if k not in ('Date', 'Vary', 'Server'))
    return res


def surf():
    s = requests.Session()
    if not ds.DOMAINS:
        ds.DOMAINS = io.read('/tmp/cnlist.txt')
    domain = random.sample(ds.DOMAINS, 1)[0]

    try:
        url = domain if domain.startswith('http') else 'http://' + domain
        if random.randint(1,100)>50:
            url=url.replace('https', 'http')

        cf.info('visiting ' + url)
        r = s.get(url, headers=fake_headers(), timeout=1)
        soup = BeautifulSoup(r.text, 'html.parser')

        if url.endswith(('png', 'jpg', 'txt', 'json', 'jpeg', 'mp3', 'mp4', 'pdf', 'mobi')):
            cf.info('Downloading {}'.format(url))
            download(url, name='/tmp/websurf.png')

        io.write(r.text, '/tmp/tmp')

        for link in soup.find_all('a'):
            _url = link.get('href')
            if _url and _url.startswith('http'):
                ds.DOMAINS.append(_url)

        # refresh urls
        ds.DOMAINS = list(set(ds.DOMAINS))
        ds.HEADERS.append(r.headers)

    except Exception as e:
        if domain in ds.DOMAINS:
            ds.DOMAINS.remove(domain)
        cf.error(str(e))
    finally:
        ds.DOMAINS = sorted(ds.DOMAINS, key=lambda e: len(e), reverse=True)
        ds.HEADERS = ds.HEADERS[:10000]


class SurfWeb(Consumer):
    def publish_message(self, message: dict):
        surf()
        return True


def run():
    SurfWeb('web', 'surf').run()


if __name__ == '__main__':
    run()

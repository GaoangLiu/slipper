import random
import time

import codefast as cf
import requests
from bs4 import BeautifulSoup
from faker import Faker

from .consumer import Consumer

cf.logger.level = 'info'
cf.info('Go.')

def fake_headers():
    h = jsn.read(random.sample(io.read('/tmp/headers.txt'), 1)[0])
    h['User-Agent'] = Faker().user_agent()
    res = dict(
        (k, h[k]) for k in list(h) if k not in ('Date', 'Vary', 'Server'))
    return res


def surf():
    url_file = '/tmp/cnlist.txt'
    s = requests.Session()
    _domains, _headers = io.read(url_file), io.read('/tmp/headers.txt')
    domain = random.sample(_domains, 1)[0]

    try:
        url = domain if domain.startswith('http') else 'http://' + domain
        cf.info('visiting ' + url)
        r = s.get(url, headers=fake_headers(), timeout=6)
        time.sleep(random.randint(3, 10))
        soup = BeautifulSoup(r.text, 'html.parser')
        io.write(r.text, '/tmp/tmp')

        for link in soup.find_all('a'):
            _url = link.get('href')
            if _url.startswith('http'):
                _domains.append(_url)

        # refresh urls
        _domains = list(set(_domains))
        _headers.append(r.headers)

    except Exception as e:
        _domains.remove(domain)
        cf.error(e)
    finally:
        random.shuffle(_domains)
        io.write(_domains[:10000], url_file)
        io.write(_headers, '/tmp/headers.txt')


class SurfWeb(Consumer):
    def publish_message(self, message: dict):
        surf()
        return True


def run():
    SurfWeb('web', 'surf').run()


if __name__ == '__main__':
    run()

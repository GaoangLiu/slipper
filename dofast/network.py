import json
import os
import re
import socket
import urllib.request
from typing import List

import arrow
import codefast as cf
import twitter
from bs4 import BeautifulSoup
from requests import Session

from .config import decode, fast_text_decode, fast_text_encode
from .oss import Bucket
from .utils import githup_upload

socket.setdefaulttimeout(3)

import cgi
import http.server
import io

from .oss import Bucket

cf.logger.level = 'info'


class Bookmark(Bucket):
    def __init__(self):
        super(Bookmark, self).__init__()
        self._local = '/tmp/bookmark.json'
        if not cf.file.exists(self._local):
            self.download('bookmark.json', self._local)

        self.json = cf.json.read(
            fast_text_decode(cf.file.read(self._local, '')))

    def reload(self):
        ''' reload file whenever necessary '''
        self.download('bookmark.json', self._local)
        self.json = cf.json.read(
            fast_text_decode(cf.file.read(self._local, '')))

    def _update_remote(self):
        cf.file.write(fast_text_encode(str(self.json)), self._local)
        self.upload(self._local)

    def add(self, keyword: str, url: str) -> None:
        if keyword in self.json:
            cf.warning(
                f'{keyword} with URL {self.json[keyword]} already added.')
        else:
            self.json[keyword] = url
            self._update_remote()
            cf.info(f'{keyword} with URL {self.json[keyword]} added SUCCESS.')

    def remove(self, keyword: str = '', url: str = '') -> None:
        ''' can delete by either keyword or URL'''
        _tuple = ('', '')
        if keyword and keyword in self.json:
            _tuple = (keyword, self.json[keyword])
            del self.json[keyword]

        elif url:
            for _key in list(self.json):
                if self.json[_key] == url:
                    _tuple = (_key, self.json[_key])
                    del self.json[_key]
        self._update_remote()
        cf.info(f'{_tuple[0]} / {_tuple[1]} remove SUCCESS')

    def get_url_by_keyword(self, keyword: str) -> str:
        return self.json.get(keyword, 'https://google.com')

    def list(self) -> None:
        for k, v in self.json.items():
            print(" {:<15} {:<63}".format(k, v))


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        r, info = self.deal_post_data()
        print(r, info, "by: ", self.client_address)
        f = io.BytesIO()
        if r:
            f.write(b"Success\n")
        else:
            f.write(b"Failed\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def deal_post_data(self):
        ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
        pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
        pdict['CONTENT-LENGTH'] = int(self.headers['Content-Length'])
        if ctype == 'multipart/form-data':
            form = cgi.FieldStorage(fp=self.rfile,
                                    headers=self.headers,
                                    environ={
                                        'REQUEST_METHOD':
                                        'POST',
                                        'CONTENT_TYPE':
                                        self.headers['Content-Type'],
                                    })
            print(type(form))
            try:
                if isinstance(form["file"], list):
                    for record in form["file"]:
                        open("./%s" % record.filename,
                             "wb").write(record.file.read())
                else:
                    open("./%s" % form["file"].filename,
                         "wb").write(form["file"].file.read())
            except IOError:
                return (
                    False,
                    "Can't create file to write, do you have permission to write?"
                )
        return (True, "Files uploaded")


class Network:
    @classmethod
    def is_good_proxy(cls, proxy: str) -> bool:
        """Check whether this proxy is valid or not"""
        try:
            pxy = {'http': proxy}
            proxy_handler = urllib.request.ProxyHandler(pxy)
            opener = urllib.request.build_opener(proxy_handler)
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            sock = urllib.request.urlopen(
                'http://www.google.com')  # change the url address here
        except urllib.error.HTTPError as e:
            print('Error code: ', e.code)
            return False
        except Exception as detail:
            print("ERROR:", detail)
            return False
        return True

    def ipcheck(self, proxy: str) -> None:
        if self.is_good_proxy(proxy):
            print("")


class Twitter(twitter.Api):
    def __init__(self):
        super(Twitter,
              self).__init__(consumer_key=decode('consumer_key'),
                             consumer_secret=decode('consumer_secret'),
                             access_token_key=decode('access_token'),
                             access_token_secret=decode('access_token_secret'),
                             proxies={'http': decode('http_proxy')})

    def hi(self):
        print('Hi, Twitter.')

    def post_status(self, text: str, media=[]):
        resp = self.PostUpdate(text, media=media)
        print("Text  : {}\nMedia : {}\nResponse:".format(text, media))
        cf.say(resp)

    def post(self, args: list):
        ''' post_status wrapper'''
        assert isinstance(args, list)

        text, media = '', []
        media_types = ('.png', '.jpeg', '.jpg', '.mp4', '.gif')

        for e in args:
            if cf.file.exists(e):
                if e.endswith(media_types):
                    media.append(e)
                else:
                    text += cf.file.read(e, '')
            else:
                text += e
        self.post_status(text, media)


class Douban:
    @classmethod
    def query_film_info(cls, dblink: str) -> str:
        soup = BeautifulSoup(cf.net.get(dblink).text, 'lxml')
        film_info = soup.find('script', {
            'type': "application/ld+json"
        }).contents[0].strip().replace('\n', '')
        dbinfos = json.loads(film_info)
        poster = dbinfos['image'].replace('.webp', '.jpg').replace(
            's_ratio_poster', 'l')
        cf.utils.shell('curl -o poster.jpg {}'.format(poster))
        cf.logger.info('// poster.jpg downloaded')

        html = ""
        with open('info.txt', 'w') as f:
            html += "#" + dbinfos['name'].rstrip() + "\n\n"
            info = soup.find('div', {'id': 'info'})
            for l in info.__str__().split("br/>"):
                text = BeautifulSoup(l, 'lxml').text.lstrip()
                if any(e in text
                       for e in ('导演', '主演', '季数', 'IMDb', '编剧', '又名')):
                    continue
                if text:
                    if '类型' in text:
                        text = text.replace(': ', ': #').replace('/ ', '#')
                    html += "➖" + text + "\n"

            vsummary = soup.find('span', {"property": 'v:summary'})
            vsummary = '\n'.join(
                (l.lstrip() for l in vsummary.text.split('\n')))

            html += "➖豆瓣 ({}): {}".format(
                dbinfos.get('aggregateRating', {}).get('ratingValue', '/'),
                dblink) + "\n\n"

            html += " {} \n".format(vsummary)
            cf.logger.info(html)
            f.write(html)


class LunarCalendar:
    '''爬虫实现的农历'''
    @classmethod
    def display(cls, date_str: str = ""):
        year, month, day = arrow.now().format('YYYY-MM-DD').split('-')
        if date_str:
            year, month, day = date_str.split('-')[:3]
        print('Date {}-{}-{}'.format(year, month, day))

        r = cf.net.get(
            'https://wannianrili.51240.com/ajax/?q={}-{}&v=19102608'.format(
                year, month))

        s = BeautifulSoup(r.text, 'lxml')
        pairs = []
        for x in s.findAll('div', {'class': 'wnrl_k_you'}):
            for y in x.findAll(
                    'div', {
                        'class': [
                            'wnrl_k_you_id_biaoti', 'wnrl_k_you_id_wnrl_riqi',
                            'wnrl_k_you_id_wnrl_nongli'
                        ]
                    }):
                pairs.append(y.text)

        weekdays = ["星期" + w for w in "一二三四五六日"]
        for w in weekdays:
            print("{:<2} | {:<8}".format(' ', w), end="")
        print('\n' + '*' * 117)

        for w in weekdays:
            if not pairs[0].endswith(w):
                print("\033[30m{} | {}\033[0m".format(pairs[1], pairs[2]),
                      end="\t")
            else:
                break

        for j in range(0, len(pairs), 3):
            if day == pairs[j + 1]:
                print("\033[31m\033[1m{} | {}\033[0m".format(
                    pairs[j + 1], pairs[j + 2]),
                      end="\t")
            else:
                print("{} | {}".format(pairs[j + 1], pairs[j + 2]), end="\t")
            if pairs[j].endswith('星期日'):
                print('')
        print('')


class AutoProxy(Bucket):
    pac = '/tmp/autoproxy.pac'
    tmp = '/tmp/autoproxy_encrypted'

    @classmethod
    def query_rules(cls) -> List[str]:
        AutoProxy().download(cf.file.basename(cls.tmp), export_to=cls.tmp)
        text = cf.file.read(cls.tmp)
        return fast_text_decode(text).split('\n')

    @classmethod
    def sync2git(cls):
        f = cf.file.basename(cls.pac)
        cf.file.copy(cls.pac, f)
        githup_upload(f, shorten=False)
        cf.logger.info(f'{f} was synced to Github.')
        cf.file.rm(f)

    @classmethod
    def add(cls, url: str) -> None:
        rule_list = cls.query_rules()
        url = '  \"||{}\"'.format(url)
        if any(url in e for e in rule_list):
            cf.logger.info('{} was already included.'.format(url))
            return

        rule_list.insert(63, url)
        str_rules = '\n'.join(rule_list)
        text_new = fast_text_encode(str_rules)
        cf.file.write(text_new, cls.tmp)
        cf.file.write(str_rules, cls.pac)
        AutoProxy().upload(cls.tmp)
        cf.logger.info('{} added to rule list SUCCESS'.format(url))
        cls.sync2git()

    @classmethod
    def delete(cls, url: str) -> None:
        rule_list = cls.query_rules()
        url = '  \"||{}\"'.format(url)
        if url in rule_list:
            rule_list.remove(url)
            str_rules = '\n'.join(rule_list)
            str_rules_encrypted = fast_text_encode(str_rules)
            cf.file.write(str_rules_encrypted, cls.tmp)
            cf.file.write(str_rules, cls.pac)
            AutoProxy().upload(cls.tmp)
            cf.logger.info('{} removed from rule list SUCCESS'.format(url))
            cls.sync2git()
        else:
            cf.logger.info('{} was NOT included in rule list'.format(url))


class CoinMarketCap:
    def __init__(self):
        self.url_listing = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        self.url_quote = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': decode('coin_market_api_key')
        }

        self.client = Session()
        self.client.headers.update(headers)

    def quote(self, coins: list = ['BTC']) -> dict:
        parameters = {'symbol': ','.join(coins)}
        resp = self.client.get(self.url_quote, params=parameters)
        return json.loads(resp.text)

    def part_display(self, d: dict) -> None:
        fields = ['cmc_rank', 'symbol', 'name']
        for coin in list(d['data']):
            print('-' * 63)
            prices = d['data'][coin]['quote']['USD']
            for f in fields:
                print(" {:<20} {:<20}".format(f, d['data'][coin][f]))

            tags = ['price'] + [
                'percent_change_' + _
                for _ in '1h|24h|7d|30d|60d|90d'.split('|')
            ]
            for t in tags:
                v = prices[t]
                if t.startswith('percent'):
                    v = cf.format.red(v) if float(v) > 0 else cf.format.green(
                        v)
                print(" {:<20} {:<20}".format(t, v))


class Phone:
    def parse(self, text: str):
        res = BeautifulSoup(text, 'lxml')
        if '系统检测您的访问过于频繁' in str(res):
            cf.logger.info('Unicoms leaders mothers are all dead !!! R.I.P. !')
            return

        if '请在系统完成升级后再来办理' in str(res):
            cf.logger.info('System under maintenance. Try again tomorrow.')
            return

        if '暂时无法为您提供服务' in str(res):
            cf.logger.info('暂时无法为您提供服务')
            return

        def _pure_text(t):
            for s in ["\\r", "\\n", "\\t", "\n", " ", "\t", "\r", "\n"]:
                t = t.lstrip().replace(s, '')
            return '\t'.join(
                [i for i in t.replace('"', '\'').split('\'') if len(i) > 0])

        for i, span in enumerate(res.findAll('span', {'class': 'wz_22'})):
            label = '免流' if i == 0 else '日租'
            print("{}: {}".format(
                label,
                _pure_text(span.text).replace('MB',
                                              ' MB').replace('GB', ' GB')))

        data = res.findAll('p', {'class': 'TotleData'})
        for i, d in enumerate(data):
            text = d.text
            text = re.sub(r'[\r\n\s\t]', '', text)
            used = re.search(r'已用(.*)',
                             text).groups()[0].replace('MB', ' MB').replace(
                                 'GB', ' GB')
            total = re.search(r'共(.*),', text).groups()[0].replace(
                'MB', ' MB').replace('GB', ' GB')

            c = "余量" if i == 0 else "通话"
            print("{}: {} / {}".format(c, used, total))

    def unicom(self):
        _headers = {
            'cookie': decode('unicom_cookie'),
        }
        url = 'http://m.client.10010.com/mobileService/operationservice/queryOcsPackageFlowLeftContent.htm'
        params = {'menuId': '000200020004'}
        r = cf.net.post(url, data=params, headers=_headers)
        if r.status_code != 200:
            cf.logger.warning(r.text)
        else:
            self.parse(r.text)


def bitly(uri: str) -> None:
    query_params = {'access_token': decode('bitly_token'), 'longUrl': uri}

    endpoint = 'https://api-ssl.bitly.com/v3/shorten'
    response = cf.net.get(endpoint, params=query_params)

    data = response.json()
    print("{:<20} {}".format("long url", uri))
    print("{:<20} {}".format("shorten url", data['data']['url']))
    short = data['data']['url']
    os.system(f"echo {short} | pbcopy")

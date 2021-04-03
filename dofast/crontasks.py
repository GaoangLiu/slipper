''' crontab tasks. '''
import json
import os
import socket
import requests
import bs4
from .config import decode
from .logger import Logger
from .toolkits.telegram import bot_messalert

socket.setdefaulttimeout(30)
logger = Logger('/var/log/phone.log')


class PapaPhone:
    def __init__(self):
        pass

    def get_headers(self):
        h = {}
        h["Cookie"] = decode('cmcc_cookie')
        h['Authorization'] = decode('cmcc_authorization')
        h["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"
        h["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        h['device'] = 'iPhone 7'
        h['Referer'] = 'https://h5.ha.chinamobile.com/hnmccClientWap/h5-rest/'
        return h

    def _query_flow(self) -> (float, str):
        try:
            url = 'https://h5.ha.chinamobile.com/h5-rest/flow/data'
            params = {'channel': 2, 'version': '6.4.2'}
            res = requests.get(url, data=params, headers=self.get_headers())
            json_res = json.loads(res.text)
            flow = float(json_res['data']['flowList'][0]['surplusFlow'])
            unit = json_res['data']['flowList'][0]['surplusFlowUnit']
            logger.info(f'Papa iPhone data flow remain {flow} GB.')
            return flow, unit
        except Exception as e:
            logger.error(f'Get data flow failed: {repr(e)}')
            return -1, 'MB'

    @classmethod
    def issue_recharge_message(cls, retry: int = 3) -> None:
        ''' issue recharge message when dataflow less than 1G'''
        if retry <= 0:
            bot_messalert('手机余量查询失败\n' + '已经连续重试 3 次，全部失败。')
        else:
            flow, unit = PapaPhone()._query_flow()
            if flow == -1:
                cls.issue_recharge_message(retry - 1)
            elif flow < 1 or unit == 'MB':
                message = f'Papa手机流量还剩余 {flow} {unit}，可以充值了。'
                logger.info(message)
                bot_messalert(message)

    @classmethod
    def issue_daily_usage(cls):
        value, unit = PapaPhone()._query_flow()
        msg = f'日常流量提醒 \n\n papa cellphone data flow {value} {unit}'
        bot_messalert(msg)


class GithubTasks:
    '''Github related tasks '''
    @classmethod
    def git_commit_reminder(cls) -> None:
        cnt = cls._count_commits()
        prev_cnt, file_ = 10240, 'github.commits.json'
        if os.path.exists(file_):
            prev_cnt = json.load(open(file_, 'r'))['count']
        json.dump({'count': cnt}, open(file_, 'w'), indent=2)

        if cnt > prev_cnt: return

        msg = (
            'Github commit reminder \n\n' +
            f"You haven't do any commit today. Your previous commit count is {cnt}"
        )
        bot_messalert(msg)

    @classmethod
    def tasks_reminder(cls):
        url = decode('GIT_RAW_PREFIX') + '2021/ps.md'

        tasks = cls._request_proxy_get(url).split('\n')
        todo = '\n'.join(t for t in tasks if not t.startswith('- [x]'))
        bot_messalert('TODO list \n' + todo)

    @classmethod
    def _request_proxy_get(cls, url: str) -> str:
        px = decode('http_proxy').lstrip('http://')
        for _ in range(5):
            try:
                res = requests.get(url,
                                   proxies={'https': px},
                                   headers={'User-Agent': 'Aha'},
                                   timeout=3)
                if res.status_code == 200:
                    return res.text
            except Exception as e:
                print(e)
        else:
            return ''

    @classmethod
    def _count_commits(cls) -> int:
        resp = cls._request_proxy_get(decode('GITHUB_MAINPAGE'))
        if resp:
            soup = bs4.BeautifulSoup(resp, 'lxml')
            h2 = soup.find_all('h2', {'class': 'f4 text-normal mb-2'}).pop()
            commits_count = next(
                int(e) for e in h2.text.split() if e.isdigit())
            return commits_count
        return 0


class HappyXiao:
    ''' happyxiao articles poster'''
    @classmethod
    def rss(cls, url: str = 'https://happyxiao.com/') -> None:
        rsp = bs4.BeautifulSoup(requests.get(url).text, 'lxml')
        more = rsp.find_all('a', attrs={'class': 'more-link'})
        articles = {m.attrs['href']: '' for m in more}
        jsonfile = 'hx.json'

        if not os.path.exists(jsonfile):
            open(jsonfile, 'w').write('{}')

        j = json.load(open(jsonfile, 'r'))
        res = '\n'.join(cls.brief(k) for k in articles.keys() if k not in j)
        j.update(articles)
        json.dump(j, open(jsonfile, 'w'), indent=2)
        if res:
            bot_messalert(res.replace('#', '%23'))

    @classmethod
    def brief(cls, url) -> str:
        rsp = bs4.BeautifulSoup(requests.get(url).text, 'lxml')
        art = rsp.find('article')
        res = url + '\n' + art.text.replace('\t', '') + str(art.a)
        return res

''' crontab tasks. '''
from .config import decode
from dofast.toolkits.telegram import YahooMail


def git_commit_reminder() -> None:
    import json, os
    cnt = get_commits()
    previous_cnt = 10240
    file_ = 'github.commits.json'
    if os.path.exists(file_):
        previous_cnt = json.load(open(file_, 'r'))['count']
    json.dump({'count': cnt}, open(file_, 'w'), indent=2)

    if cnt > previous_cnt: return

    msg = f"You haven't do any commit today. Your previous commit count is {cnt}"
    YahooMail().send(decode('GMAIL2'),
                     subject="Github commit reminder",
                     message=msg)


def tasks_reminder():
    url = decode('GIT_RAW_PREFIX') + '2021/ps.md'

    tasks = _request_proxy_get(url).split('\n')
    todo = '\n'.join(t for t in tasks if not t.startswith('- [x]'))
    YahooMail().send(decode('GMAIL2'), subject="TODO list", message=todo)


def _request_proxy_get(url: str) -> str:
    import requests
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


def get_commits() -> int:
    import bs4
    resp = _request_proxy_get(decode('GITHUB_MAINPAGE'))
    if not resp: return
    soup = bs4.BeautifulSoup(resp, 'lxml')
    h2 = soup.find_all('h2', {'class': 'f4 text-normal mb-2'}).pop()
    commits_count = next(int(e) for e in h2.text.split() if e.isdigit())
    return commits_count

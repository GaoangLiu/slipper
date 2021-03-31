''' crontab tasks. '''
from .config import decode


def get_commits() -> int:
    import requests, bs4
    resp = requests.get(decode('GITHUB_MAINPAGE'))
    soup = bs4.BeautifulSoup(resp.text, 'lxml')
    h2 = soup.find_all('h2', {'class': 'f4 text-normal mb-2'}).pop()
    commits_count = next(int(e) for e in h2.text.split() if e.isdigit())
    return commits_count


def git_commit_reminder() -> None:
    import json, os
    cnt = get_commits()
    previous_cnt = 10240
    file_ = 'github.commits.json'
    if os.path.exists(file_):
        previous_cnt = json.load(open(file_, 'r'))['count']
    json.dump({'count': cnt}, open(file_, 'w'), indent=2)

    if cnt > previous_cnt: return

    from dofast.toolkits.telegram import YahooMail
    msg = f"You haven't do any commit today. Your previous commit count is {cnt}"
    YahooMail().send(decode('GMAIL2'),
                     subject="Github commit reminder",
                     message=msg)


def tasks_reminder():
    url = decode('GIT_RAW_PREFIX') + '2021/ps.md'
    
    import requests
    tasks = requests.get(url).text.split('\n')
    todo = '\n'.join(t for t in tasks if not t.startswith('- [x]'))

    from dofast.toolkits.telegram import YahooMail
    YahooMail().send(decode('GMAIL2'), subject="TODO list", message=todo)

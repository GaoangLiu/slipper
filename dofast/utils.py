# coding:utf-8
import base64
import bs4
import json
import os
import requests
import subprocess
import sys
import time
from functools import wraps
from typing import List
from pprint import pprint
from tqdm import tqdm

from .logger import Logger
from .config import decode
import codefast as cf

# =========================================================== display
def sleep(countdown: int) -> None:
    time.sleep(countdown)


def random_sleep(lower_bound: int, upper_bound: int) -> None:
    """Randomly sleep for few seconds. Typical usage involving a crontab task
    to prevent robot behavior detection.
    """
    import random
    time.sleep(random.randint(lower_bound, upper_bound))


# =========================================================== IO
def show_func_name():
    cf.say(f"\n--------------- {sys._getframe(1).f_code.co_name} ---------------")


def smartopen(file_path: str):
    import smart_open
    with smart_open.open(file_path) as f:
        return f.readlines()


def info(msg):
    Logger().info(msg)


def debug(msg):
    Logger().debug(msg)


def warning(msg):
    Logger().warning(msg)


def error(msg):
    Logger().error(msg)


def critical(msg):
    Logger().critical(msg)


def shell(cmd: str, print_str: bool = False) -> str:
    ret_str = ''
    try:
        ret_str = subprocess.check_output(cmd,
                                          stderr=subprocess.STDOUT,
                                          shell=True).decode('utf8')
    except Exception as e:
        print(e)
    finally:
        if print_str:
            cf.say(ret_str)
        return ret_str


def jsonread(file_name: str) -> dict:
    res = {}
    with open(file_name, 'r') as f:
        res = json.loads(f.read())
    return res


def textread(file_name: str) -> List:
    return [l.strip() for l in open(file_name, 'r').readlines()]


def textwrite(cons: str, file_name: str) -> List:
    with open(file_name, 'w') as f:
        f.write(cons)


def jsonwrite(d: dict, file_name: str):
    json.dump(d, open(file_name, 'w'), ensure_ascii=False, indent=2)


def create_random_file(size: int = 100):  # Default 100M
    _file = 'cc.txt'
    open(_file, 'w').write("")
    print(f">> Create {_file} of size {size} MB")
    logfile = '/tmp/ddfile.txt'
    if io.exists(logfile):
        for f in io.read(logfile):
            cf.info('removing previous file', f)
            io.rm(f)

    with open(_file, 'ab') as fout:
        cc_dir = os.path.join(io.pwd().rstrip(), _file)
        io.write([cc_dir], logfile)
        for _ in tqdm(range(size)):
            fout.write(os.urandom(1024 * 1024))


def pip_install(package_name: str):
    # Install a package via subprocess
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", package_name])


def rounded_corners(image_name: str, rad: int = -1):
    """Add rounded_corners to images"""
    from PIL import Image, ImageDraw
    im = Image.open(image_name)
    w, h = im.size
    if rad < 0:
        rad = int(w * 0.02)
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, "white")
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    import uuid
    export_name = f'{uuid.uuid4()}.png'
    print(f'Export to {export_name}')
    im.save(export_name)
    return im


def download(url: str, proxy=None, name=None, referer=None):
    if not name:
        name = url.split('/').pop()
    if proxy:
        proxy = {'http': proxy}
    headers_ = {'referer': referer}
    response = client.get(url, stream=True, proxies=proxy, headers=headers_)
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024  # 8 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)

    with open(name, 'wb') as f:
        for chunk in response.iter_content(block_size):
            progress_bar.update(len(chunk))
            f.write(chunk)
    progress_bar.close()


# =========================================================== Decorator
def set_timeout(countdown: int, callback=print):
    def decorator(func):
        def handle(signum, frame):
            raise RuntimeError

        def wrapper(*args, **kwargs):
            import signal
            try:
                signal.signal(signal.SIGALRM, handle)
                signal.alarm(countdown)  # set countdown
                r = func(*args, **kwargs)
                signal.alarm(0)  # close alarm
                return r
            except RuntimeError as e:
                print(e)
                callback()

        return wrapper

    return decorator


def timethis(func):
    '''
    Decorator that reports the execution time.
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, end - start)
        return result

    return wrapper


def logged(logger_func, name=None, message=None):
    """
    Add logging to a function. name is the logger name, and message is the
    log message. If name and message aren't specified,
    they default to the function's module and name.
    """
    import logging

    def decorate(func):
        logname = name if name else func.__module__
        log = logging.getLogger(logname)
        logmsg = message if message else func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            logger_func(logmsg)
            return func(*args, **kwargs)

        return wrapper

    return decorate


# =========================================================== Global var
client = requests.Session()


# =========================================================== media
def smms_upload(file_path: str) -> dict:
    """Upload image to image server sm.ms"""
    url = "https://sm.ms/api/v2/upload"
    data = {'smfile': open(file_path, 'rb')}
    res = requests.Session().post(
        url, files=data, headers=jsonread('/usr/local/info/smms.json'))
    j = json.loads(res.text)
    try:
        info(j['data']['url'])
    except Exception as e:
        error(f"Exception {j}")
        info(j['images'])  # Already uploaded
        raise Exception(str(e))
    finally:
        return j


# =========================================================== Network
def git_io_shorten(url):
    res = client.post('https://git.io/create', data={'url': url})
    return f'http://git.io/{res.text}'


def githup_upload(file_name: str, shorten=True):
    from github import Github, InputGitTreeElement

    _token = decode('GIT_TOKEN')
    g = Github(_token, timeout=300)
    repo = g.get_user().get_repo('stuff')
    data = base64.b64encode(open(file_name, "rb").read())
    blob = repo.create_git_blob(data.decode("utf-8"), "base64")
    path = f'2021/{file_name}'
    element = InputGitTreeElement(path=path,
                                  mode='100644',
                                  type='blob',
                                  sha=blob.sha)
    element_list = list()
    element_list.append(element)

    master_ref = repo.get_git_ref('heads/master')
    master_sha = master_ref.object.sha
    base_tree = repo.get_git_tree(master_sha)
    tree = repo.create_git_tree(element_list, base_tree)
    parent = repo.get_git_commit(master_sha)
    commit = repo.create_git_commit(f"Uploading {file_name }", tree, [parent])
    master_ref.edit(commit.sha)

    if shorten:
        url_long = f"{decode('GIT_RAW_PREFIX')}{path}"
        print("Long url:  ", url_long)
        print("Short url: ", git_io_shorten(url_long))


class YouDao():
    def _get_header(self):
        headers = {}
        headers[
            "User-Agent"] = "Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 unicom{version:iphone_c@6.002}"
        headers[
            "Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        return headers

    def search_word(self, kw='novice'):
        s = requests.Session()
        url = 'http://dict.youdao.com/w/{}'.format('%20'.join(kw.split()))
        res = s.get(url, headers=self._get_header())
        soup = bs4.BeautifulSoup(res.text, 'lxml')

        trans = soup.findAll('div', class_='trans-container')

        if len(trans) == 0:
            print("**Sorry, but no translation was found.**")
            return
        """ Chinese to English """
        import string
        for span in soup.findAll('span', class_='contentTitle'):
            if kw[0] in string.ascii_lowercase:  # Only print this for Chinese word
                continue

            trans = span.text.replace(";", '').strip()
            if trans[-1] in string.ascii_lowercase:
                print(trans)
        """ English to Chinese """
        ul = soup.findAll('ul')[1]
        for li in ul.findAll('li'):
            print('\t{}'.format(li.text))

        import re
        for div in soup.findAll('div',
                                {'class': {'examples', 'collinsMajorTrans'}}):
            # print(div.text)
            con = re.sub(r'(\s+)', ' ', div.text.strip())
            print('\t{}'.format(con))
            if div.attrs['class'][0] == 'examples':
                print('')


def youdao_dict(word: str):
    YouDao().search_word(word)


# =========================================================== Search
def findfile(regex: str, dir: str = "."):
    for relpath, _, files in os.walk(dir):
        for f in files:
            if regex in f:
                full_path = os.path.join(dir, relpath, f)
                print(os.path.normpath(os.path.abspath(full_path)))

# coding:utf-8
import os
import sys
import json
import time
import signal
import argparse
import requests
import subprocess
import base64
from github import Github
from github import InputGitTreeElement
from typing import List
from pprint import pprint
from logger import Logger
from tqdm import tqdm
from PIL import Image, ImageDraw


# =========================================================== display
def p(*s):
    for i in s:
        print(i)


def pp(d: dict):
    pprint(d)


def sleep(countdown: int):
    time.sleep(countdown)


# =========================================================== IO
def shell(cmd: str) -> str:
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT,
                                   shell=True).decode('utf8')


def jsonread(file_name: str) -> dict:
    res = {}
    with open(file_name, 'r') as f:
        res = json.loads(f.read())
    return res


def jsonwrite(d: dict, file_name: str):
    json.dump(d, open(file_name, 'w'), ensure_ascii=False, indent=2)


def create_random_file(size: int = 100):  # Default 100M
    _file = 'sample.txt'
    open(_file, 'w').write("")
    print(f">> Create {_file} of size {size} MB")

    with open(_file, 'ab') as fout:
        for _ in tqdm(range(size)):
            fout.write(os.urandom(1024 * 1024))


def pip_install(package_name: str):
    # Install a package via subprocess
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", package_name])


def rounded_corners(image_name: str, rad: int = 20):
    """Add rounded_corners to images"""
    im = Image.open(image_name)
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, "white")
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    im.save("out.png")
    return im


# =========================================================== Decorator
def set_timeout(countdown: int, callback=print):
    def decorator(func):
        def handle(signum, frame):
            raise RuntimeError

        def wrapper(*args, **kwargs):
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


# =========================================================== Global var
logger = Logger()
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
        logger.info(j['data']['url'])
    except Exception as e:
        logger.error(f"Exception {j}")
        logger.info(j['images'])  # Already uploaded
        raise Exception(str(e))
    finally:
        return j


# =========================================================== Network
def git_io_shorten(
    url='https://raw.githubusercontent.com/drocat/stuff/master/2021/medicine2.png'
):
    res = client.post('https://git.io/create', data={'url': url})
    return f'http://git.io/{res.text}'


def githup_upload(file_name: str):
    _token = "3654301e73ef4c5ccaffcd724af73c6bfc805048"
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

    long = f"https://raw.githubusercontent.com/drocat/stuff/master/{path}"
    p("Long url", long)
    p("Short url", git_io_shorten(long))

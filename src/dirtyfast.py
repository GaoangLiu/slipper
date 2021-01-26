# coding:utf-8
import os
import sys
import json
import time
import signal
import argparse
import requests
import subprocess
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
logger = Logger('/tmp/log.sli.log')


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
class Request:
    client = requests.Session()

# coding:utf-8
import os
import sys
import json
import time
import signal
from typing import List
from pprint import pprint
from logger import Logger
from tqdm import tqdm
import argparse


# =========================================================== display
def p(s):
    print(s)


def pp(d: dict):
    pprint(d)


def sleep(countdown: int):
    time.sleep(countdown)


# =========================================================== IO
logger = Logger()


def jsonread(file_name: str) -> dict:
    res = {}
    with open(file_name, 'r') as f:
        res = json.loads(f.read())
    return res


def jsonwrite(d: dict, file_name: str):
    json.dump(d, open(file_name, 'w'), ensure_ascii=False, indent=2)


def create_random_file(size: int = 100):  # Default 100M
    open('sample.txt', 'w').write("")
    print(f">> Create sample.txt of size {size} MB")

    with open('sample.txt', 'ab') as fout:
        for _ in tqdm(range(size)):
            fout.write(os.urandom(1024 * 1024))


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


# =========================================================== entry_point
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--ddfile", help="Create a file with os.urandom")
    args = parser.parse_args()
    if args.ddfile:
        create_random_file(int(args.ddfile))

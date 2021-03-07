import os, sys
import json
import base64
import tempfile
from Crypto.Cipher import AES

import oss2
from getpass import getpass
from dofast.config import ALIYUN_ACCESS_KEY_ID, ALIYUN_ACCESS_KEY_SECRET, ALIYUN_BUCKET, ALIYUN_REGION, PHRASE
from dofast.utils import shell, textwrite, textread
from tqdm import tqdm

from .toolkits.file import load_password


def encode(msg_text: str, passphrase: str) -> str:
    msg_text += '|' + msg_text * 100
    msg_text = msg_text[:1024]
    bytes_text = msg_text.encode().rjust(1024)  # in case this is a long text
    passphrase = passphrase.encode().ljust(32, b'*')
    cipher = AES.new(passphrase, AES.MODE_ECB)
    return base64.b64encode(cipher.encrypt(bytes_text)).decode('ascii')


def decode(msg_text: str, passphrase: str) -> str:
    bytes_text = msg_text.encode().ljust(1024)
    passphrase = passphrase.encode().ljust(32, b'*')
    try:
        cipher = AES.new(passphrase, AES.MODE_ECB)
        return cipher.decrypt(
            base64.b64decode(bytes_text)).decode().split('|')[0]
    except Exception as e:
        print(f"Maybe wrong password. {e}")
        return ""


class Bucket:
    def __init__(self, phrase: str = None):
        _passphrase = load_password('/etc/bucket.key')
        _id = decode(ALIYUN_ACCESS_KEY_ID, _passphrase)
        _secret = decode(ALIYUN_ACCESS_KEY_SECRET, _passphrase)
        _region = decode(ALIYUN_REGION, _passphrase)
        _bucket_name = decode(ALIYUN_BUCKET, _passphrase)
        _auth = oss2.Auth(_id, _secret)
        _service = oss2.Service(_auth, _region)
        _http_region = _region.lstrip('http://')

        self.bucket = oss2.Bucket(_auth, _region, _bucket_name)
        self.url_prefix = f"https://{_bucket_name}.{_http_region}/transfer/"

    def upload(self, file_name) -> None:
        """Upload a file to transfer/"""
        file_size = os.path.getsize(file_name)
        chuck = file_size // 100
        sys.stdout.write("[%s 🍄" % (" " * 100))
        sys.stdout.flush()
        sys.stdout.write("\b" * (101))  # return to start of line, after '['

        def progress_bar(*args):
            acc = args[0]
            ratio = lambda n: n * 100 // args[1]
            if ratio(acc + 8192) > ratio(acc):
                sys.stdout.write(str(ratio(acc) // 10))
                sys.stdout.flush()

        object_name = 'transfer/' + file_name.split('/')[-1]
        self.bucket.put_object_from_file(object_name,
                                         file_name,
                                         progress_callback=progress_bar)
        sys.stdout.write("]\n")  # this ends the progress bar
        print(f"✅ {file_name} uploaded to transfer/")

    def download(self, file_name) -> None:
        """Download a file from transfer/"""
        self.bucket.get_object_to_file(f"transfer/{file_name}",
                                       file_name.split('/')[-1])
        print(f"✅ {file_name} Downloaded.")

    def delete(self, file_name: str) -> None:
        """Delete a file from transfer/"""
        self.bucket.delete_object(f"transfer/{file_name}")
        print(f"✅ {file_name} deleted from transfer/")

    def list_files(self, prefix="transfer/") -> None:
        for obj in oss2.ObjectIterator(self.bucket, prefix=prefix):
            print(obj.key)


class Message():
    def __init__(self):
        self._passphrase = decode(PHRASE, load_password('/etc/slimsg.key'))
        self.bucket = Bucket(self._passphrase).bucket
        self.file = 'transfer/msgbuffer.txt'
        self._tmp = '/tmp/msgbuffer.txt'

    def read(self) -> dict:
        self.bucket.get_object_to_file(self.file, self._tmp)
        conversations = textread(self._tmp)
        for line in conversations[-10:]:
            if not line: continue
            name, content = line.strip().split('⎮')
            sign = "🔥" if name == shell('whoami').strip() else "❄️ "
            print('{} {}'.format(sign, content))

    def write(self, msg_body: str):
        contents = shell('whoami').strip() + "⎮" + msg_body
        info = self.bucket.head_object(self.file)
        loc = info.content_length
        resp = self.bucket.append_object(self.file, loc, "\n" + contents)
        if resp.status == 200:
            print("✔ Message Sent!")

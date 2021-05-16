import sys

import oss2
import codefast as cf
from .config import decode
from .utils import shell, download


class Bucket:
    def __init__(self, phrase: str = None):
        _id = decode("ALIYUN_ACCESS_KEY_ID")
        _secret = decode("ALIYUN_ACCESS_KEY_SECRET")
        _bucket = decode("ALIYUN_BUCKET")
        _region = decode("ALIYUN_REGION")
        _auth = oss2.Auth(_id, _secret)
        _http_region = _region.lstrip('http://')

        self.bucket = oss2.Bucket(_auth, _region, _bucket)
        self.url_prefix = f"https://{_bucket}.{_http_region}/transfer/"

    def upload(self, file_name: str) -> None:
        """Upload a file to transfer/"""
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

    def download(self, file_name: str) -> None:
        """Download a file from transfer/"""
        self.bucket.get_object_to_file(f"transfer/{file_name}",
                                       file_name.split('/')[-1])
        cf.logger.info(f"✅ {file_name} Downloaded.")

    def delete(self, file_name: str) -> None:
        """Delete a file from transfer/"""
        self.bucket.delete_object(f"transfer/{file_name}")
        cf.logger.info(f"✅ {file_name} deleted from transfer/")

    def list_files(self, prefix="transfer/") -> None:
        for obj in oss2.ObjectIterator(self.bucket, prefix=prefix):
            print(obj.key)


class FastOSS:
    CLIEND = Bucket()

    @classmethod
    def upload(cls, path: str) -> None:
        cls.CLIEND.upload(path)

    @classmethod
    def download(cls, file_name: str, export_name: str = None) -> None:
        prefix = cls.CLIEND.url_prefix
        download(prefix + file_name,
                 referer=prefix.strip('/transfer/'),
                 name=export_name)


class Message():
    def __init__(self):
        self.bucket = Bucket().bucket
        self.file = 'transfer/msgbuffer.json'
        self._tmp = '/tmp/msgbuffer.json'
        self.bucket.get_object_to_file(self.file, self._tmp)
        self.conversations = cf.json.read(self._tmp)

    def read(self, top: int = 10) -> dict:
        for conv in self.conversations['msg'][-top:]:
            name, content = conv['name'], conv['content']
            sign = "🔥" if name == shell('whoami').strip() else "❄️ "
            print('{} {}'.format(sign, content))

    def write(self, msg_body: str):
        name = shell('whoami').strip()
        content = msg_body
        self.conversations['msg'].append({'name': name, 'content': content})
        cf.json.write(self.conversations, self._tmp)
        resp = Bucket().upload(self._tmp)

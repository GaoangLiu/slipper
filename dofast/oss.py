import sys
import datetime

import codefast as cf
import oss2

from .config import decode
from .utils import download, shell
from .config import decode, fast_text_decode, fast_text_encode


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


class Bucket:
    def __init__(self):
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

        object_name = 'transfer/' + cf.io.basename(file_name)
        self.bucket.put_object_from_file(object_name,
                                         file_name,
                                         progress_callback=progress_bar)
        sys.stdout.write("]\n")  # this ends the progress bar
        cf.logger.info(f"{file_name} uploaded to transfer/")

    def _download(self, file_name: str, export_to: str = None) -> None:
        """Download a file from transfer/"""
        f = export_to if export_to else cf.io.basename(file_name)
        self.bucket.get_object_to_file(f"transfer/{file_name}", f)
        cf.logger.info(f"{file_name} Downloaded.")

    def download(self, remote_file_name: str, local_file_name: str) -> None:
        from .utils import download as _dw
        _dw(self.url_prefix + remote_file_name,
            referer=self.url_prefix.strip('/transfer/'),
            name=local_file_name)

    def download_decode(self, remote_file_name) -> str:
        '''Download encrypted file, read content and return decoded string'''
        self.download(cf.io.basename(remote_file_name), '/tmp/tmp')
        return fast_text_decode(cf.io.read('/tmp/tmp', ''))

    def upload_encode(self, local_file_name) -> None:
        '''Read local content, encode and upload it'''
        _con = cf.io.read(local_file_name, 'r')
        cf.io.write(fast_text_encode(_con), f'/tmp/{local_file_name}')
        self.upload(f'/tmp/{local_file_name}')

    def delete(self, file_name: str) -> None:
        """Delete a file from transfer/"""
        self.bucket.delete_object(f"transfer/{file_name}")
        cf.logger.info(f"{file_name} deleted from transfer/")

    def _get_files(self, prefix="transfer/") -> list:
        res = []
        for obj in oss2.ObjectIterator(self.bucket, prefix=prefix):
            res.append((obj.key, obj.last_modified, obj.size))
        return res

    def list_files(self, prefix="transfer/") -> None:
        files = self._get_files(prefix)
        files.sort(key=lambda e: e[1])
        for tp in files:
            print("{:<25} {:<10} {:<20}".format(
                str(datetime.datetime.fromtimestamp(tp[1])), sizeof_fmt(tp[2]),
                tp[0]))

    def list_files_by_size(self, prefix="transfer/") -> None:
        files = self._get_files(prefix)
        files.sort(key=lambda e: e[2])
        for tp in files:
            print("{:<25} {:<10} {:<20}".format(
                str(datetime.datetime.fromtimestamp(tp[1])), sizeof_fmt(tp[2]),
                tp[0]))

    def __repr__(self) -> str:
        return '\n'.join('{:<20} {:<10}'.format(str(k), str(v))
                         for k, v in vars(self).items())


class Message(Bucket):
    def __init__(self):
        super(Message, self).__init__()
        self.file = 'transfer/msgbuffer.json'
        self._tmp = '/tmp/msgbuffer.json'
        self.bucket.get_object_to_file(self.file, self._tmp)
        self.conversations = cf.json.read(self._tmp)

    def read(self, top: int = 10) -> dict:
        for conv in self.conversations['msg'][-top:]:
            name, content = conv['name'], conv['content']
            sign = "🔥" if name == shell('whoami').strip() else "❄️ "
            print('{} {}'.format(sign, content))

    def write(self, content: str) -> None:
        name = shell('whoami').strip()
        self.conversations['msg'].append({'name': name, 'content': content})
        cf.json.write(self.conversations, self._tmp)
        self.upload(self._tmp)

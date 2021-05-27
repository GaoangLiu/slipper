import sys

import codefast as cf
import oss2

from .config import decode
from .utils import download, shell


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

        object_name = 'transfer/' + cf.file.basename(file_name)
        self.bucket.put_object_from_file(object_name,
                                         file_name,
                                         progress_callback=progress_bar)
        sys.stdout.write("]\n")  # this ends the progress bar
        cf.logger.info(f"{file_name} uploaded to transfer/")

    def download(self, file_name: str, export_to:str=None) -> None:
        """Download a file from transfer/"""
        f = export_to if export_to else cf.file.basename(file_name)
        self.bucket.get_object_to_file(f"transfer/{file_name}", f)
        cf.logger.info(f"{file_name} Downloaded.")

    def delete(self, file_name: str) -> None:
        """Delete a file from transfer/"""
        self.bucket.delete_object(f"transfer/{file_name}")
        cf.logger.info(f"{file_name} deleted from transfer/")

    def list_files(self, prefix="transfer/") -> None:
        for obj in oss2.ObjectIterator(self.bucket, prefix=prefix):
            print(obj.key)
    
    def __repr__(self)->str:
        return '\n'.join(f'{k:<10} {v:<10}' for k, v in self.__dict__.items())



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

    def write(self, content: str)-> None:
        name = shell('whoami').strip()
        self.conversations['msg'].append({'name': name, 'content': content})
        cf.json.write(self.conversations, self._tmp)
        self.upload(self._tmp)

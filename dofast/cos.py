""" Tencent COS API wrapper """
import sys

from typing import List
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from tqdm import tqdm

from .toolkits.endecode import decode_with_keyfile as dkey
from .config import TENCENT_SECRET_ID, TENCENT_SECRET_KEY, AUTH, HTTP_PROXY, HTTPS_PROXY, BUCKET


class COS:
    def __init__(self):
        _id = dkey(AUTH, TENCENT_SECRET_ID)
        _key = dkey(AUTH, TENCENT_SECRET_KEY)
        _proxies = {
            'http': dkey(AUTH, HTTP_PROXY),
            'https': dkey(AUTH, HTTP_PROXY)
        }
        self.bucket = dkey(AUTH, BUCKET)
        _config = CosConfig(Region='ap-beijing',
                            SecretId=_id,
                            SecretKey=_key,
                            Proxies=_proxies)
        self.client = CosS3Client(_config)

    def prefix(self) -> str:
        return f'https://{self.bucket}.cos.ap-beijing.myqcloud.com/'

    def list_buckets(self) -> dict:
        return self.client.list_buckets()

    def list_files(self, prefix: str = '') -> dict:
        """List all objects in a directory."""
        response = self.client.list_objects(Bucket=self.bucket, Prefix=prefix)
        for fh in response['Contents']:
            size = int(fh['Size'])
            unit = 'MB' if size > 1024 * 1024 else 'KB'
            size = size // 1024 / 1024 if size > 1024 * 1024 else size // 1024
            print("{:<50} {:<20} {} {}".format(fh['Key'], fh['LastModified'],
                                               size, unit))

    def write_content(self, content: str, remote_file: str) -> None:
        self.client.put_object(Bucket=self.bucket,
                               Body=content,
                               Key=remote_file,
                               StorageClass='STANDARD',
                               EnableMD5=False)

    def read_content(self, remote_file: str) -> str:
        response = self.client.get_object(Bucket=self.bucket, Key=remote_file)
        fp = response['Body'].get_raw_stream()
        return fp.read().decode('utf8')

    def upload_file(self, file_path: str, remote_path: str = '.') -> None:
        """Upload file to remove_path/ directory"""
        _file_name = file_path.split('/')[-1]
        response = self.client.upload_file(Bucket=self.bucket,
                                           LocalFilePath=file_path,
                                           Key=f'{remote_path}/{_file_name}',
                                           PartSize=1,
                                           MAXThread=20,
                                           EnableMD5=False)

    def download_file(self, remote_file_path: str,
                      local_file_path: str) -> None:
        response = self.client.get_object(
            Bucket=self.bucket,
            Key=remote_file_path,
        )

        with open(f"{local_file_path}","wb") as file, \
            tqdm(total=int(response['Content-Length']),
                                      unit='B',
                                      unit_scale=True,
                                      unit_divisor=1024) as pbar:
            for data in response['Body']._rt.iter_content(chunk_size=1024):
                pbar.update(len(data))
                file.write(data)

    def delete_file(self, file_path: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=file_path)

    def delete_multiple_files(self, file_path_list: List[str]) -> None:
        """Delete multiple files
        :param file_path_list: List, list of files to be deleted. 
        """
        _objects = [{'Key': fp} for fp in file_path_list]
        resp = self.client.delete_objects(Bucket=self.bucket,
                                          Delete={'Object': _objects})

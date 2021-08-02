import json

import codefast as cf
import nsq,sys

from .consumer import Consumer
from dofast.config import SERVER_HOST

cf.logger.level = 'info'
cf.info('Go.')


class SyncFileConsumer(Consumer):
    def __init__(self, topic: str, channel: str):

        nsq.Reader(message_handler=self.async_handler,
                   nsqd_tcp_addresses=[f'{SERVER_HOST}:4150'],
                   topic=topic,
                   channel=channel,
                   max_in_flight=10,
                   lookupd_poll_interval=3)

    def publish_message(self, message: dict):
        msg = json.loads(message.body)
        cf.info(msg)
        _uuid = msg['data']['uuid']
        if io.exists('/tmp/syncfile.json') and jsn('/tmp/syncfile.json')['uuid'] == _uuid:
            return 

        filename = msg['data']['filename']
        from dofast.oss import Bucket
        cf.info('Downloading:', filename)
        
        Bucket().download(filename, f'/tmp/{filename}')
        cf.info('Download completed:', filename)
        
        cf.utils.shell('unzip -P syncsync63 -d . -o /tmp/sync.zip')
        cf.info('File(s) unzipped.')


def daemon():
    channel_name=sys.argv[1] if len(sys.argv) >=2  else 'sync'
    SyncFileConsumer('file', channel_name).run()

if __name__ == '__main__':
    SyncFileConsumer('file', 'sync').run()

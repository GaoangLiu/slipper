import json
import os
import sys
import traceback
from abc import ABCMeta, abstractmethod
from threading import Thread

import codefast as cf
import nsq

cf.logger.level = 'info'
cf.info('start')


class Config:
    from pathlib import Path
    config_file = os.path.join(Path.home(), '.config/nsq.json')
    default_tcp = 'localhost:4150'
    TCP = jsn.read(config_file).get(
        'TCP', 'localhost:4150') if io.exists(config_file) else default_tcp


class ExcThread(Thread):
    def __init__(self, target, args, name=''):
        super(ExcThread, self).__init__(target=target, args=args, name=name)
        self.func = target
        self.args = args
        self.name = name
        self.exitcode = 0
        self.exception = None
        self.exc_traceback = ''

    def run(self):
        try:
            self.func(*self.args)
        except Exception as e:
            self.exitcode = 1
            self.exception = e
            cf.error(e)
            self.exc_traceback = ''.join(
                traceback.format_exception(*sys.exc_info()))


class Consumer(metaclass=ABCMeta):
    def __init__(self, topic: str, channel: str):
        nsq.Reader(message_handler=self.async_handler,
                   nsqd_tcp_addresses=[Config.TCP],
                   topic=topic,
                   channel=channel,
                   max_in_flight=10,
                   lookupd_poll_interval=3)

    def run(self):
        nsq.run()

    @abstractmethod
    def publish_message(self):
        ...

    def handler(self, message):
        self.publish_message(message)

    def async_handler(self, message):
        worker = ExcThread(target=self.handler, args=(message, ), name='abc')
        worker.start()
        worker.join()
        return True


class TestConsumer(Consumer):
    def publish_message(self, message: dict):
        cf.info(json.loads(message.body))
        cf.info(str(message), 'SUCCESS')
        return True


if __name__ == '__main__':
    TestConsumer('jsontopic', 'cccache').run()

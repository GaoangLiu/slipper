import json

import codefast as cf

from dofast.security._hmac import certify_token
from dofast.toolkits.telegram import bot_messalert

from .consumer import Consumer
from .config import SALT

cf.logger.level = 'info'
cf.info('Go.')


class TelegramPostman(Consumer):
    def publish_message(self, message: dict):
        '''message demo: {'text': 'Hello, this is John from Ohio.', 'token': 'hmac token'} 
        '''
        msg = json.loads(message.body)
        key = io.read(SALT, '')

        if certify_token(key, msg.get('token')):
            cf.info('certify_token SUCCESS')
            if msg.get('text') is not None:
                bot_messalert(msg.get('text'))
        else:
            cf.warning('certify_token FAILED')


def daemon():
    TelegramPostman('web', 'postman').run()


if __name__ == '__main__':
    TelegramPostman().run()

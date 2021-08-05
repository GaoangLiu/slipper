import codefast as cf
from flask import Flask, request

from dofast.security._hmac import certify_token
from dofast.toolkits.telegram import bot_messalert

from .config import SALT
from .network import Twitter

app = Flask(__name__)


def run_task(msg: dict, func):
    key = io.read(SALT, '')
    if certify_token(key, msg.get('token')):
        cf.info('certify_token SUCCESS')
        content = msg.get('text')
        if content is not None:
            func(content)
            return 'SUCCESS'
    else:
        return 'FAILED'


@app.route('/tweet', methods=['GET', 'POST'])
def tweet():
    msg = request.get_json()
    key = io.read(SALT, '')
    if not certify_token(key, msg.get('token')):
        return 'FAILED'

    text = cf.utils.decipher(key, msg.get('text'))
    media = [f'/tmp/{e}' for e in msg.get('media')]
    cf.info(f'Input tweet: {text} / ' + ''.join(media))
    Twitter().post([text] + media)
    return 'SUCCESS'


@app.route('/messalert', methods=['GET', 'POST'])
def msg():
    msg = request.get_json()
    try:
        return run_task(msg, bot_messalert)
    except Exception as e:
        cf.error(str(e))
        return 'FAILED'


@app.route('/nsq', methods=['GET', 'POST'])
def nsq():
    msg = request.get_json()
    key = cf.io.reads(SALT)
    if not certify_token(key, msg.get('token')):
        return 'FAILED'
    topic = msg.get('topic')
    channel = msg.get('channel')
    data = msg.get('data')
    cf.net.post(f'http://127.0.0.1:4151/pub?topic={topic}&channel={channel}',
                json={'data': data})
    print(topic, channel, data)
    return 'SUCCESS'


@app.route('/')
def hello_world():
    return 'SUCCESS!'


def run():
    app.run(host='0.0.0.0', port=6363)


if __name__ == '__main__':
    run()

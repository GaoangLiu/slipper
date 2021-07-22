import codefast as cf
from flask import Flask, request

from dofast.security._hmac import certify_token
from dofast.toolkits.telegram import bot_messalert

app = Flask(__name__)


@app.route('/messalert', methods=['GET', 'POST'])
def msg():
    msg = request.get_json()
    key = io.read('/etc/auth.key', '')
    try:
        if certify_token(key, msg.get('token')):
            cf.info('certify_token SUCCESS')
            content = msg.get('text')
            if content is not None:
                bot_messalert(content)
                return 'SUCCESS'
        else:
            return 'FAILED'
    except Exception as e:
        cf.error(str(e))
        return 'FAILED'


@app.route('/')
def hello_world():
    return 'SUCCESS!'


def run():
    app.run(host='0.0.0.0', port=6363)


if __name__ == '__main__':
    run()

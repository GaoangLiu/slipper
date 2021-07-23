import codefast as cf
from flask import Flask, request

from dofast.security._hmac import certify_token
from dofast.toolkits.telegram import bot_messalert
from .network import Twitter

app = Flask(__name__)

def run_task(msg:dict,func):
    key = io.read('/etc/auth.key', '')
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
    files = request.files.to_dict(flat=False)
    key = io.read('/etc/auth.key', '')
    if not certify_token(key, msg.get('token')):
        return 'FAILED'
    text = msg.get('text')
    for f in files:
        f.save(f'/tmp/{f.filename}')

    

@app.route('/messalert', methods=['GET', 'POST'])
def msg():
    msg = request.get_json()
    try:
        return run_task(msg, bot_messalert)
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

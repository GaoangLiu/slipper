import json
import os
import socketserver
import sys

import codefast as cf
from codefast.argparser import PLACEHOLDER

from .config import SALT, SERVER_HOST, fast_text_decode, fast_text_encode
from .network import (AutoProxy, Bookmark, CoinMarketCap,
                      CustomHTTPRequestHandler, Douban, ForgiveCurve,
                      InputMethod, LunarCalendar, Phone, Twitter, bitly)
from .oss import Bucket, Message
from .security._hmac import generate_token
from .utils import download as getfile
from .utils import shell


class DCT(dict):
    def __init__(self, data: dict):
        self.data = data

    def format_time(self, seconds: int) -> str:
        if seconds <= 60:
            return f'{seconds}s'
        elif seconds <= 3600:
            return f'{seconds // 60}m ' + self.format_time(seconds % 60)
        else:
            return f'{seconds // 3600}h ' + self.format_time(seconds % 3600)

    def __repr__(self):
        return '\n'.join('{:<10}: {:<10}'.format(p[0], p[1]) for p in (
            ('distance', self.data['distance']),
            ('eta', self.format_time(self.data['eta'])),
            ('station', self.data['stationLeft']))) + '\n'


def eta():
    url = 'http://www.bjbus.com/api/api_etartime.php?conditionstr=000000058454081-110100016116032&token=eyJhbGciOiJIUzI1NiIsIlR5cGUiOiJKd3QiLCJ0eXAiOiJKV1QifQ.eyJwYXNzd29yZCI6IjY0ODU5MTQzNSIsInVzZXJOYW1lIjoiYmpidXMiLCJleHAiOjE2MjcwOTkyMDB9.OQYkF6rC9jfgxoC5nXDjjv1nqDIv3KfXqol0ATdts9g'
    headers = {
        'Cookie':
        'PHPSESSID=e6a7785ab9fd771f201e91f1dbfec9e2; SERVERID=564a72c0a566803360ad8bcb09158728|1625665356|1625633922',
        'User-Agent':
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
    }
    res = cf.net.get(url, headers=headers).json()
    data = res['data'][0]['datas']['trip']
    data.sort(key=lambda e: e['distance'])

    for e in data:
        print(DCT(e))


def jsonify() -> dict:
    if len(sys.argv) <= 1:
        print('Usage: jsonify file_name (> export.json)')
        return
    jsf = sys.argv[1]
    assert io.exists(jsf)
    js = jsn.read(io.read(jsf, ''))
    js = json.dumps(js)
    print(js)


def nsq_sync():
    cli = Bucket()
    if len(sys.argv) > 1:
        cf.utils.shell('zip -r9 -P syncsync63 -FSr /tmp/sync.zip {}'.format(
            ' '.join(sys.argv[1:])))
        cf.info('Files zipped.')
        cli.upload('/tmp/sync.zip')
        token = generate_token(cf.io.reads(SALT), expire=5)
        _uuid = cf.utils.uuid(),
        jsn.write({'uuid': _uuid}, '/tmp/syncfile.json')
        js = {
            'token': token,
            'topic': 'file',
            'channel': 'sync',
            'uuid': _uuid,
            'data': {
                'uuid': _uuid,
                'filename': 'sync.zip'
            }
        }
        res = cf.net.post('http://a.ddot.cc:6363/nsq', json=js)
        cf.info('FileSync', res.text)


def _sync():
    cli = Bucket()
    if len(sys.argv) > 1:
        cf.utils.shell('zip -r9 -P syncsync63 -FSr /tmp/sync.zip {}'.format(
            ' '.join(sys.argv[1:])))
        cf.info('Files zipped.')
        cli.upload('/tmp/sync.zip')
    else:
        cli.download('sync.zip', '/tmp/sync.zip')
        cf.info('zip filed downloaded.')
        cf.utils.shell('unzip -P syncsync63 -o /tmp/sync.zip')


def _hint_wubi():
    if len(sys.argv) > 1:
        InputMethod().entry(sys.argv[1])


def secure_oss():
    sp = cf.argparser.ArgParser()
    sp.input('-u', '-upload')
    sp.input('-d', '-download')
    sp.parse()

    cli = Bucket()
    cf.utils.shell('mkdir -p /tmp/ossfiles/')

    if sp.upload:
        v = io.basename(sp.upload.value)
        cf.utils.shell(
            f'zip -r0 -P syncsync63 /tmp/ossfiles/{v} {sp.upload.value}')
        cli.upload(f'/tmp/ossfiles/{v}')

    elif sp.download:
        url_prefix = cli.url_prefix
        v = sp.download.value
        getfile(url_prefix + sp.download.value,
                name=f'/tmp/ossfiles/{v}',
                referer=url_prefix.strip('/transfer/'))
        cf.utils.shell(f'unzip -o -P syncsync63 /tmp/ossfiles/{v}')


def pxy():
    if len(sys.argv) == 1:
        print(shell("curl -s cip.cc"))
    else:
        port = sys.argv.pop()
        ip = 'localhost' if len(sys.argv) == 1 else sys.argv.pop()
        print("Checking on:", ip, port)
        curl_socks = f"curl -s --connect-timeout 5 --socks5 {ip}:{port} ipinfo.io"
        curl_http = f"curl -s --connect-timeout 5 --proxy {ip}:{port} ipinfo.io"
        res = shell(curl_socks)
        if res != '':
            print(res)
        else:
            print('FAILED(socks5 proxy check)')
            print(shell(curl_http))


def main():
    sp = cf.argparser.ArgParser()
    # PLACEHOLDER = cf.argparser.PLACEHOLDER
    sp.input('-cos',
             '--cos',
             sub_args=[["u", "up", "upload"], ["download", "d", "dw"],
                       ["l", "list"], ["del", "delete"]])
    sp.input('-oss',
             '--oss',
             sub_args=[["u", "up", "upload"], ["d", "dw", 'download'],
                       ["l", "list"], ["del", "delete"], ['size']])
    sp.input('-dw', '--download', sub_args=[['p', 'proxy']])
    sp.input('-d', '--ddfile')
    sp.input('-ip', '--ip', sub_args=[['p', 'port']], default_value="localhost")
    sp.input('-rc', '--roundcorner', sub_args=[['r', 'radius']])
    sp.input('-gu', '--githubupload')
    sp.input('-sm', '--smms')
    sp.input('-yd', '--youdao')
    sp.input('-fd', '--find', sub_args=[['dir', 'directory']])
    sp.input('-m', '--msg', sub_args=[['r', 'read'], ['w', 'write']])
    sp.input('-fund', '--fund', sub_args=[['ba', 'buyalert']])
    sp.input('-stock', '--stock')
    sp.input(
        '-aes',
        '--aes',
        sub_args=[['en', 'encode'], ['de', 'decode']],
        description=
        'AES encode/decode message. Usage: \n sli -aes msg -en password \n sli -aes encrypted_msg -de password\n'
    )

    sp.input('-gcr', '--githubcommitreminder')
    sp.input('-pf', '--phoneflow', sub_args=[['rest'], ['daily']])
    sp.input('-hx', '--happyxiao')
    sp.input('-tgbot', '--telegrambot')
    sp.input('-db', '--doubaninfo', description='Get douban film information.')
    sp.input(
        '-sync',
        '--sync',
        description='synchronize files. Usage: sli -sync file1 file2 file3')
    sp.input('-vpsinit', '--vpsinit', description='VPS environment initiation.')
    sp.input('-json',
             '--jsonify',
             sub_args=[['o', 'output']],
             description='jsonify single quoted string')
    sp.input('-tt', '-twitter', description='Twitter API.')
    sp.input(
        '-lunar',
        '-lunarcalendar',
        default_value="",
        description='Lunar calendar. Usage:\n sli -lc or sli -lc 2088-09-09.')
    sp.input('-fi', '-fileinfo', description='Get file meta information.')
    sp.input(
        '-st',
        '-securitytext',
        sub_args=[['-d', '-decode'], ['-o', '-output']],
        description=
        'Generate secirty text. Usage: \n sli -st input.txt -o output.txt \n sli -st input.txt -d -o m.txt'
    )

    sp.input(
        '-ap',
        '-autoproxy',
        sub_args=[['-a', '-add'], ['-d', '-delete']],
        description=
        'AutoProxy configuration. Usage:\n sli -ap google.com \n sli -ap -d google.com'
    )

    sp.input(
        '-coin',
        sub_args=[['-q', '-quote']],
        description='Coin Market API. Usage: \n sli -coin -q \n sli -coin -q btc'
    )

    sp.input('-bitly', description='Bitly shorten url.')
    sp.input('-http',
             '-httpserver',
             sub_args=[['p', 'port']],
             description='Simple HTTP server. Usage:\n sli -http -p 8899')

    sp.input('-uni', description='Unicom data flow usage.')
    sp.input(
        '-bm',
        '--bookmark',
        sub_args=[['a', 'add'], ['d', 'delete'], ['l', 'list'], ['o', 'open'],
                  ['reload']],
        description=
        'Make bookmark easier. Usage:\n sli -bm -o google \n sli -bm -a google https://google.com \n sli -bm -d google'
    )

    sp.input('-ebb',
             '-ebbinghaus',
             sub_args=[['r', 'repeat'], ['d', 'delete'], ['a', 'add'],
                       ['reminder']],
             description='\nEbbinghaus forgive curve in usage.')

    sp.input('-e2c', '-excel2csv', description='Extract sheets to CSVs')

    sp.parse()

    # ------------------------------------
    if sp.excel2csv:
        os.system('mkdir -p /tmp/excel/')
        cf.reader.Excel(sp.excel2csv.value).to_csv('/tmp/excel/')

    elif sp.ebbinghaus:
        fc = ForgiveCurve()
        if sp.ebbinghaus.add:
            fc.add_task(sp.ebbinghaus.add)
        elif sp.ebbinghaus.delete:
            fc.remove_task(sp.ebbinghaus.delete)
        elif sp.ebbinghaus.repeat:
            fc.repeat_task(sp.ebbinghaus.repeat)
        elif sp.ebbinghaus.reminder:
            fc.tg_reminder()
        else:
            fc.reminder()

    elif sp.bookmark:
        bm = Bookmark()
        if sp.bookmark.open:
            _key, url = sp.bookmark.open, 'http://google.com'
            matched = [(k, v) for k, v in bm.json.items() if _key in k]
            if len(matched) == 1:
                url = matched[0][1]

            elif len(matched) > 1:
                for i, pair in enumerate(matched):
                    print("{:<3} {:<10} {:<10}".format(i, pair[0], pair[1]))
                c = input('Pick one:')
                url = matched[int(c) % len(matched)][1]

            cmd = f'open "{url}"' if 'macos' in cf.os.platform(
            ) else f'xdg-open "{url}"'
            cf.shell(cmd)

        elif sp.bookmark.add:
            _args = sp.bookmark.add
            assert len(_args) == 2, 'Usage: sli -bm -a/-add keyword URL'
            bm.add(keyword=_args[0], url=_args[1])

        elif sp.bookmark.delete:
            _args = sp.bookmark.delete
            if _args.startswith('http'):
                bm.remove(url=_args)
            else:
                bm.remove(keyword=_args)

        elif sp.bookmark.reload:
            bm.reload()

        else:
            bm.list()

    elif sp.uni:
        Phone().unicom()

    elif sp.httpserver:
        port = 8899 if not sp.httpserver.port else int(sp.httpserver.port)
        Handler = CustomHTTPRequestHandler
        with socketserver.TCPServer(("", port), Handler) as httpd:
            cf.logger.info(f"serving at port {port}")
            httpd.serve_forever()

    elif sp.bitly:
        bitly(sp.bitly.value)

    elif sp.coin:
        cmc, _quote = CoinMarketCap(), sp.coin.quote
        if _quote:
            coins = ['BTC', 'ETC', 'ETH', 'SHIB'] if isinstance(
                _quote, dict) else [_quote]
            cmc.part_display(cmc.quote(coins))

    elif sp.autoproxy:
        if sp.autoproxy.delete:
            AutoProxy.delete(sp.autoproxy.delete)
        elif sp.autoproxy.add:
            AutoProxy.add(sp.autoproxy.add)

    elif sp.fileinfo:
        info = cf.io.info(sp.fileinfo.value)
        for key in ('bit_rate', 'channel_layout', 'channels',
                    'codec_tag_string', 'codec_long_name', 'codec_name',
                    'duration', 'filename', 'format_name', 'sample_rate',
                    'size', 'width'):
            print('{:<20} {}'.format(key, info.get(key, None)))

    elif sp.doubaninfo:
        Douban.query_film_info(sp.doubaninfo.value)

    elif sp.twitter:

        @cf.utils.retry()
        def post_status():
            text, media = '', []
            key = io.read(SALT, '')
            for e in sys.argv[2:]:
                if cf.io.exists(e):
                    if e.endswith(('.png', '.jpeg', '.jpg', '.mp4', '.gif')):
                        media.append(io.basename(e))
                        cf.net.post(f'http://{SERVER_HOST}:8899',
                                    files={'file': open(e, 'rb')})
                    elif e.endswith(('.txt', '.dat')):
                        text += cf.utils.cipher(key, io.read(e, ''))
                    else:
                        cf.warning("Unsupported media type", e)
                else:
                    text += cf.utils.cipher(key, e)
            res = cf.net.post(f'http://{SERVER_HOST}:6363/tweet',
                              json={
                                  'token': generate_token(key, expire=20),
                                  'text': text,
                                  'media': media
                              })
            print(res, res.text)
            assert res.text == 'SUCCESS', 'Webo post failed.'

        post_status()

    elif sp.tgbot:
        from .toolkits.telegram import messalert
        messalert(sp.tgbot.value)

    elif sp.happyxiao:
        from .crontasks import HappyXiao
        HappyXiao.rss()

    elif sp.phoneflow:
        from .crontasks import PapaPhone
        if sp.phoneflow.rest:
            PapaPhone.issue_recharge_message()
        elif sp.phoneflow.daily:
            PapaPhone.issue_daily_usage()

    elif sp.githubcommitreminder:
        from .crontasks import GithubTasks
        GithubTasks.git_commit_reminder()
        GithubTasks.tasks_reminder()

    elif sp.cos:
        from .cos import COS
        cli = COS()
        if sp.cos.upload:
            cli.upload_file(sp.cos.upload, "transfer/")
        elif sp.cos.download:
            _file = sp.cos.download
            cli.download_file(f"transfer/{_file}", _file)
        elif sp.cos.delete:
            cli.delete_file(f"transfer/{sp.cos.delete}")
        elif sp.cos.list:
            print(cli.prefix())
            cli.list_files("transfer/")

    elif sp.oss:
        cli = Bucket()
        if sp.oss.upload:
            cli.upload(sp.oss.upload)
        elif sp.oss.download:
            url_prefix = cli.url_prefix
            getfile(url_prefix + sp.oss.download,
                    referer=url_prefix.strip('/transfer/'))
        elif sp.oss.delete:
            cli.delete(sp.oss.delete)
        elif sp.oss.list:
            print(cli.url_prefix)
            if sp.oss.size:
                cli.list_files_by_size()
            else:
                cli.list_files()

    elif sp.sync:
        cli = Bucket()
        files: str = '|'.join(sys.argv[2:])
        if files:
            for f in sys.argv[2:]:
                cli.upload(f.strip())
            cf.json.write({'value': files}, '/tmp/syncsync.json')
            cli.upload('/tmp/syncsync.json')
        else:
            cli.download('syncsync.json')
            files = cf.json.read('syncsync.json')['value'].split('|')
            for f in files:
                getfile(cli.url_prefix + f,
                        referer=cli.url_prefix.strip('/transfer/'))
            os.remove('syncsync.json')

    elif sp.download:
        getfile(sp.download.value, proxy=sp.download.proxy)

    elif sp.ddfile:
        from .utils import create_random_file
        create_random_file(int(sp.ddfile.value or 100))

    elif sp.ip:
        v_ip, v_port = sp.ip.value, sp.ip.port
        from .utils import shell
        if not sp.ip.port:
            print(shell("curl -s cip.cc"))
        else:
            print("Checking on:", v_ip, v_port)
            curl_socks = f"curl -s --connect-timeout 5 --socks5 {v_ip}:{v_port} ipinfo.io"
            curl_http = f"curl -s --connect-timeout 5 --proxy {v_ip}:{v_port} ipinfo.io"
            res = shell(curl_socks)
            if res != '':
                print(res)
            else:
                print('FAILED(socks5 proxy check)')
                print(shell(curl_http))

    elif sp.json:
        jdict = cf.json.eval(sp.json.value)
        print(json.dumps(jdict))
        if sp.json.output:
            cf.json.write(jdict, sp.json.output)

    elif sp.roundcorner:
        from .utils import rounded_corners
        image_path, radius = sys.argv[2], -1
        if len(sys.argv) == 4:
            radius = int(sys.argv[3])
        elif len(sys.argv) == 5:
            radius = int(sys.argv[4])
        rounded_corners(image_path, radius)

    elif sp.githubupload:
        from .utils import githup_upload
        githup_upload(sp.githubupload.value)

    elif sp.smms:
        from .utils import smms_upload
        smms_upload(sp.smms.value)

    elif sp.youdao:
        from .utils import youdao_dict
        youdao_dict(sp.youdao.value)

    elif sp.find:
        from .utils import findfile
        print(sp.find.value, sp.find.directory or '.')
        findfile(sp.find.value, sp.find.directory or '.')

    elif sp.msg:
        if sp.msg.write:
            Message().write(sp.msg.write)
        elif sp.msg.read:
            top_ = 1 if sp.msg.read == {'value': ''} else int(sp.msg.read)
            Message().read(top=top_)     # show only 1 line
        elif sp.msg.value != PLACEHOLDER:
            Message().write(sp.msg.value)
        else:
            Message().read()

    elif sp.fund:
        from .fund import invest_advice, tgalert
        if sp.fund.buyalert: tgalert(sp.fund.buyalert)
        else:
            invest_advice(None if sp.fund.value ==
                          PLACEHOLDER else sp.fund.value)

    elif sp.stock:
        from .stock import Stock
        if sp.stock.value != PLACEHOLDER: Stock().trend(sp.stock.value)
        else: Stock().my_trend()

    elif sp.aes:
        from .toolkits.endecode import short_decode, short_encode

        text = sp.aes.value
        if sp.aes.encode: print(short_encode(text, sp.aes.encode))
        elif sp.aes.decode: print(short_decode(text, sp.aes.decode))

    elif sp.securitytext:
        text = sp.securitytext.value
        if cf.io.exists(text):
            text = cf.io.read(text, '')
        func = fast_text_decode if sp.securitytext.decode else fast_text_encode
        text_r = func(text)
        if sp.securitytext.output:
            cf.io.write(text_r, sp.securitytext.output)
            print('Text exported to {}'.format(sp.securitytext.output))
        else:
            print(text_r)

    elif sp.vpsinit:
        dirname: str = cf.io.dirname()
        text: str = cf.io.read(f"{dirname}/data/vps_init.sh")
        cf.io.write(text, 'config.sh')
        print('SUCCESS: config.sh copied in current directory.')

    elif sp.lunarcalendar:
        date: str = sp.lunarcalendar.value.replace('PLACEHOLDER', '')
        LunarCalendar.display(date)

    else:
        from .data.msg import display_message
        display_message()
        sp.help()
        done, total = sp._arg_counter, 50
        print('✶' * done + '﹆' * (total - done) + "({}/{})".format(done, total))


if __name__ == '__main__':
    main()

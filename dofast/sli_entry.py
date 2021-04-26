from .utils import jsonwrite, jsonread
from .utils import download as getfile


def _init_config() -> None:
    """ init configureation file on installing library."""
    from pathlib import Path
    _config_path = str(Path.home()) + "/.config/"
    _cf = _config_path + 'dofast.json'
    if Path(_cf).is_file(): return

    import os, inspect
    file_path = os.path.dirname(
        os.path.realpath(inspect.getfile(inspect.currentframe())))
    zip_json = f"{file_path}/dofast.json.zip"

    import zipfile, getpass
    with zipfile.ZipFile(zip_json, 'r') as zip_ref:
        zip_ref.extractall(path=_config_path,
                           pwd=bytes(
                               getpass.getpass("type here config password: "),
                               'utf-8'))


def main():
    _init_config()

    from .simple_parser import SimpleParser, PLACEHOLDER
    sp = SimpleParser()
    sp.input('-cos',
             '--cos',
             sub_args=[["u", "up", "upload"], ["download", "d", "dw"],
                       ["l", "list"], ["del", "delete"]])
    sp.input('-oss',
             '--oss',
             sub_args=[["u", "up", "upload"], ["download", "d", "dw"],
                       ["l", "list"], ["del", "delete"]])
    sp.input('-dw', '--download', sub_args=[])
    sp.input('-d', '--ddfile')
    sp.input('-ip',
             '--ip',
             sub_args=[['p', 'port']],
             default_value="localhost")
    sp.input('-rc', '--roundcorner', sub_args=[['r', 'radius']])
    sp.input('-gu', '--githubupload')
    sp.input('-sm', '--smms')
    sp.input('-yd', '--youdao')
    sp.input('-fd', '--find', sub_args=[['dir', 'directory']])
    sp.input('-m', '--msg', sub_args=[['r', 'read'], ['w', 'write']])
    sp.input('-fund', '--fund', sub_args=[['ba', 'buyalert']])
    sp.input('-stock', '--stock')
    sp.input('-aes', '--aes', sub_args=[['en', 'encode'], ['de', 'decode']])
    sp.input('-gcr', '--githubcommitreminder')
    sp.input('-pf', '--phoneflow', sub_args=[['rest'], ['daily']])
    sp.input('-hx', '--happyxiao')
    sp.input('-tgbot', '--telegrambot')
    sp.input('-sync', '--sync')
    sp.input('-vpsinit',
             '--vpsinit',
             description='VPS environment initiation.')

    sp.parse_args()
    if sp.tgbot:
        from .toolkits.telegram import bot_messalert
        bot_messalert(sp.tgbot.value)

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
        from .oss import Bucket, Message
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
            cli.list_files()

    elif sp.sync:
        from .oss import Bucket, Message
        import os
        cli = Bucket()
        if sp.sync.value != PLACEHOLDER:
            cli.upload(sp.sync.value)
            jsonwrite({'value': sp.sync.value}, '/tmp/syncsync.json')
            cli.upload('/tmp/syncsync.json')
        else:
            cli.download('syncsync.json')
            f = jsonread('syncsync.json')['value']
            getfile(cli.url_prefix + f,
                    referer=cli.url_prefix.strip('/transfer/'))
            os.remove('syncsync.json')

    elif sp.download:
        from .oss import Bucket
        getfile(sp.download.value,
                referer=Bucket().url_prefix.strip('/transfer/'))

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

    elif sp.roundcorner:
        from .utils import rounded_corners
        image_path = sp.roundcorner.value
        radius = int(sp.roundcorner.radius or 10)
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
        from .oss import Message
        if sp.msg.write:
            Message().write(sp.msg.write)
        elif sp.msg.read:
            Message().read()
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

    elif sp.vpsinit:
        from .utils import shell
        import os, inspect
        file_path = os.path.dirname(
            os.path.realpath(inspect.getfile(inspect.currentframe())))
        bash_file = f"{file_path}/data/vps_init.sh"
        shell(f'bash {bash_file}')

    else:
        from .data.msg import display_message
        display_message()


if __name__ == '__main__':
    main()

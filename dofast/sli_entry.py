import dofast.utils as du
from dofast.simple_parser import SimpleParser, PLACEHOLDER
from dofast.oss import Bucket, Message
from dofast.cos import COS
from dofast.fund import invest_advice, tgalert
from dofast.stock import Stock

from dofast.toolkits.endecode import short_decode, short_encode
from dofast.toolkits.telegram import read_hema_bot, download_file_by_id
from dofast.network import Network
from dofast.data.msg import display_message


def main():
    sp = SimpleParser()
    sp.add_argument('-cos',
                    '--cos',
                    sub_args=[["u", "up", "upload"], ["download", "d", "dw"],
                              ["l", "list"], ["del", "delete"]])
    sp.add_argument('-oss',
                    '--oss',
                    sub_args=[["u", "up", "upload"], ["download", "d", "dw"],
                              ["l", "list"], ["del", "delete"]])
    sp.add_argument('-dw', '--download', sub_args=[])
    sp.add_argument('-d', '--ddfile')
    sp.add_argument('-ip',
                    '--ip',
                    sub_args=[['p', 'port']],
                    default_value="localhost")
    sp.add_argument('-rc', '--roundcorner', sub_args=[['r', 'radius']])
    sp.add_argument('-gu', '--githubupload')
    sp.add_argument('-sm', '--smms')
    sp.add_argument('-yd', '--youdao')
    sp.add_argument('-fd', '--find', sub_args=[['dir', 'directory']])
    sp.add_argument('-m', '--msg', sub_args=[['r', 'read'], ['w', 'write']])
    sp.add_argument('-fund', '--fund', sub_args=[['ba', 'buyalert']])
    sp.add_argument('-stock', '--stock')
    sp.add_argument('-aes',
                    '--aes',
                    sub_args=[['en', 'encode'], ['de', 'decode']])

    sp.parse_args()

    if sp.cos:
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
            # Note the download func here is: dofast.utils.download
            du.download(cli.url_prefix + sp.oss.download)
        elif sp.oss.delete:
            cli.delete(sp.oss.delete)
        elif sp.oss.list:
            print(cli.url_prefix)
            cli.list_files()

    elif sp.download:
        print(sp.download)
        du.download(sp.download.value)

    elif sp.ddfile:
        du.create_random_file(int(sp.ddfile.value or 100))

    elif sp.ip:
        v_ip, v_port = sp.ip.value, sp.ip.port
        if not sp.ip.port:
            du.p(du.shell("curl -s cip.cc"))
        else:
            print("Checking on:", v_ip, v_port)
            curl_socks = f"curl -s --connect-timeout 5 --socks5 {v_ip}:{v_port} ipinfo.io"
            curl_http = f"curl -s --connect-timeout 5 --proxy {v_ip}:{v_port} ipinfo.io"
            res = du.shell(curl_socks)
            if res != '':
                du.p(res)
            else:
                du.p('FAILED(socks5 proxy check)')
                du.p(du.shell(curl_http))

    elif sp.roundcorner:
        image_path = sp.roundcorner.value
        radius = int(sp.roundcorner.radius or 10)
        du.rounded_corners(image_path, radius)

    elif sp.githubupload:
        du.githup_upload(sp.githubupload.value)

    elif sp.smms:
        du.smms_upload(sp.smms.value)

    elif sp.youdao:
        du.youdao_dict(sp.youdao.value)

    elif sp.find:
        print(sp.find.value, sp.find.directory or '.')
        du.findfile(sp.find.value, sp.find.directory or '.')

    elif sp.msg:
        if sp.msg.write:
            Message().write(sp.msg.write)
        elif sp.msg.read:
            Message().read()
        elif sp.msg.value != PLACEHOLDER:
            Message().write(sp.msg.value)
        else:
            Message().read()

    elif sp.fund:
        if sp.fund.buyalert: tgalert(sp.fund.buyalert)
        else:
            invest_advice(None if sp.fund.value ==
                          PLACEHOLDER else sp.fund.value)

    elif sp.stock:
        if sp.stock.value != PLACEHOLDER: Stock().trend(sp.stock.value)
        else: Stock().my_trend()

    elif sp.aes:
        text = sp.aes.value
        if sp.aes.encode: du.p(short_encode(text, sp.aes.encode))
        elif sp.aes.decode: du.p(short_decode(text, sp.aes.decode))

    else:
        display_message()


if __name__ == '__main__':
    main()

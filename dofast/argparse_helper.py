import argparse
import dofast.utils as du
from dofast.simple_parser import SimpleParser
from dofast.oss import Bucket, Message
from dofast.cos import COS
from dofast.fund import invest_advice, tgalert
from dofast.stock import Stock

from .toolkits.endecode import short_decode, short_encode
from .toolkits.telegram import read_hema_bot, download_file_by_id
from .network import Network

msg = """A Simple yet powerful terminal CLient. 😏

-dw, --download -p, --proxy [-r|-o](--rename) ::: Download file.
-d, --ddfile[size] ::: Create random file.
-ip [-p, --port]::: Curl cip.cc
-rc, --roundcorner [--radius] ::: Add rounded corner to images.
-gu, --githubupload ::: Upload files to GitHub.
-sm, --smms ::: Upload image to sm.ms image server.
-yd, --youdao ::: Youdao dict translation.
-fd, --find [-dir, --dir] ::: Find files from dir.

-oss [-u, --upload | -d, --download | -del, --delete] ::: Aliyun OSS manager
-cos [-u, --upload | -d, --download | -del, --delete] ::: COS file manager.

-m, --msg [-r, --write | -w, --write] ::: Messenger
-fund, --fund [fund_code] ::: Fund investment.
-stock, --stock [stock_code] ::: Stock trend.
-aes [-en | -de ] ::: AES encode/decode.
-hema [-id id ] ::: Read hema bot update / Download file by id
"""


def parse_arguments():
    sp = SimpleParser()
    sp.parse_args()

    if sp.has_attribute(['-dw', '--download'], excludes=['-oss']):
        sp.set_default('-p', 'http://cn.ddot.cc:51172')
        url = sp.fetch_value(['-dw'])
        proxy = sp.fetch_value(['-p', '--proxy'])
        name = sp.fetch_value(['-r', '-o', '--rename'])
        du.download(url, proxy, name)

    elif sp.has_attribute(['-d', '--dduile'], excludes=['-oss', '-cos']):
        size = sp.fetch_value(['-d', '--dduile'], 100)
        du.create_random_file(int(size))

    elif sp.has_attribute(['-ip']):
        if sp.has_attribute(['-p', '-port', '--port']):
            ip = sp.fetch_value(['-ip'], 'localhost')
            port = sp.fetch_value(['-p', '-port', '--port'], '80')
            if Network.is_good_proxy(f'{ip}:{port}'):
                curl_socks = f"curl -s --connect-timeout 3 --socks5 {ip}:{port} ipinfo.io"
                curl_http = f"curl -s --connect-timeout 3 --proxy {ip}:{port} ipinfo.io"
                res = du.shell(curl_socks)
                if res != '':
                    du.p(res)
                else:
                    du.p('FAILED(socks5 proxy check)')
                    du.p(du.shell(curl_http))
            else:
                print("Proxy invalid.")
        else:
            du.p(du.shell("curl -s cip.cc"))

    elif sp.has_attribute(['-rc', '--roundcorner']):
        image_path = sp.fetch_value(['-rc'])
        radius = int(sp.fetch_value(['--radius'], 10))
        du.rounded_corners(image_path, radius)

    elif sp.has_attribute(['-gu', '--githupupload']):
        du.githup_upload(sp.dict['-gu'].pop())

    elif sp.has_attribute(['-sm', '--smms']):
        du.smms_upload(sp.fetch_value(['-sm', '--smms']))

    elif sp.has_attribute(['-pac', '--updatepac']):
        url = sp.fetch_value(['-pac', '--updatepac'])
        du.update_pac(url)

    elif sp.has_attribute(['-yd', '--youdao']):
        du.youdao_dict(sp.fetch_value(['-yd', '--youdao'], 'Abandon'))

    elif sp.has_attribute(['-fd', '--find']):
        dir_ = sp.fetch_value(['-dir', '--dir'], ".")
        fname = sp.fetch_value(['-fd', '--find'])
        du.finduile(fname, dir_)

    elif sp.has_attribute(['-oss', '--oss']):
        if sp.has_attribute(['-u', '--upload']):
            Bucket().upload(sp.fetch_value(['-u', '--upload']))
        elif sp.has_attribute(['-d', '--download']):
            url = Bucket().url_prefix + sp.fetch_value(['-d', '--download'])
            du.download(url)
        elif sp.has_attribute(['-del', '--delete']):
            Bucket().delete(sp.fetch_value(['-del', '--delete']))
        elif sp.has_attribute(['-l', '--list']):
            print(Bucket().url_prefix)
            Bucket().list_files()
        elif sp.has_attribute(['-pf', '--prefix']):
            print(Bucket().url_prefix)

    elif sp.has_attribute(['-cos', '--cos']):
        coscli = COS()
        if sp.has_attribute(['-u', '--upload']):
            fname = sp.fetch_value(['-u', '--upload'])
            print(f"Start uploading {fname} ...")
            coscli.upload_file(fname, 'transfer/')
        elif sp.has_attribute(['-d', '--download']):
            fname = sp.fetch_value(['-d', '--download'])
            print(f"Start downloading {fname} ...")
            coscli.download_file(f'transfer/{fname}', fname)
        elif sp.has_attribute(['-del', '--delete']):
            coscli.delete_file('transfer/' +
                               sp.fetch_value(['-del', '--delete']))
        elif sp.has_attribute(['-l', '--list']):
            print(coscli.prefix())
            coscli.list_files('transfer/')

    elif sp.has_attribute(['-m', '--msg']):
        vs = sp.fetch_value(['-m', '--msg'])
        if sp.has_attribute(['-w', '--write']):
            Message().write(sp.fetch_value(['-w', '--write']))
        elif sp.has_attribute(['-r', '--read']):
            Message().read()
        elif vs:  # i.e., sli -m 'Some message'
            Message().write(vs)
        else:
            Message().read()

    elif sp.has_attribute(['-fund', '--fund']):
        if sp.has_attribute(['-ba', '--buyalert']):
            tgalert()
        else:
            invest_advice(sp.fetch_value(['-fund', '--fund'], None))

    elif sp.has_attribute(['-stock', '--stock']):
        code = sp.fetch_value(['-stock', '--stock'])
        if code:
            Stock().trend(str(code))
        else:
            Stock().my_trend()

    elif sp.has_attr(['-aes']):
        _msg = sp.fetch_value(['-aes'])
        if sp.has_attr(['-en']):
            passphrase = sp.fetch_value(['-en'])
            du.p(short_encode(_msg, passphrase))
        elif sp.has_attr(['-de']):
            passphrase = sp.fetch_value(['-de'])
            du.p(short_decode(_msg, passphrase))

    elif sp.has_attr(['-hema']):
        if sp.has_attr(['-id']):
            download_file_by_id(sp.fetch_value(['-id']))
        else:
            read_hema_bot()

    else:
        for l in msg.split("\n"):
            c, e = (l + " ::: ").split(':::')[:2]
            print("{:<70} {:<20}".format(c, e))

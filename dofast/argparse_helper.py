import argparse
import dofast.utils as df
from dofast.simple_parser import SimpleParser
from dofast.oss import Bucket, Message
from dofast.cos import COS
from dofast.fund import invest_advice, tgalert
from dofast.stock import Stock

msg = """A Simple yet powerful terminal CLient. 😏

-dw, --download -p, --proxy [-r|-o](--rename) ::: Download file.
-d, --ddfile[size] ::: Create random file.
-ip [-p, --port]::: Curl cip.cc
-rc, --roundcorner [--radius] ::: Add rounded corner to images.
-gu, --githubupload ::: Upload files to GitHub.
-sm, --smms ::: Upload image to sm.ms image server.
-yd, --youdao ::: Youdao dict translation.
-fd, --find [-dir, --dir] ::: Find files from dir.
-oss [-u, --upload | -d, --download | -del, --delete] ::: Aliyun OSS upload and download files.

-m, --msg [-r, --write | -w, --write] ::: Messenger
-fund, --fund [fund_code] ::: Fund investment.
-stock, --stock [stock_code] ::: Stock trend.
"""


def parse_arguments():
    sp = SimpleParser()
    sp.parse_args()

    if sp.has_attribute(['-dw', '--download'], excludes=['-oss']):
        sp.set_default('-p', 'http://cn.ddot.cc:51172')
        url = sp.fetch_value(['-dw'])
        proxy = sp.fetch_value(['-p', '--proxy'])
        name = sp.fetch_value(['-r', '-o', '--rename'])
        df.download(url, proxy, name)

    elif sp.has_attribute(['-d', '--ddfile'], excludes=['-oss', '-cos']):
        size = sp.fetch_value(['-d', '--ddfile'], 100)
        df.create_random_file(int(size))

    elif sp.has_attribute(['-ip']):
        if sp.has_attribute(['-p', '-port', '--port']):
            ip = sp.fetch_value(['-ip'], 'localhost')
            port = sp.fetch_value(['-p', '-port', '--port'], '80')
            df.p(df.shell(f"curl -s --connect-timeout 3 --socks5 {ip}:{port} ipinfo.io"))
        else:
            df.p(df.shell("curl -s cip.cc"))

    elif sp.has_attribute(['-rc', '--roundcorner']):
        image_path = sp.fetch_value(['-rc'])
        radius = int(sp.fetch_value(['--radius'], 10))
        df.rounded_corners(image_path, radius)

    elif sp.has_attribute(['-gu', '--githupupload']):
        df.githup_upload(sp.dict['-gu'].pop())

    elif sp.has_attribute(['-sm', '--smms']):
        df.smms_upload(sp.fetch_value(['-sm', '--smms']))

    elif sp.has_attribute(['-pac', '--updatepac']):
        url = sp.fetch_value(['-pac', '--updatepac'])
        df.update_pac(url)

    elif sp.has_attribute(['-yd', '--youdao']):
        df.youdao_dict(sp.fetch_value(['-yd', '--youdao'], 'Abandon'))

    elif sp.has_attribute(['-fd', '--find']):
        dir_ = sp.fetch_value(['-dir', '--dir'], ".")
        fname = sp.fetch_value(['-fd', '--find'])
        df.findfile(fname, dir_)

    elif sp.has_attribute(['-oss', '--oss']):
        if sp.has_attribute(['-u', '--upload']):
            Bucket().upload(sp.fetch_value(['-u', '--upload']))
        elif sp.has_attribute(['-d', '--download']):
            url = Bucket().url_prefix + sp.fetch_value(['-d', '--download'])
            df.download(url)
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
            fname=sp.fetch_value(['-u', '--upload'])
            print(f"Start uploading {fname} ...")
            coscli.upload_file(fname, 'transfer/')
        elif sp.has_attribute(['-d', '--download']):
            fname = sp.fetch_value(['-d', '--download'])
            print(f"Start downloading {fname} ...")
            coscli.download_file(f'transfer/{fname}', fname)
        elif sp.has_attribute(['-del', '--delete']):
            coscli.delete_file('transfer/' + sp.fetch_value(['-del', '--delete']))
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

    else:
        for l in msg.split("\n"):
            c, e = (l + " ::: ").split(':::')[:2]
            print("{:<70} {:<20}".format(c, e))

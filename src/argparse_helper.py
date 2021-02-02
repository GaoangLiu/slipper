import argparse
import dofast as df
from simple_parser import SimpleParser

msg = """A Simple yet powerful terminal CLient. 😏

-dw, --download -p, --proxy -r, --rename ::: Download file.
-d, --ddfile[size] ::: Create random file.
-ip ::: Curl cip.cc
-rc, --roundcorner ::: Add rounded corner to images.
-gu, --githubupload ::: Upload files to GitHub.
-sm, --smms ::: Upload image to sm.ms image server.
-yd, --youdao ::: Youdao dict translation.
-fd, --find [-dir, --dir] ::: Find files from dir.
"""


def parse_arguments():
    sp = SimpleParser()
    sp.parse_args()

    if sp.has_attribute(['-dw', '--download']):
        sp.set_default('-p', 'http://cn.ddot.cc:51172')
        url = sp.read_arg_value(['-dw'])
        proxy = sp.read_arg_value(['-p', '--proxy'])
        name = sp.read_arg_value(['-r', '--rename'])
        df.download(url, proxy, name)
    elif sp.has_attribute(['-d', '--ddfile']):
        size = sp.read_arg_value(['-d', '--ddfile'], 100)
        df.create_random_file(int(size))
    elif sp.has_attribute(['-ip']):
        df.p(df.shell("curl -s cip.cc"))
    elif sp.has_attribute(['-rc', '--roundcorner']):
        image_path = sp.read_arg_value(['-rc'])
        radius = int(sp.read_arg_value(['--radius'], 10))
        df.rounded_corners(image_path, radius)
    elif sp.has_attribute(['-gu', '--githupupload']):
        df.githup_upload(sp.dict['-gu'].pop())
    elif sp.has_attribute(['-sm', '--smms']):
        df.smms_upload(sp.read_arg_value(['-sm', '--smms']))
    elif sp.has_attribute(['-pac', '--updatepac']):
        url = sp.read_arg_value(['-pac', '--updatepac'])
        df.update_pac(url)
    elif sp.has_attribute(['-yd', '--youdao']):
        df.youdao_dict(sp.read_arg_value(['-yd', '--youdao'], 'Abandon'))
    elif sp.has_attribute(['-fd', '--find']):
        dir_ = sp.read_arg_value(['-dir', '--dir'], ".")
        fname = sp.read_arg_value(['-fd', '--find'])
        df.findfile(fname, dir_)
    else:
        for l in msg.split("\n"):
            c, e = (l + " ::: ").split(':::')[:2]
            print("{:<50} {:<20}".format(c, e))

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
-tgbot, --telegrambot ::: Telegram bot message.
-fund, --fund [fund_code] ::: Fund investment.
-stock, --stock [stock_code] ::: Stock trend.

-gcr(--gitcommitreminder) ::: Github daily commit reminder.
-pf(--phoneflow) [rest, daily] ::: Phone flow monitor.
-hx(--happyxiao) ::: http://www.happyxiao.com/ newsletters
"""

def display_message(message: str = msg):
    for l in message.split("\n"):
        c, e = (l + " ::: ").split(':::')[:2]
        print("{:<70} {:<20}".format(c, e))

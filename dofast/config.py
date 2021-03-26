import json
from pathlib import Path
from .toolkits.endecode import decode_with_keyfile

def decode(keyword: str) -> str:
    config_file = str(Path.home()) + '/.config/dofast.json'
    js = json.load(open(config_file, 'r'))
    _pass = decode_with_keyfile(js["auth_file"], js[keyword.lower()])
    return _pass


# def decode(keyword: str):
#     cmd = f"{file_path}/{_df} {keyword}"
#     return subprocess.check_output(cmd, stderr=subprocess.STDOUT,
#                                    shell=True).decode('utf8').strip()

# ALIYUN_ACCESS_KEY_ID = decode("ALIYUN_ACCESS_KEY_ID")
# ALIYUN_ACCESS_KEY_SECRET = decode("ALIYUN_ACCESS_KEY_SECRET")
# ALIYUN_BUCKET = decode("ALIYUN_BUCKET")
# ALIYUN_REGION = decode("ALIYUN_REGION")

# TENCENT_SECRET_ID = decode("TENCENT_SECRET_ID")
# TENCENT_SECRET_KEY = decode("TENCENT_SECRET_KEY")
# TENCENT_BUCKET = decode("TENCENT_BUCKET")

# PLUTOSHARE = decode("pluto_share")
# MESSALERT = decode("mess_alert")
# HTTP_PROXY = decode("http_proxy")
# HTTPS_PROXY = decode("http_proxy")

# GIT_TOKEN = decode("GIT_TOKEN")
# GIT_RAW_PREFIX = decode("GIT_RAW_PREFIX")

# YAHOO_USER_NAME = decode("YAHOO_USER_NAME")
# YAHOO_USER_PASSWORD = decode("YAHOO_USER_PASSWORD")
# GMAIL_USER_NAME = decode("gmail")
# FOXMAIL_USERNAME = decode("foxmail")

# HEMA_BOT = None

# # print(ALIYUN_ACCESS_KEY_ID,
# #       ALIYUN_ACCESS_KEY_SECRET,
# #       ALIYUN_BUCKET,
# #       PLUTOSHARE,
# #       GMAIL_USER_NAME,
# #       FOXMAIL_USERNAME,
# #       sep="\n")

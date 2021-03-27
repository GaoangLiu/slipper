import json
from pathlib import Path
from .toolkits.endecode import decode_with_keyfile


def decode(keyword: str) -> str:
    config_file = str(Path.home()) + '/.config/dofast.json'
    js = json.load(open(config_file, 'r'))
    _pass = decode_with_keyfile(js["auth_file"], js[keyword.lower()])
    return _pass

from pathlib import Path

import codefast as cf

from .toolkits.endecode import decode_with_keyfile, encode_with_keyfile

config_file = str(Path.home()) + '/.config/dofast.json'
js = cf.json.read(config_file)
salt = js['auth_file']


def decode(keyword: str) -> str:
    _pass = decode_with_keyfile(salt, js[keyword.lower()])
    return _pass


def fast_text_encode(text: str) -> str:
    ''' Encode text with passphrase in js[auth_file]'''
    return encode_with_keyfile(salt, text)


def fast_text_decode(text: str):
    return decode_with_keyfile(salt, text)

import getpass
import zipfile
from pathlib import Path

import codefast as cf

from .toolkits.endecode import decode_with_keyfile, encode_with_keyfile


def _init_config() -> dict:
    """ init configureation file on installing library."""

    _config_path = str(Path.home()) + "/.config/"
    _cf = _config_path + 'dofast.json'
    if not cf.io.exists(_cf):
        zip_json = f"{cf.io.dirname()}/dofast.json.zip"
        with zipfile.ZipFile(zip_json, 'r') as zip_ref:
            zip_ref.extractall(
                path=_config_path,
                pwd=bytes(getpass.getpass("type here your config password: "),
                          'utf-8'))
    return cf.js(_cf)


SERVER_HOST = 'a.ddot.cc'
js = _init_config()
SALT = js['auth_file']


def decode(keyword: str) -> str:
    _pass = decode_with_keyfile(SALT, js[keyword.lower()])
    return _pass


def fast_text_encode(text: str) -> str:
    ''' Encode text with passphrase in js[auth_file]'''
    return encode_with_keyfile(SALT, text)


def fast_text_decode(text: str):
    return decode_with_keyfile(SALT, text)

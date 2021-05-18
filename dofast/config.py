import getpass
import zipfile
from pathlib import Path

import codefast as cf

from .toolkits.endecode import decode_with_keyfile, encode_with_keyfile


def _init_config() -> dict:
    """ init configureation file on installing library."""

    _config_path = str(Path.home()) + "/.config/"
    _cf = _config_path + 'dofast.json'
    if not cf.file.exists(_cf):
        zip_json = f"{cf.file.dirname()}/dofast.json.zip"
        with zipfile.ZipFile(zip_json, 'r') as zip_ref:
            zip_ref.extractall(
                path=_config_path,
                pwd=bytes(getpass.getpass("type here your config password: "),
                          'utf-8'))
    return cf.json.read(_cf)


js = _init_config()
salt = js['auth_file']


def decode(keyword: str) -> str:
    _pass = decode_with_keyfile(salt, js[keyword.lower()])
    return _pass


def fast_text_encode(text: str) -> str:
    ''' Encode text with passphrase in js[auth_file]'''
    return encode_with_keyfile(salt, text)


def fast_text_decode(text: str):
    return decode_with_keyfile(salt, text)

import os, sys
import json
import base64
import tempfile
from Crypto.Cipher import AES


def encode(msg_text: str, passphrase: str) -> str:
    msg_text += '|' + msg_text * 100
    msg_text = msg_text[:1024]
    bytes_text = msg_text.encode().rjust(1024)  # in case this is a long text
    passphrase = passphrase.encode().ljust(32, b'*')
    cipher = AES.new(passphrase, AES.MODE_ECB)
    return base64.b64encode(cipher.encrypt(bytes_text)).decode('ascii')


def decode(msg_text: str, passphrase: str) -> str:
    bytes_text = msg_text.encode().ljust(1024)
    passphrase = passphrase.encode().ljust(32, b'*')
    try:
        cipher = AES.new(passphrase, AES.MODE_ECB)
        return cipher.decrypt(
            base64.b64decode(bytes_text)).decode().split('|')[0]
    except Exception as e:
        print(f"Maybe wrong password. {e}")
        return ""


def decode_with_keyfile(file_path: str, encrypted_message: str) -> str:
    """Decode message with keyfile, which contains the key phrase"""
    with open(file_path, 'r') as f:
        return decode(encrypted_message, f.read())

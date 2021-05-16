import base64
from Crypto.Cipher import AES


def encode(message: str, passphrase: str) -> str:
    message += '|' + message * 100
    message = message[:1024]
    bytes_text = message.encode().rjust(1024)  # in case this is a long text
    passphrase = passphrase.encode().ljust(32, b'*')
    cipher = AES.new(passphrase, AES.MODE_ECB)
    return base64.b64encode(cipher.encrypt(bytes_text)).decode('ascii')


def decode(message: str, passphrase: str) -> str:
    bytes_text = message.encode().ljust(1024)
    passphrase = passphrase.encode().ljust(32, b'*')
    try:
        cipher = AES.new(passphrase, AES.MODE_ECB)
        return cipher.decrypt(
            base64.b64decode(bytes_text)).decode().split('|')[0]
    except Exception as e:
        print(f"Maybe wrong password. {e}")
        return ""


def short_encode(message: str, passphrase: str) -> str:
    """Automatically increase just length w.r.t. message"""
    _bytelen, _len = 2, 0
    while 4**_bytelen < len(message):
        _bytelen += 1
    _len = 4**_bytelen
    bytes_text = message.encode().ljust(_len, b'|')
    passphrase = passphrase.encode().ljust(32, b'*')
    cipher = AES.new(passphrase, AES.MODE_ECB)
    return base64.b64encode(
        cipher.encrypt(bytes_text)).decode('ascii') + "|" + str(_len)


def short_decode(message: str, passphrase: str) -> str:
    if '|' not in message:
        return decode(message, passphrase)
    _text, _len = message.split('|')
    bytes_text = _text.encode().ljust(int(_len))
    passphrase = passphrase.encode().ljust(32, b'*')
    try:
        cipher = AES.new(passphrase, AES.MODE_ECB)
        text = cipher.decrypt(
            base64.b64decode(bytes_text)).decode().split('|')
        while text and not text[-1]:
            text.pop()
        return '|'.join(text)
    except Exception as e:
        print(f"Maybe wrong password. {e}")
        return ""


def decode_with_keyfile(file_path: str, encrypted_message: str) -> str:
    """Decode message with keyfile, which contains the key phrase"""
    with open(file_path, 'r') as f:
        _decode = short_decode if '|' in encrypted_message else decode
        return _decode(encrypted_message, f.read().strip())


def encode_with_keyfile(file_path: str, msg: str) -> str:
    """Enocde message with keyfile, which contains the key phrase"""
    with open(file_path, 'r') as f:
        return short_encode(msg, f.read().strip())

import os, sys
import json
import base64
import tempfile
from Crypto.Cipher import AES
from itertools import dropwhile


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


def short_encode(msg_text: str, passphrase: str) -> str:
    """Automatically increase just length w.r.t. msg_text"""
    _len = 4**next(dropwhile(lambda x: 4**x < len(msg_text), range(3, 1000)))
    msg_text += '|' + msg_text * _len
    msg_text = msg_text[:_len]
    bytes_text = msg_text.encode().rjust(_len)  # in case this is a long text
    passphrase = passphrase.encode().ljust(32, b'*')
    cipher = AES.new(passphrase, AES.MODE_ECB)
    return base64.b64encode(
        cipher.encrypt(bytes_text)).decode('ascii') + "|" + str(_len)


def short_decode(msg_text: str, passphrase: str) -> str:
    _text, _len = msg_text.split('|')
    bytes_text = _text.encode().ljust(int(_len))
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
        _decode = short_decode if '|' in encrypted_message else decode
        return _decode(encrypted_message, f.read().strip())


# print(short_encode('a', 'b'))
# et = 'IpUvmC6I/bBC99BNnK9dcw95NFc/TSaUHePKnj3t5ir8fSqrlN9KvJjth6qERekqiLqsb1QSmPrEJjtcUsudZis7Qns9yvJOg4nm9YH8Y/gpIKVUWNQbf1WtDC5CUrPAeRi7fG8KC6pxoXuroqyGVkXqhfmzfnfjQ71vHS60zwS5wNv4z6BRKE7GupuBARv0YLv01QL0YjRZq+rUVvCCeLGFNMcLBmSGwdIGC6FFHG2EAS56UpSDWSHVRJK+QeifRcHi7mJkqtf0onf1uR2GzQkkt9vFUOy04r4xnWAO1eO3LoNncSdRXoP6HiRU95oqrfrconpNtFGEJpvsXzAdM8MDUgo6XSCq14LmYPPrJqhc7x9x9pg+v2VmxORj9Itby516XDrl0OXUx77SZRyMyPzSZBHMG+hNwj6tH8sIis/lOi/+b16SC1hO8tSYRBFI+uNHw48Qe6ItN8VWVnc+nvaKBrW19+LglSy5af3kpcfAc1pjzUB6mf1gVTFcCJDU1ZbJAWvL8FfN7MrEAclZ3TkDFZTdI62ay4DI5vDJXsrZOzS2PWPSIbpbNqzAZhcZWVRpnoB4IT1SxBr9Gf74xxF+TLZVD0lDrbt68/eIxDGlpkOtg+Y7hF5Gr4WJW344EkZboOJw3Ztsbmp+aO29VSKVL5guiP2wQvfQTZyvXXMPeTRXP00mlB3jyp497eYqV2Z5UtKbaxQKuvKxQd+a0EcbIKe4BIT66XMd6dBJtJ9f4+21m9LdiV3efwplXsWYbEuntlpNVnZ4MrIgYr/m9kB/5moYm7fc3ogPIAVAT+clziMp2v/UknMPDEIOyDCujI7ICasgmgAmIkQAbFceXLAWjCAkPZ9fNH3Gh1rOKl5Rdn5tDy08oF8DVki8joVDRhMbFGHRqvi42rtAntZxeGD3hDEi9XY0fjTAFm/5XyI3SmJf6X5NAhTP8kJTQs24J7yQE0tJ8bHAMlEFKiX5gSn5ihcsVB2deATzT1TgQPyuxFJVkNKiD0XSphSH2KR4iLqsb1QSmPrEJjtcUsudZis7Qns9yvJOg4nm9YH8Y/gpIKVUWNQbf1WtDC5CUrPAeRi7fG8KC6pxoXuroqyGVkXqhfmzfnfjQ71vHS60zwS5wNv4z6BRKE7GupuBARv0YLv01QL0YjRZq+rUVvCCeLGFNMcLBmSGwdIGC6FFHG2EAS56UpSDWSHVRJK+QeifRcHi7mJkqtf0onf1uR2GzQkkt9vFUOy04r4xnWAO1eO3LoNncSdRXoP6HiRU95oqrfrconpNtFGEJpvsXzAdM8MDUgo6XSCq14LmYPPrJqhc7x9x9pg+v2VmxORj9Itby516XDrl0OXUx77SZRyMyA=='
# print(decode_with_keyfile('/tmp/telegram.key', et))

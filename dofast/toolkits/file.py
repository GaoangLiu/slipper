import os
import sys
from dofast.utils import textwrite, textread
from getpass import getpass


def load_password(file_path: str) -> str:
    """If passphrase file exists, then return the value in it.
    Otherwise, getpass() and store in file.
    """
    if os.path.exists(file_path):
        return textread(file_path)[0]
    else:
        _passphrase = getpass("Type here your OSS passphrase: ")
        if os.geteuid() != 0:
            print(
                "To store the password, you need to run this script with sudo!"
            )
        else:
            textwrite(_passphrase, file_path)
        return _passphrase

import os
import sys
from dofast.utils import textwrite, textread


def load_password(file_path: str) -> str:
    """If passphrase file exists, then return the value in it.
    Otherwise, getpass() and store in file.
    """
    if os.path.exists(file_path):
        return textread(file_path)[0]
    else:
        _passphrase = getpass("Type in your passphrase: ")
        textwrite(_passphrase, file_path)  # sudo may required.
        return _passphrase

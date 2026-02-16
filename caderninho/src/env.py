import os

from dotenv import load_dotenv

from caderninho.src.utils import is_testing

load_dotenv()


def getenv(key, default=None, test_key=None):
    if is_testing() and test_key:
        return os.getenv(test_key, default)
    if default:
        return os.getenv(key, default)
    return os.getenv(key)

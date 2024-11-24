import os

from dotenv import load_dotenv

load_dotenv()


def getenv(key, default=None):
    if default:
        return os.getenv(key, default)
    return os.getenv(key)

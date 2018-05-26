import os
from functools import wraps

import urllib.request
import requests
import wget

DIRNAME = 'downloads'
SAMPLE_URL = 'http://i3.ytimg.com/vi/J---aiyznGQ/mqdefault.jpg'


def create_download_dir():
    if not os.path.exists(DIRNAME):
        os.makedirs(DIRNAME)


def download_path(filename):
    return DIRNAME + os.path.sep + filename


def download(func):
    """decorator for download"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        create_download_dir()
        return func(*args, **kwargs)

    return wrapper


@download
def download_urlretrieve(target_url):
    """
    using urlretrieve
     - this way is deprecated in python3
    """

    urllib.request.urlretrieve(target_url, download_path('cat.jpg'))


@download
def download_urlopen(target_url):
    """
    using urlopen
    """

    filedata = urllib.request.urlopen(target_url)
    data_2_write = filedata.read()

    with open(download_path('cat.jpg'), 'wb') as f:
        f.write(data_2_write)


@download
def download_requests(target_url):
    """
    using requests
     - this module is not built-in
     - can get additional respons metadata from response
    """

    res = requests.get(target_url)

    with open(download_path('cat.jpg'), 'wb') as f:
        f.write(res.content)


@download
def download_wget(target_url):
    """
    using wget module
    """
    wget.download(target_url, download_path('cat.jpg'))


if __name__ == '__main__':
    download_urlretrieve(SAMPLE_URL)
    download_urlopen(SAMPLE_URL)
    download_requests(SAMPLE_URL)
    download_wget(SAMPLE_URL)

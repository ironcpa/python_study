from os import urandom


def abc_urandom(length):
    return 'abc' + urandom(length)

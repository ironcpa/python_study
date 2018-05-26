import unittest
import mock

from mock_module import abc_urandom


def simple_urandom(length):
    return 'f' * length


class TestRandom(unittest.TestCase):
    @mock.patch('mock_module.urandom', side_effect=simple_urandom)
    def test_urandom(self, abc_urandom):
        assert abc_urandom(5) == 'abcfffff'


if __name__ == '__main__':
    print(simple_urandom(5))
    print(abc_urandom(5))

import algorithms
import unittest
from random import shuffle
from unittest import TestCase


class TestAlgorithms(TestCase):
    def test_binary_sort(self):
        src = [x for x in range(10)]
        # shuffle(src)
        print(src)

        rslt = algorithms.binsearch(src, 7)
        print(rslt)
        self.assertEqual(rslt, 7)


if __name__ == '__main__':
    print('>' * 80)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAlgorithms)
    unittest.TextTestRunner(verbosity=2).run(suite)

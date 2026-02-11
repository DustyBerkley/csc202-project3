from typing import *
from dataclasses import dataclass
import unittest
import sys
sys.setrecursionlimit(10**6)

# when given a string, return a list of the frequencies of each character in the string
def cnt_freq(text: str) -> List[int]:
    counts = [0] * 256
    for char in text:
        idx = ord(char)
        counts[idx] += 1
    return counts



class Tests(unittest.TestCase):
    def test_cnt_freq(self):
        str_1 : str = "aaabccddddd"
        str_2 : str = "aaeefad"
        self.assertEqual(cnt_freq(str_1)[96:104], [0, 3, 1, 2, 5, 0, 0, 0])
        self.assertEqual(cnt_freq(str_2)[96:104], [0, 3, 0, 0, 1, 2, 1, 0])


if (__name__ == '__main__'):
    unittest.main()
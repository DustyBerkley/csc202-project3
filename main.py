from typing import *
from dataclasses import dataclass
import unittest
import sys
sys.setrecursionlimit(10**6)

@dataclass(frozen=True)
class HLeaf:
    count: int
    char: str

@dataclass(frozen=True)
class HNode:
    count: int
    char: str
    left: 'HTree'
    right: 'HTree'

HTree = Union[HLeaf, HNode]

# when given a string, return a list of the frequencies of each character in the string
def cnt_freq(text: str) -> List[int]:
    counts = [0] * 256
    for char in text:
        idx = ord(char)
        counts[idx] += 1
    return counts

# Returns True if the first tree has a smaller total occurrence count than the second,
# or if counts are same and char at root of 1st tree < 2nd
def tree_lt(t1: HTree, t2: HTree) -> bool:
    if t1.count != t2.count:
        return t1.count < t2.count
    return t1.char < t2.char

class Tests(unittest.TestCase):
    def test_cnt_freq(self):
        str_1 : str = "aaabccddddd"
        str_2 : str = "aaeefad"
        self.assertEqual(cnt_freq(str_1)[96:104], [0, 3, 1, 2, 5, 0, 0, 0])
        self.assertEqual(cnt_freq(str_2)[96:104], [0, 3, 0, 0, 1, 2, 1, 0])


if (__name__ == '__main__'):
    unittest.main()
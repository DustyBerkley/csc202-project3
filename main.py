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

HTList : TypeAlias = Union['HTLNode', None]

@dataclass(frozen=True)
class HTLNode:
    value: HTree
    rest: HTList

# return the length of a linked list of HTrees
def list_len(list: HTList) -> int:
    if(list == None):
        return 0
    return 1 + list_len(list.rest)

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
    tree_1 : HTree = HNode(1, "a", HNode(2, "b", HLeaf(4, "d"), HLeaf(5, "e")), HNode(3, "c", HLeaf(6, "f"), HLeaf(7, "g")))
    tree_2 : HTree = HNode(8, "h", HLeaf(9, "i"), HLeaf(10, "j"))
    list_1 : HTList = None
    list_2 : HTList = HTLNode(tree_1, None)
    list_3 : HTList = HTLNode(tree_1, HTLNode(tree_2, None))
    
    def test_cnt_freq(self):
        str_1 : str = "aaabccddddd"
        str_2 : str = "aaeefad"
        self.assertEqual(cnt_freq(str_1)[96:104], [0, 3, 1, 2, 5, 0, 0, 0])
        self.assertEqual(cnt_freq(str_2)[96:104], [0, 3, 0, 0, 1, 2, 1, 0])

    def test_tree_lt(self):
        self.assertTrue(tree_lt(self.tree_1, self.tree_2))
        self.assertTrue(tree_lt(self.tree_1, self.tree_1.left))

    def test_list_len(self):
        self.assertEqual(list_len(self.list_1), 0)
        self.assertEqual(list_len(self.list_2), 1)
        self.assertEqual(list_len(self.list_3), 2)


if (__name__ == '__main__'):
    unittest.main()
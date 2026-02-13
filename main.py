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

# Returns the HTree at said index within the HTList
def list_ref(list: HTList, idx: int) -> HTree:
    if idx < 0:
        raise IndexError("Negative index")
    if list is None:
        raise IndexError("Index out of bounds")
    if idx == 0:
        return list.value
    return list_ref(list.rest, idx - 1)

# insert a tree into a given tree list so that it follows the ordering rules of tree_lt
def tree_list_insert(list: HTList, other_tree: HTree) -> HTList:
    match list:
        case None:
            return HTLNode(other_tree, None)
        case HTLNode(v, r):
            if(not tree_lt(v, other_tree)):
                return HTLNode(other_tree, list)
            else:
                return HTLNode(v, tree_list_insert(r, other_tree))


# Returns an HTList containing 256 HLeaf nodes, in order 0 to 255
def base_tree_list(freqs: List[int]) -> HTList:
    lst: HTList = None
    for i in range(255, -1, -1):
        leaf: HLeaf = HLeaf(freqs[i], chr(i))
        lst = HTLNode(leaf, lst)
    return lst

class Tests(unittest.TestCase):
    tree_1 : HTree = HNode(1, "a", HNode(2, "b", HLeaf(4, "d"), HLeaf(5, "e")), HNode(3, "c", HLeaf(10, "f"), HLeaf(11, "g")))
    tree_2 : HTree = HNode(8, "h", HLeaf(9, "i"), HLeaf(14, "j"))
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

    def test_list_ref(self):
        self.assertEqual(list_ref(self.list_2, 0), self.tree_1)
        self.assertEqual(list_ref(self.list_3, 0), self.tree_1)
        self.assertEqual(list_ref(self.list_3, 1), self.tree_2)
        with self.assertRaises(IndexError):
            list_ref(self.list_3, 2)

    def test_base_tree_list(self):
        freqs = [0] * 256
        freqs[97] = 5
        freqs[98] = 3
        lst = base_tree_list(freqs)
        self.assertEqual(list_len(lst), 256)
        self.assertEqual(list_ref(lst, 97).count, 5)
        self.assertEqual(list_ref(lst, 97).char, 'a')
        self.assertEqual(list_ref(lst, 98).count, 3)
        self.assertEqual(list_ref(lst, 98).char, 'b')

    def test_tree_list_insert(self):
        self.assertEqual(tree_list_insert(self.list_1, self.tree_1), self.list_2)
        self.assertEqual(tree_list_insert(self.list_2, self.tree_2), self.list_3)

if (__name__ == '__main__'):
    unittest.main()
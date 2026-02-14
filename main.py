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

# Returns a sorted HTList by inserting each node from the unsorted list into an initially empty list
def initial_tree_sort(unsorted: HTList) -> HTList:
    def go(rem: HTList, sorted_lst: HTList) -> HTList:
        if rem is None:
            return sorted_lst
        return go(rem.rest, tree_list_insert(sorted_lst, rem.value))

    return go(unsorted, None)

# Returns a new sorted HTList by combining the first two trees into a HNode and inserting it into the remaining list
def coalesce_once(sorted_list: HTList) -> HTList:
    first = sorted_list.value
    second = sorted_list.rest.value

    rest = sorted_list.rest.rest

    new_count = first.count + second.count
    new_char = min(first.char, second.char)

    new_tree = HNode(new_count, new_char, first, second)

    return tree_list_insert(rest, new_tree)

# Returns an HTree formed by repeatedly combining trees in a sorted HTList until only one tree remains
def coalesce_all(sorted_list: HTList) -> HTree:
    if sorted_list is None:
        raise ValueError("Must have length >= 1")

    if sorted_list.rest is None:
        return sorted_list.value

    return coalesce_all(coalesce_once(sorted_list))

# Construct a Huffman tree from 's'.
def string_to_HTree(s : str) -> HTree:
    # chain together the functions required for the task:
    freqs = cnt_freq(s)
    treelist = base_tree_list(freqs)
    sorted_treelist = initial_tree_sort(treelist)
    return coalesce_all(sorted_treelist)

# Returns a 256-element array mapping each ASCII character to its Huffman encoding
def build_encoder_array(tree: HTree) -> List[str]:
    encoder: List[str] = [""] * 256

    # path_acc = current bit string being built
    # enc_acc = encoder array being filled
    def helper(t: HTree, path_acc: str, enc_acc: List[str]) -> None:
        if isinstance(t, HLeaf):
            enc_acc[ord(t.char)] = path_acc
        else:
            helper(t.left, path_acc + "0", enc_acc)
            helper(t.right, path_acc + "1", enc_acc)

    helper(tree, "", encoder)
    return encoder

# Returns the Huffman encoding of a string using the encoder array
def encode_string_one(s: str, encoder: List[str]) -> str:
    result = ""
    for ch in s:
        result += encoder[ord(ch)]
    return result

# Returns a bytearray representing the given bit string that is 1/8 long
def bits_to_bytes(bits: str) -> bytearray:
    padding = (8 - len(bits) % 8) % 8
    bits = bits + ("0" * padding)

    num_bytes = len(bits) // 8
    result = bytearray(num_bytes)

    for i in range(num_bytes):
        chunk = bits[i*8:(i+1)*8]
        result[i] = int(chunk, 2)

    return result

# Encodes contents of a source file using Huffman coding and writes the result to a target file
def huffman_code_file(source: str, target: str) -> None:
    with open(source, "r", encoding="utf-8") as f:
        text = f.read()

    tree = string_to_HTree(text)
    encoder = build_encoder_array(tree)
    bits = encode_string_one(text, encoder)
    byte_data = bits_to_bytes(bits)

    with open(target, "wb") as f:
        f.write(byte_data)


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

    def test_initial_tree_sort(self):
        a = HLeaf(2, 'b')
        b = HLeaf(1, 'c')
        c = HLeaf(1, 'a')

        unsorted = HTLNode(a, HTLNode(b, HTLNode(c, None)))
        sorted_lst = initial_tree_sort(unsorted)

        self.assertEqual(list_len(sorted_lst), 3)
        self.assertEqual(list_ref(sorted_lst, 0), c)  # (1,'a')
        self.assertEqual(list_ref(sorted_lst, 1), b)  # (1,'c')
        self.assertEqual(list_ref(sorted_lst, 2), a)  # (2,'b')

    def test_coalesce_once(self):
        a = HLeaf(1, 'a')
        b = HLeaf(2, 'b')
        c = HLeaf(5, 'c')

        lst = HTLNode(a, HTLNode(b, HTLNode(c, None)))

        new_lst = coalesce_once(lst)

        self.assertEqual(list_len(new_lst), 2)
        new_tree = list_ref(new_lst, 0)

        self.assertEqual(new_tree.count, 3)
        self.assertEqual(new_tree.char, 'a')
        self.assertEqual(new_tree.left, a)
        self.assertEqual(new_tree.right, b)

    def test_coalesce_all(self):
        a = HLeaf(1, 'a')
        b = HLeaf(2, 'b')
        c = HLeaf(3, 'c')

        lst = HTLNode(a, HTLNode(b, HTLNode(c, None)))

        tree = coalesce_all(lst)

        self.assertEqual(tree.count, 6)
        self.assertEqual(tree.char, 'a')  # min char across combined roots by your rule

    def test_build_encoder_array(self):
        a = HLeaf(1, 'a')
        b = HLeaf(1, 'b')
        c = HLeaf(1, 'c')
        right = HNode(2, 'b', b, c)
        tree = HNode(3, 'a', a, right)

        encoder = build_encoder_array(tree)

        self.assertEqual(encoder[ord('a')], "0")
        self.assertEqual(encoder[ord('b')], "10")
        self.assertEqual(encoder[ord('c')], "11")

    def test_encode_string_one(self):
        encoder = [""] * 256
        encoder[ord('a')] = "0"
        encoder[ord('b')] = "11"
        encoder[ord('c')] = "10"

        self.assertEqual(encode_string_one("a", encoder), "0")
        self.assertEqual(encode_string_one("ab", encoder), "011")
        self.assertEqual(encode_string_one("cab", encoder), "10011")

    def test_bits_to_bytes(self):
        self.assertEqual(bits_to_bytes("00000000"), bytearray([0]))
        self.assertEqual(bits_to_bytes("11111111"), bytearray([255]))
        self.assertEqual(bits_to_bytes("10101111"), bytearray([175]))

    def test_bits_to_bytes_padding(self):
        self.assertEqual(bits_to_bytes("1"), bytearray([128]))  # "10000000"
        self.assertEqual(bits_to_bytes("101"), bytearray([160]))  # "10100000"


if (__name__ == '__main__'):
    unittest.main()
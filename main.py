from typing import *
from dataclasses import dataclass
import unittest
import sys

sys.setrecursionlimit(10 ** 6)


@dataclass(frozen=True)
class HLeaf:
    count: int
    char: str

HTree = Union['HLeaf', 'HNode']

@dataclass(frozen=True)
class HNode:
    count: int
    char: str
    left: 'HTree'
    right: 'HTree'

HTList: TypeAlias = Union['HTLNode', None]

@dataclass(frozen=True)
class HTLNode:
    value: HTree
    rest: HTList


EncoderArray: TypeAlias = List[str]


# return the length of a linked list of HTrees
def list_len(list: HTList) -> int:
    if (list == None):
        return 0
    return 1 + list_len(list.rest)


# when given a string, return a list of the frequencies of each character in the string
def cnt_freq(text: str) -> List[int]:
    counts = [0] * 256
    for char in text:
        idx = ord(char)
        if 0 <= idx <= 255:
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
            if (not tree_lt(v, other_tree)):
                return HTLNode(other_tree, list)
            else:
                return HTLNode(v, tree_list_insert(r, other_tree))


# sort an entire list of HTrees so that it follows the ordering rules of tree_lt
def initial_tree_sort(unsorted_list: HTList) -> HTList:
    match unsorted_list:
        case None:
            return None
        case HTLNode(v, r):
            return tree_list_insert(initial_tree_sort(r), v)


# collapse the first two trees of a given HTList into a single tree and add it back to the list
# sorted_list must have at least two items
def coalesce_once(sorted_list: HTList) -> HTList:
    if (list_len(sorted_list) < 2):
        raise LookupError("sorted list must have at least two items")
    first_tree: HTree = sorted_list.value
    second_tree: HTree = sorted_list.rest.value
    new_count: int = first_tree.count + second_tree.count
    new_char: str = first_tree.char
    if second_tree.char < first_tree.char:
        new_char = second_tree.char

    new_node: HNode = HNode(new_count, new_char, first_tree, second_tree)
    new_list: HTList = tree_list_insert(sorted_list.rest.rest, new_node)
    return new_list


# collapse all trees in a given HTList into one single tree
# sorted_list must have at least one item
def coalesce_all(sorted_list: HTList) -> HTree:
    if (sorted_list == None):
        raise LookupError("sorted list must have at least one item")
    if (sorted_list.rest == None):
        return sorted_list.value
    return coalesce_all(coalesce_once(sorted_list))


# Returns an HTList containing 256 HLeaf nodes, in order 0 to 255
def base_tree_list(freqs: List[int]) -> HTList:
    lst: HTList = None
    for i in range(255, -1, -1):
        leaf: HLeaf = HLeaf(freqs[i], chr(i))
        lst = HTLNode(leaf, lst)
    return lst


# Construct a Huffman tree from 's'.
def string_to_HTree(s: str) -> HTree:
    # chain together the functions required for the task:
    freqs = cnt_freq(s)
    treelist = base_tree_list(freqs)
    sorted_treelist = initial_tree_sort(treelist)
    return coalesce_all(sorted_treelist)


# build an encoding array from a given Huffman Tree
def build_encoder_array(tree: HTree) -> EncoderArray:
    encoder_array: EncoderArray = [""] * 256

    def traverse_tree(tree: HTree, encoder_array: EncoderArray, pathway: str) -> None:
        match tree:
            case HLeaf(count, char):
                encoder_array[ord(char)] = pathway
            case HNode(count, char, left, right):
                traverse_tree(left, encoder_array, pathway + "0")
                traverse_tree(right, encoder_array, pathway + "1")

    traverse_tree(tree, encoder_array, "")
    return encoder_array


# encode an input string into a huffman encoding given an encoder array
def encode_string_one(input: str, encoder_array: EncoderArray) -> str:
    match input:
        case "":
            return ""
        case _:
            this_encoding: str = encoder_array[ord(input[0])]
            return this_encoding + encode_string_one(input[1:len(input)], encoder_array)


# convert a list of encoded bits to a list of encoded bytes
def bits_to_bytes(encoded_bits: str) -> bytearray:
    if (len(encoded_bits) % 8 != 0):
        pad_length: int = 8 - len(encoded_bits) % 8
        encoded_bits += "0" * pad_length

    array_of_bytes = bytearray(len(encoded_bits) // 8)

    for i in range(0, len(encoded_bits), 8):
        first_eight: str = encoded_bits[i:i + 8]
        this_byte: int = int(first_eight, 2)
        array_of_bytes[i // 8] = this_byte

    return array_of_bytes


# take the contents of a given file, consruct a huffman tree from it and encode that file using the huffman tree
# write this encoded file to a given output file
def huffman_code_file(input_file_path: str, output_file_path: str) -> None:
    with open(input_file_path, 'r') as input_file:
        input_data = input_file.read()
        huffman_tree: HTree = string_to_HTree(input_data)
        encoder_array: EncoderArray = build_encoder_array(huffman_tree)
        encoded_bits: str = encode_string_one(input_data, encoder_array)
        encoded_bytes: bytearray = bits_to_bytes(encoded_bits)

        with open(output_file_path, 'wb') as output_file:
            output_file.write(encoded_bytes)


class Tests(unittest.TestCase):
    tree_1: HTree = HNode(1, "a", HNode(2, "b", HLeaf(4, "d"), HLeaf(5, "e")),
                          HNode(3, "c", HLeaf(10, "f"), HLeaf(11, "g")))
    tree_2: HTree = HNode(8, "h", HLeaf(9, "i"), HLeaf(14, "j"))
    list_1: HTList = None
    list_2: HTList = HTLNode(tree_1, None)
    list_3: HTList = HTLNode(tree_1, HTLNode(tree_2, None))
    list_4: HTList = HTLNode(tree_2, HTLNode(tree_1, HTLNode(HLeaf(3, "c"), None)))
    list_5: HTList = HTLNode(tree_2, HTLNode(tree_1, None))

    def test_cnt_freq(self):
        str_1: str = "aaabccddddd"
        str_2: str = "aaeefad"
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
        self.assertEqual(initial_tree_sort(self.list_5), self.list_3)
        self.assertEqual(initial_tree_sort(self.list_4),
                         HTLNode(self.tree_1, HTLNode(HLeaf(3, "c"), HTLNode(self.tree_2, None))))

    def test_coalesce_once(self):
        first_coalesced: HTList = HTLNode(HNode(11, "c", HLeaf(3, "c"), self.tree_2), None)
        second_coalesced: HTList = HTLNode(HNode(8, "c", HLeaf(3, "c"), HLeaf(5, "g")), HTLNode(self.tree_2, None))

        self.assertEqual(coalesce_once(HTLNode(HLeaf(3, "c"), HTLNode(self.tree_2, None))), first_coalesced)
        self.assertEqual(coalesce_once(HTLNode(HLeaf(3, "c"), HTLNode(HLeaf(5, "g"), HTLNode(self.tree_2, None)))),
                         second_coalesced)

    def test_coalesce_all(self):
        first_coalesced: HTree = HNode(11, "c", HLeaf(3, "c"), self.tree_2)
        second_coalesced: HTree = HNode(16, "c", HNode(8, "c", HLeaf(3, "c"), HLeaf(5, "g")), self.tree_2)

        self.assertEqual(coalesce_all(HTLNode(HLeaf(3, "c"), HTLNode(self.tree_2, None))), first_coalesced)
        self.assertEqual(coalesce_all(HTLNode(HLeaf(3, "c"), HTLNode(HLeaf(5, "g"), HTLNode(self.tree_2, None)))),
                         second_coalesced)

    def test_build_encoder_array(self):
        test_tree: HTree = string_to_HTree("abcccbdd")
        self.assertEqual(build_encoder_array(test_tree)[97:101], ['1101', '111', '0', '10'])

    def test_encode_string_one(self):
        test_tree: HTree = string_to_HTree("This is a test encoding string. Hopefully this works")
        test_encoding_array = build_encoder_array(test_tree)
        actual_encoding = encode_string_one("test phrase", test_encoding_array)
        expected_encoding: str = "000010001100010111101011011111101001110110100"
        self.assertEqual(actual_encoding, expected_encoding)

    def test_bits_to_bytes(self):
        test_bits: str = "000010001100010111101011011111101001110110100"
        self.assertEqual(bits_to_bytes(test_bits), bytearray(b'\x08\xc5\xeb~\x9d\xa0'))


if (__name__ == '__main__'):
    unittest.main()
    # huffman_code_file("input_test.txt", "output_test.txt")
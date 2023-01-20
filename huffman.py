from bitarray import BitArray, SimpleArray
import struct

class Huffman:
    """
    Namespace for functions to implement Huffman encode and decode.
    Reference:
    - https://github.com/tjazerzen/Huffman_encoding_decoding
    - https://stackoverflow.com/questions/759707/efficient-way-of-storing-huffman-tree
    """
    class Node:
        def __init__(self, char, freq):
            self.char = char  # the ascii character to encode
            self.freq = freq  # frequency of the char in the input string
            self.code = ""    # the Huffman code of this char
            self.is_leaf = False
            self.left = None
            self.right = None
        
        def __repr__(self):
            return "char: {}, freq: {}, code: {}".format(self.char, self.freq, self.code)


    @staticmethod
    def stats_input(input):
        """
        Statistic the frequence of each charactor in the string
        Return a dict of {char : freq}. 
        The dict is sorted so that highest is at front
        """
        dict_freq = {}
        for char in input:
            if char in dict_freq:
                dict_freq[char] += 1
            else:
                dict_freq[char] = 1
        dict_freq = sorted(dict_freq.items(), key=lambda x:x[1], reverse=True)
        return dict(dict_freq)

    @staticmethod
    def insert_node(nodes_list, node):
        """
        Insert the node into the nodes_list while maintaining the ordering of the list
        """
        freq = node.freq
        for idx in range(len(nodes_list)):
            freq_cur = nodes_list[idx].freq
            if freq_cur <= freq:
                nodes_list.insert(idx, node)
                return
        nodes_list.append(node)

    @staticmethod
    def build_tree(input):
        """
        Build the Huffman tree from an input string
        """
        dict_freq = Huffman.stats_input(input)
        nodes_list = []
        for char, freq in dict_freq.items():
            node = Huffman.Node(char, freq)
            node.is_leaf = True
            nodes_list.append(node)

        while len(nodes_list) != 1:
            first_node = nodes_list.pop()
            second_node = nodes_list.pop()
            node = Huffman.Node("", first_node.freq + second_node.freq)
            node.right = first_node
            node.left = second_node
            Huffman.insert_node(nodes_list, node)

        return nodes_list[0]

    @staticmethod
    def get_codes(root):
        """
        Get the Huffman dict ({char: Huffman code}) from Huffman tree
        """
        dict_code = {}
        node_stack = []
        node_stack.append(root)
        position_stack = []
        position_stack.append("")
        while len(node_stack) != 0:
            node = node_stack.pop()
            position = position_stack.pop()
            node.code = position
            dict_code[node.char] = node.code
            if node.left:
                node_stack.append(node.left)
                position_stack.append(position + "0")
            if node.right:
                node_stack.append(node.right)
                position_stack.append(position + "1")
        dict_code.pop("")
        return dict_code

    @staticmethod
    def encode_input(dict_code, text_input, to_bitarray = True):
        """
        Use Huffman dict to encode input text
        """
        if to_bitarray:
            text_encode = BitArray()
        else:
            text_encode = SimpleArray()
        for char in text_input:
            huff_code = dict_code[char]
            for ch in huff_code:
                bit = int(ch == "1")
                text_encode.write_bit(bit)
        return text_encode

    @staticmethod
    def decode_input(root, text_encode):
        text_decode = ""
        idx_cur = 0
        idx_max = len(text_encode)
        while idx_cur < idx_max:
            node = root
            while not node.is_leaf:
                if text_encode.read_bit():
                    node = node.right
                    idx_cur += 1
                else:
                    node = node.left
                    idx_cur += 1
            text_decode += node.char
        return text_decode


    @staticmethod
    def encode_tree(root, to_bitarray = True):
        stack = []
        stack.append(root)
        if to_bitarray:
            tree_encode = BitArray()
        else:
            tree_encode = SimpleArray()
        while len(stack) != 0:
            node = stack.pop()
            if node.is_leaf:
                tree_encode.write_bit(1)
                tree_encode.write_char(node.char)
            else:
                tree_encode.write_bit(0)
                stack.append(node.right)
                stack.append(node.left)
        return tree_encode

    @staticmethod
    def decode_tree(bit_reader):
        bit_cur = bit_reader.read_bit()
        if bit_cur:
            node = Huffman.Node(bit_reader.read_char(), 0)
            node.is_leaf = True
            return node
        else:
            left = Huffman.decode_tree(bit_reader)
            right = Huffman.decode_tree(bit_reader)
            node = Huffman.Node("", 0)
            node.left = left
            node.right = right
            return node

    @staticmethod
    def pack_tree_and_text_bitarray(tree, text):
        rst = (struct.pack("<I", tree.bit_offset_w) + tree.to_bytes() + 
               struct.pack("<I", text.bit_offset_w) + text.to_bytes())
        return rst

    @staticmethod
    def unpack_tree_and_text_bitarray(input_bytes):
        num_bit_tree = struct.unpack("<I", input_bytes[0:4])[0]
        num_byte_tree = int(num_bit_tree / 8)
        if num_bit_tree - 8 * num_byte_tree > 0:
            num_byte_tree += 1
        idx_text = 4 + num_byte_tree
        tree = BitArray.from_bytes(input_bytes[4:idx_text], num_bit_tree)

        num_bit_text = struct.unpack("<I", input_bytes[idx_text:idx_text+4])[0]
        num_byte_text = int(num_bit_text / 8)
        if num_bit_text - 8 * num_byte_text > 0:
            num_byte_text += 1
        text = BitArray.from_bytes(input_bytes[idx_text+4:idx_text+4+num_byte_text], num_bit_text)
        idx_r = idx_text+4+num_byte_text
        if (idx_r) != len(input_bytes):
            IndexError("Input bytes too large, something must be wrong.\n"
                       "read bytes: {}, total bytes: {}".format(idx_r, len(input_bytes)))
        return [tree, text]

def test_huffman(text_input):
    dict_freq = Huffman.stats_input(text_input)
    huffman_tree = Huffman.build_tree(text_input)
    dict_code = Huffman.get_codes(huffman_tree)
    text_encode = Huffman.encode_input(dict_code, text_input, to_bitarray=False)
    tree_encode = Huffman.encode_tree(huffman_tree, to_bitarray=False)

    huffman_tree_decode = Huffman.decode_tree(tree_encode)
    text_decode = Huffman.decode_input(huffman_tree_decode, text_encode)

def test_huffman_binary(text_input):
    dict_freq = Huffman.stats_input(text_input)
    huffman_tree = Huffman.build_tree(text_input)
    dict_code = Huffman.get_codes(huffman_tree)
    text_encode_bitarray = Huffman.encode_input(dict_code, text_input)
    tree_encode_bitarray = Huffman.encode_tree(huffman_tree)
    
    tree_encode_bitarray.reset_read_head()
    huffman_tree_decode = Huffman.decode_tree(tree_encode_bitarray)
    text_encode_bitarray.reset_read_head()
    text_decode = Huffman.decode_input(huffman_tree_decode, text_encode_bitarray)

if __name__ == "__main__":
    # text_input = "A Huffman code is a type of optimal prefix code that is used for compressing data. The Huffman encoding and decoding schema is also lossless, meaning that when compressing the data to make it smaller, there is no loss of information."
    text_input = "AAAAAABCCCCCCDDEEEEE"
    test_huffman(text_input)
    # test_huffman_binary(text_input)
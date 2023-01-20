# -*- coding: utf-8 -*-

import struct

basic_structures = {
    "int8": ("b", 1),
    "uint8": ("B", 1),
    "int16": ("h", 2),
    "uint16": ("H", 2),
    "int32": ("i", 4),
    "uint32": ("I", 4),
    "float": ("f", 4),
    "double": ("d", 8),
    "bool": ("?", 1)
}

class ParsedStruct:
    """
    Stores the parsed fields in an struct.
    The `self.fields` variable is a list of paris:
    [(var_name, type_name, is_list, list_size)]
    """
    def __init__(self, name, type_var_pairs):
        """
        `type_var_pairs`: list of pair of type_name and var_name.
        Example: [("int32", "id"), ("int32[]" "friends"), ("float[3]", "position")]
        """
        self.name = name
        self.fields = []
        for type_name, var_name in type_var_pairs:
            is_list = False
            list_size = 0
            if type_name[-1] == "]":
                is_list = True
                idx_l = type_name.find("[")
                try:
                    list_size = int(type_name[idx_l+1:-1])
                except ValueError:
                    list_size = 0
                type_name = type_name[:idx_l]
            self.fields.append((var_name, type_name, is_list, list_size))

    @staticmethod
    def parse_struct(proto):
        """
        Read a struct from the proto
        """
        name, proto_left = proto.split("{", 1)
        name = name.strip()
        body, proto_left = proto_left.split("}", 1)
        fields = body.split(";")[:-1]
        type_var_pairs = []
        for field in fields:
            type_var_pair = field.strip().split()
            if len(type_var_pair) == 1:
                idx = type_var_pair[0].find("]")
                type_name = type_var_pair[0][0:idx+1]
                variable_name = type_var_pair[0][idx+1:]
                type_var_pair = [type_name, variable_name]
            type_var_pairs.append(type_var_pair)
        proto_left = proto_left.split(";", 1)[1].strip()
        parsed_struct = ParsedStruct(name, type_var_pairs)
        return parsed_struct, proto_left

    def __str__(self):
        s_name = "Struct name: {}".format(self.name)
        s_fields = "Struct fields: {}".format(self.fields)
        return s_name + "\n" + s_fields + "\n"

    def __repr__(self):
        return self.__str__()

class BitArray:
    """
    Container to manipulate bit in python.
    Main methods: write_bit, write_char, read_bit, read_char
    Reference:
    - https://github.com/scott-griffiths/bitstring
    """

    def __init__(self):
        self.raw_array = bytearray()
        self.bit_offset_w = 0  # write
        self.bit_offset_r = 0  # read
        self.byte_length = 0

    @staticmethod
    def from_bytes(input_bytes, num_bit = 0):
        bit_array = BitArray()
        bit_array.bit_offset_w = num_bit
        bit_array.raw_array = bytearray(input_bytes)
        return bit_array

    def to_bytes(self):
        return bytes(self.raw_array)

    def print_binary(self):
        for i in range(self.byte_length):
            print("{:08b}".format(self.raw_array[i]))

    def print_hex(self):
        print(self.raw_array)

    def __repr__(self):
        return self.raw_array

    def __len__(self):
        return self.bit_offset_w

    def check_full(self):
        if self.bit_offset_w == self.byte_length * 8:
            self.byte_length += 1
            self.raw_array.append(0)

    def write_bit(self, bit):
        """
        append a bit at the end of bit array
        input bit can be 1 / 0
        """
        self.check_full()
        if bit:
            idx_byte = int(self.bit_offset_w / 8)
            idx_bit = self.bit_offset_w - 8 * idx_byte
            self.raw_array[idx_byte] |= (0b10000000 >> idx_bit)
        self.bit_offset_w += 1

    def write_char(self, char):
        """
        append an ascii character at the end of bit array
        """
        # convert char to int
        char_ascii = ord(char)
        if self.bit_offset_w == self.byte_length * 8:
            # quick method if array is already in chunck of byte
            self.raw_array.append(char_ascii)
            self.byte_length += 1
            self.bit_offset_w += 8
        else:
        # get each bit of char from left to right and append it
            for i in range(8):
                bit = 0b00000001 & (char_ascii >> (7-i))
                self.write_bit(bit)

    def reset_read_head(self):
        self.bit_offset_r = 0

    def check_out_range(self):
        if self.bit_offset_r == self.bit_offset_w:
            raise IndexError("Read bit out of range")

    def read_bit(self):
        self.check_out_range()
        idx_byte = int(self.bit_offset_r / 8)
        idx_bit = self.bit_offset_r - 8 * idx_byte
        bit = (self.raw_array[idx_byte] >> (7-idx_bit)) & 0b00000001
        self.bit_offset_r += 1
        return bit

    def read_char(self):
        char_ascii = 0
        for i in range(8):
            bit = self.read_bit()
            if bit:
                char_ascii ^= (0b10000000 >> i)
        char = chr(char_ascii)  # str(unichr(char_ascii)) for python2
        return char


class SimpleArray:
    """
    The list version of BitArray, used only for testing
    """
    def __init__(self):
        self.raw_array = []
        self.bit_offset_r = 0  # read

    def __repr__(self):
        return str(self.raw_array)

    def __len__(self):
        return len(self.raw_array)

    def write_bit(self, bit):
        self.raw_array.append(bit)

    def write_char(self, char):
        self.write_bit(char)

    def reset_read_head(self):
        self.bit_offset_r = 0

    def read_bit(self):
        bit = self.raw_array[self.bit_offset_r]
        self.bit_offset_r += 1
        return bit

    def read_char(self):
        return self.read_bit()


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


class ProtoParser:
    def __init__(self):
        self.protocol = {}

    def buildDesc(self, filename):
        with open(filename) as f:
            str_proto = f.read()
        while len(str_proto) > 0:
            parsed_struct, str_proto = ParsedStruct.parse_struct(
                str_proto)
            self.protocol[parsed_struct.name] = parsed_struct

    def dumps(self, strucut_name, obj_data):
        data_b = self.serialize_struct(obj_data, strucut_name)
        data_hex = data_b.encode("hex")
        return data_hex

    def loads(self, strucut_name, serialized_data):
        self.data_to_load = serialized_data.decode("hex")
        rst, idx_read = self.load_struct(strucut_name)
        if idx_read != len(self.data_to_load):
            print("serialized_data has not been read completely")
        return rst

    def serialize_struct(self, obj_data, type_name):
        if type_name == "string":
            string_size = len(obj_data)
            data_s = struct.pack("<H", string_size) + obj_data
        elif type_name in basic_structures.keys():
            type_code = basic_structures[type_name][0]
            data_s = struct.pack("<{:s}".format(type_code), obj_data)
        elif type_name in self.protocol.keys():
            fields = self.protocol[type_name].fields
            data_s = b""
            for (var_name, type_name_, is_list, list_size) in fields:
                var_data = obj_data[var_name]
                if is_list:
                    data_s += self.serialize_list(var_data,
                                                  type_name_, list_size)
                else:
                    data_s += self.serialize_struct(var_data, type_name_)
        else:
            raise KeyError("Unrecognized strucut name: {}".format(type_name))
        return data_s

    def serialize_list(self, list_data, type_name, list_size):
        data_s = b""
        if not list_size:
            num = len(list_data)
            data_s += struct.pack("<H".format(num), num)
        for i in range(len(list_data)):
            data_s += self.serialize_struct(list_data[i], type_name)
        return data_s

    def load_struct(self, type_name, idx_read = 0):
        if type_name == "string":
            string_size = struct.unpack("<H", self.data_to_load[idx_read:idx_read+2])[0]
            string_data = self.data_to_load[idx_read+2:idx_read+2+string_size]
            idx_read += 2 + string_size
            return string_data, idx_read
        elif type_name in basic_structures.keys():
            type_code, type_size = basic_structures[type_name]
            var_data = struct.unpack("<{:s}".format(
                type_code), self.data_to_load[idx_read:idx_read+type_size])[0]
            idx_read += type_size
            return var_data, idx_read
        elif type_name in self.protocol.keys():
            fields = self.protocol[type_name].fields
            var_data = {}
            for (var_name, type_name_, is_list, list_size) in fields:
                if is_list:
                    var_data[var_name], idx_read = self.load_list(type_name_, list_size, idx_read)
                else:
                    var_data[var_name], idx_read = self.load_struct(type_name_, idx_read)
            return var_data, idx_read
        else:
            raise KeyError("Unrecognized strucut name: {}".format(type_name))

    def load_list(self, type_name, list_size, idx_read):
        if not list_size:
            list_size = struct.unpack("<H", self.data_to_load[idx_read:idx_read+2])[0]
            idx_read += 2
        data = []
        for _ in range(list_size):
            item, idx_read = self.load_struct(type_name, idx_read)
            data.append(item)
        return tuple(data), idx_read

    def dumpComp(self, strucut_name, obj_data):
        obj_serialized = self.dumps(strucut_name, obj_data)
        obj_serialized = obj_serialized.decode("hex")
        huffman_tree = Huffman.build_tree(obj_serialized)
        dict_code = Huffman.get_codes(huffman_tree)
        text_encode_bitarray = Huffman.encode_input(dict_code, obj_serialized)
        tree_encode_bitarray = Huffman.encode_tree(huffman_tree)
        tree_text_packed = Huffman.pack_tree_and_text_bitarray(tree_encode_bitarray, text_encode_bitarray)
        return tree_text_packed

    def loadComp(self, strucut_name, data_compressed):
        tree_encode, text_encode = Huffman.unpack_tree_and_text_bitarray(data_compressed)
        tree = Huffman.decode_tree(tree_encode)
        data_serialized = Huffman.decode_input(tree, text_encode)
        obj = self.loads(strucut_name, data_serialized.encode("hex"))
        return obj


if __name__ == "__main__":
    # read protocal to python dict
    proto_parser = ProtoParser()
    proto_parser.buildDesc("player.proto")

    obj = {
        "name": "骨精灵",
        "id": 5201314,
        "married": False,
        "friends": (5201315, 244578811),
        "position": (134.5, 0.0, 23.41),
        "pet": {
            "name": "骨精灵的小可爱",
            "skill": (
                {"id": 1, "level": 10},
                {"id": 2, "level": 99}
            )
        }
    }

    obj_simple = {
        "name": "骨精灵",
        "id": 5201314,
        "married": False,
        "friends": (5201315, 244578811),
        "position": (134.5, 0.0, 23.41),
    }

    print("Original object: ")
    print(obj)

    obj_serialized = proto_parser.dumps("Player", obj)
    print("Serialized object: ")
    print(obj_serialized)

    rst_deserialized = proto_parser.loads("Player", obj_serialized)
    print("Deserialized object: ")
    print(rst_deserialized)

    obj_compressed = proto_parser.dumpComp("Player", obj)
    print("Compressed object: ")
    print(obj_compressed)

    obj_decompressed = proto_parser.loadComp("Player", obj_compressed)
    print("Deompressed object: ")
    print(obj_decompressed)

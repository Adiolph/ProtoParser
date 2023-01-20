import struct
from huffman import Huffman
from parsed_strucut import ParsedStruct

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


class ProtoParser:
    def __init__(self) -> None:
        self.protocol = {}

    def buildDesc(self, filename):
        with open(filename) as f:
            str_proto = f.read()
        while len(str_proto) > 0:
            struct_name, type_var_pairs, str_proto = ParsedStruct.parse_struct(
                str_proto)
            self.protocol[struct_name] = ParsedStruct(
                struct_name, type_var_pairs)

    def dumps(self, strucut_name: str, obj_data: dict) -> str:
        data_b = self.serialize_struct(obj_data, strucut_name)
        return data_b.hex()

    def loads(self, strucut_name: str, serialized_data: str) -> dict:
        self.data_s = bytes.fromhex(serialized_data)
        rst = self.load_struct(strucut_name)
        if len(self.data_s) != 0:
            print("serialized_data has not been read completely")
        return rst

    def serialize_struct(self, obj_data, type_name: str) -> bytes:
        if type_name == "string":
            data_b = obj_data.encode(encoding="UTF-8", errors="strict")
            string_size = len(data_b)
            data_s = struct.pack("<H", string_size) + data_b
        elif type_name in basic_structures.keys():
            type_code = basic_structures[type_name][0]
            data_s = struct.pack("<{:s}".format(type_code), obj_data)
        elif type_name in self.protocol.keys():
            fields = self.protocol[type_name].fields
            data_s = b""
            for var_name, (type_name, is_list, list_size) in fields.items():
                var_data = obj_data[var_name]
                if is_list:
                    data_s += self.serialize_list(var_data,
                                                  type_name, list_size)
                else:
                    data_s += self.serialize_struct(var_data, type_name)
        else:
            raise KeyError("Unrecognized strucut name: {}".format(type_name))
        return data_s

    def serialize_list(self, list_data, type_name: str, list_size: int) -> bytes:
        data_s = b""
        if not list_size:
            num = len(list_data)
            data_s += struct.pack("<H".format(num), num)
        for i in range(len(list_data)):
            data_s += self.serialize_struct(list_data[i], type_name)
        return data_s

    def load_struct(self, type_name: str):
        if type_name == "string":
            string_size = struct.unpack("<H", self.data_s[:2])[0]
            idx_r = 2+string_size
            string_data_bytes = self.data_s[2:idx_r]
            string_data = string_data_bytes.decode(
                encoding="UTF-8", errors="strict")
            self.data_s = self.data_s[idx_r:]
            return string_data
        elif type_name in basic_structures.keys():
            type_code, type_size = basic_structures[type_name]
            idx_r = type_size
            var_data = struct.unpack("<{:s}".format(
                type_code), self.data_s[:idx_r])[0]
            self.data_s = self.data_s[idx_r:]
            return var_data
        elif type_name in self.protocol.keys():
            fields = self.protocol[type_name].fields
            var_data = {}
            for var_name, (type_name, is_list, list_size) in fields.items():
                if is_list:
                    var_data[var_name] = self.load_list(type_name, list_size)
                else:
                    var_data[var_name] = self.load_struct(type_name)
            return var_data
        else:
            raise KeyError("Unrecognized strucut name: {}".format(type_name))

    def load_list(self, type_name: str, list_size: int) -> tuple:
        if not list_size:
            list_size = struct.unpack("<H", self.data_s[:2])[0]
            self.data_s = self.data_s[2:]
        data = []
        for _ in range(list_size):
            data.append(self.load_struct(type_name))
        return tuple(data)

    def dumpComp(self, strucut_name: str, obj_data: dict) -> bytes:
        obj_serialized = self.dumps(strucut_name, obj_data)
        huffman_tree = Huffman.build_tree(obj_serialized)
        dict_code = Huffman.get_codes(huffman_tree)
        text_encode_bitarray = Huffman.encode_input(dict_code, obj_serialized)
        tree_encode_bitarray = Huffman.encode_tree(huffman_tree)
        tree_text_packed = Huffman.pack_tree_and_text_bitarray(tree_encode_bitarray, text_encode_bitarray)
        return tree_text_packed

    def loadComp(self, strucut_name: str, data_compressed: bytes) -> dict:
        tree_encode, text_encode = Huffman.unpack_tree_and_text_bitarray(data_compressed)
        tree = Huffman.decode_tree(tree_encode)
        data_serialized = Huffman.decode_input(tree, text_encode)
        obj = self.loads(strucut_name, data_serialized)
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

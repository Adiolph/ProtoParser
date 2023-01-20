class ParsedStruct:
    def __init__(self, name, type_var_pairs) -> None:
        self.name = name
        self.fields = {}
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
            self.fields[var_name] = (type_name, is_list, list_size)

    @staticmethod
    def parse_struct(proto: str):
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
        return name, type_var_pairs, proto_left

    def __str__(self) -> str:
        s_name = "Struct name: {}".format(self.name)
        s_fields = "Struct fields: {}".format(self.fields)
        return s_name + "\n" + s_fields + "\n"

    def __repr__(self) -> str:
        return self.__str__()

if __name__ == "__main__":
    with open("a.proto") as f:
        proto = f.read()
    protocol = []
    while len(proto) > 0:
        name, type_var_pairs, proto = ParsedStruct.parse_struct(proto)
        protocol.append(ParsedStruct(name, type_var_pairs))
    print(protocol)
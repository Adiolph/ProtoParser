# https://docs.python.org/3/library/struct.html

import struct

data_skill = (-1, 1)
proto_skill = struct.Struct("<iH")
data_skill_s = proto_skill.pack(*data_skill)

# pack
data_friends = (1, 2, 3, 4, 5)
data_friends_num = len(data_friends)
proto_friends = struct.Struct(f"<H{data_friends_num}i")
data_fridents_s = proto_friends.pack(data_friends_num, *data_friends)
print(data_fridents_s.hex())
# unpack
data_friends_num = struct.unpack("<H", data_fridents_s[0:2])[0]
data_size = data_friends_num * 4
data_friends = struct.unpack(f"<{data_friends_num}i", data_fridents_s[2:2+data_size])


data_name = "骨精灵"
data_name_b = data_name.encode(encoding='UTF-8', errors='strict')
print(data_name_b.hex())
data_name_num = 2*len(data_name_b)
proto_name = struct.Struct(f"<H")
data_name_s = proto_name.pack(data_name_num) + data_name_b

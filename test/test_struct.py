# https://docs.python.org/3/library/struct.html

import struct

data_skill = (-1, 1)
proto_skill = struct.Struct("<iH")
data_skill_s = proto_skill.pack(*data_skill)

# pack
data_friends = (1, 2, 3, 4, 5)
data_friends_num = len(data_friends)
proto_friends = struct.Struct("<H{}i".format(data_friends_num))
data_fridents_s = proto_friends.pack(data_friends_num, *data_friends)
print(data_fridents_s)
# unpack
data_friends_num = struct.unpack("<H", data_fridents_s[0:2])[0]
data_size = data_friends_num * 4
data_friends = struct.unpack("<{}i".format(data_friends_num), data_fridents_s[2:2+data_size])


data_name = "骨精灵a2"
len(data_name)
print(data_name)
data_name_num = len(data_name)
proto_name = struct.Struct("<H")
data_name_s = proto_name.pack(data_name_num) + data_name

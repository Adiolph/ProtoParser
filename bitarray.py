class BitArray:
    """
    Container to manipulate bit in python.
    Main methods: write_bit, write_char, read_bit, read_char
    Reference:
    - https://github.com/scott-griffiths/bitstring
    """

    def __init__(self) -> None:
        self.raw_array = bytearray()
        self.bit_offset_w = 0  # write
        self.bit_offset_r = 0  # read
        self.byte_length = 0

    @staticmethod
    def from_bytes(input_bytes: bytes, num_bit = 0):
        bit_array = BitArray()
        bit_array.bit_offset_w = num_bit
        bit_array.raw_array = bytearray(input_bytes)
        return bit_array

    def to_bytes(self) -> bytes:
        return bytes(self.raw_array)

    def print_binary(self):
        for i in range(self.byte_length):
            print("{:08b}".format(self.raw_array[i]))

    def print_hex(self):
        print(self.raw_array.hex())

    def __repr__(self) -> str:
        return self.raw_array.hex()

    def __len__(self) -> int:
        return self.bit_offset_w

    def check_full(self) -> None:
        if self.bit_offset_w == self.byte_length * 8:
            self.byte_length += 1
            self.raw_array.append(0)

    def write_bit(self, bit: int) -> None:
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

    def write_char(self, char: str) -> None:
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
    def __init__(self) -> None:
        self.raw_array = []
        self.bit_offset_r = 0  # read

    def __repr__(self) -> str:
        return str(self.raw_array)

    def __len__(self) -> int:
        return len(self.raw_array)

    def write_bit(self, bit: int):
        self.raw_array.append(bit)

    def write_char(self, char: str):
        self.write_bit(char)

    def reset_read_head(self):
        self.bit_offset_r = 0

    def read_bit(self) -> int:
        bit = self.raw_array[self.bit_offset_r]
        self.bit_offset_r += 1
        return bit

    def read_char(self) -> str:
        return self.read_bit()


if __name__ == "__main__":
    arr = BitArray()
    print("Writing")
    # 0 - 8
    arr.write_bit(1)
    arr.write_bit(0)
    arr.write_bit(0)
    arr.write_bit(1)
    arr.write_bit(1)
    arr.write_bit(1)
    arr.write_bit(0)
    arr.write_bit(1)
    # 8 - 12
    arr.write_bit(0)
    arr.write_bit(1)
    arr.write_bit(1)
    arr.write_bit(0)
    arr.write_bit(1)
    # char
    arr.write_char("a")

    print("Writing result:")
    arr.print_binary()

    print("Reading: ")
    arr.reset_read_head()
    for i in range(13):
        print(arr.read_bit())
    print(arr.read_char())

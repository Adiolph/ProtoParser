class BitArray:
    """
    Container to manipulate bit in python.
    Main methods: write_bits, write_char, read_bit, read_char
    Reference:
    - https://github.com/scott-griffiths/bitstring
    """

    def __init__(self):
        # the main internal data strucuture of bit array
        self.raw_array = bytearray()
        # a temp buffer to accelerate writting
        self.write_buffer = ""
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

    def write_bits(self, bits):
        """
        append 0/1 bit string into the bit array
        """
        self.write_buffer += bits
        while len(self.write_buffer) >= 8:
            self.raw_array.append(int(self.write_buffer[:8:], 2))
            self.write_buffer = self.write_buffer[8::]
            self.bit_offset_w += 8
    
    def flush(self):
        if self.write_buffer:
            self.bit_offset_w += len(self.write_buffer)
            self.write_buffer = self.write_buffer.ljust(8, '0')
            self.raw_array.append(int(self.write_buffer, 2))

    def write_char(self, char):
        """
        append a char into the bit array
        """
        char_bits = "{:08b}".format(ord(char))
        self.write_bits(char_bits)

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

    def write_bits(self, bits):
        self.raw_array.append(bits)

    def write_char(self, char):
        self.write_bits(char)

    def reset_read_head(self):
        self.bit_offset_r = 0

    def read_bit(self):
        bit = self.raw_array[self.bit_offset_r]
        self.bit_offset_r += 1
        return bit

    def read_char(self):
        return self.read_bit()


if __name__ == "__main__":
    arr = BitArray()
    print("Writing")
    # 0 - 8
    arr.write_bits("1")
    arr.write_bits("0")
    arr.write_bits("0")
    arr.write_bits("1")
    arr.write_bits("1")
    arr.write_bits("1")
    arr.write_bits("0")
    arr.write_bits("1")
    # 8 - 12
    arr.write_bits("0")
    arr.write_bits("1")
    arr.write_bits("1")
    arr.write_bits("0")
    arr.write_bits("1")
    # char
    arr.write_char("a")
    # flush
    arr.flush()

    print("Writing result:")
    arr.print_binary()

    print("Reading: ")
    arr.reset_read_head()
    for i in range(13):
        print(arr.read_bit())
    print(arr.read_char())

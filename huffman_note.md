
# Test encode input
- "A": 01100000
- " ": 11
- "H": 0110011
- "u": 011011
- "f": 00100

- 110 0000 -> 96
- 101 1001 -> 217
- 011 011  -> 

pass

# Test encode tree

## text

AAAAAABCCCCCCDDEEEEE

## Huffman tree 

   root
  /     \
 / \    / \
A   C  E  / \
         D   B

## Huffman dict

{
    'B': '111', 
    'D': '110', 
    'E': '10', 
    'C': '01', 
    'A': '00'
}

## Tree encode

### Text version

001A1C01E01D1B

### Binary version
00101000
00110100
00110101
00010101
01000100
10100001
00000000

## Text encode

00000000
00001110
10101010
10111011
01010101
01000000
from __future__ import annotations
from dataclasses import dataclass

from constants.huffman_codes import HuffmanCodes
from constants.huffman_lengths import HuffmanLengths


huffman_codes = HuffmanLengths.HUFFMAN_CODES
huffman_lengths = HuffmanLengths.HUFFMAN_CODES



class HPACKError(Exception):
    pass

class HPACKDecodeError(HPACKError):
    pass

class HPACKEncodeError(HPACKError):
    pass

def encode_integer(value: int, prefix_bits: int) -> bytes:
    limit = (1 << prefix_bits) - 1

    if value < limit:
        return value.to_bytes(1, "big")

    output = bytearray()
    output.append(limit)

    value -= limit

    while value >= 128:
        output.append((value % 128) + 128)
        value //= 128

    output.append(value)
    return bytes(output)


def decode_integer(prefix_value: int, prefix_bits: int, data: bytes) -> object:
    limit = (1 << prefix_bits) - 1 # = (2 ** prefix_bits) - 1

    if prefix_value < limit:
        return prefix_value
    else:
        prefix_value = limit
        shift = 0
                                                                                                                                
        for byte in data:
            prefix_value += (byte & 127) * 2 ** shift
            shift += 7

            if byte & 128 == 0:
                return prefix_value

            if shift > 63:
                raise HPACKDecodeError("Integer too large")

        raise HPACKDecodeError("Int Error")
    
    
def encode_string(huffman_table, data):
    """
    bit_buffer = 0
    bit_count = 0
    output = empty byte array

    for each byte in data:

        code = h[byte]
        code_length = length[byte]

        bit_buffer = (bit_buffer << code_length) OR code
        bit_count = bit_count + code_length

        while bit_count >= 8:
            bit_count = bit_count - 8
            output_byte = (bit_buffer >> bit_count) AND 0xFF
            append output_byte to output
            bit_buffer = bit_buffer AND ((1 << bit_count) - 1)

    if bit_count > 0:
        padding = 8 - bit_count
        bit_buffer = bit_buffer << padding
        bit_buffer = bit_buffer OR ((1 << padding) - 1)
        append bit_buffer to output
    return output
    """

    bit_buffer = 0
    bit_count = 0
    output = bytearray()

    for byte in data:
        code, code_length = huffman_table[byte]

        bit_buffer = (bit_buffer << code_length) | code
        bit_count += code_length

        while bit_count >= 8:
            bit_count -= 8
            output_byte = (bit_buffer >> bit_count) & 0xFF
            output.append(output_byte)
            bit_buffer &= (1 << bit_count) - 1

    if bit_count > 0:
        padding = 8 - bit_count
        bit_buffer <<= padding
        bit_buffer |= (1 << padding) - 1
        output.append(bit_buffer)

    return output


class Node:
    def __init__(self, index, left=None, right=None):
        self.index: int | None = index
        self.left: Node | None = left
        self.right: Node | None = right


def huffman_tree(huffman_codes):
    """
    root = new Node

    for symbol from 0 to 256:
        code, length = table[symbol]
        node = root

        for bit_position from length - 1 down to 0:
            bit = (code >> bit_position) AND 1

            if bit == 0:
                if node.zero does not exist:
                    node.zero = new Node
                node = node.zero
            else:
                if node.one does not exist:
                    node.one = new Node
                node = node.one
        
        node.symbol = symbol
    return root    
    """
    root = Node(None, None)

    for index, (code, code_length) in enumerate(huffman_codes):
        node = root
        for bit_position in range(code_length - 1, -1, -1):
            bit = (code >> bit_position) & 1

            if bit == 0:
                if node.left is None:
                    node.left = Node(None, None)
                node = node.left
            else:
                if node.right is None:
                    node.right = Node(None, None) 

                node = node.right

        node.index = index
    
    return root
            

def decode_string(data):
    """
    output = empty byte array
    node = tree

    for each byte in data:
        for bit_position from 7 down to 0:
            bit = (byte >> bit_position) AND 1

            if bit is 0:
                node = node.left
            else:
                node = node.right

            if node does not exist:
                error "Invalid Huffman encoding"

            if node.index is not empty:
                if node.index is EOS:
                    error "Unexpected EOS"
                append node.index to output
                node = tree

    validate remaining bits as padding

    return output
    """
    output = bytearray()

    root = huffman_tree(huffman_codes)
    node = root

    padding_bits = 0
    padding_value = 0

    for byte in data:
        for bit_position in range(7, -1, -1):
            bit = (byte >> bit_position) & 1

            padding_bits += 1
            padding_value = (padding_value << 1) | bit

            node = node.right if bit else node.left

            if node is None:
                raise HPACKDecodeError("Invalid Huffman encoding")

            if node.index is not None:
                if node.index == 256:
                    raise HPACKDecodeError("Unexpected EOS")

                output.append(node.index)

                node = root
                padding_bits = 0
                padding_value = 0

    if padding_bits > 7:
        raise HPACKDecodeError("Invalid Huffman padding")

    if padding_bits > 0:
        if padding_value != (1 << padding_bits) - 1:
            raise HPACKDecodeError("Invalid Huffman padding")

    return bytes(output)

data = b"www.example.com"

encoded = encode_string(HuffmanLengths.HUFFMAN_CODES, data)
decoded = decode_string(encoded)

print(encoded.hex())
print(decoded)
print(decoded == data)



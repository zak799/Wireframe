from __future__ import annotations
from dataclasses import dataclass

class HPACKError(Exception):
    pass

class HPACKDecodeError(HPACKError):
    pass

class HPACKEncodeError(HPACKError):
    pass

def encode_integer(i: int, n: int) -> bytes:
    limit = (1 << n) - 1

    if i < limit:
        return i.to_bytes(1, "big")

    output = bytearray()
    output.append(limit)

    i -= limit

    while i >= 128:
        output.append((i % 128) + 128)
        i //= 128

    output.append(i)
    return bytes(output)


def decode_integer(i: int, n: int, data: bytes) -> object:
    limit = (1 << n) - 1 # = (2 ** n) - 1

    if i < limit:
        return i
    else:
        i = limit
        m = 0
                                                                                                                                
        for byte in data:
            i += (byte & 127) * 2 ** m
            m += 7

            if byte & 128 == 0:
                return i

        raise HPACKDecodeError("Int Error")
    
    
def encode_string(h, length, data):
    ...

def decode_string():
    ...


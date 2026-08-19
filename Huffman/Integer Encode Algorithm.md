## [Prerequisites](https://datatracker.ietf.org/doc/html/rfc7541#section-5.1)

   Decoding the integer value from the list of octets starts by
   reversing the order of the octets in the list.  Then, for each octet,
   its most significant bit is removed.  The remaining bits of the
   octets are concatenated, and the resulting value is increased by
   2^N-1 to obtain the integer value.

   The prefix size, N, is always between 1 and 8 bits.  An integer
   starting at an octet boundary will have an 8-bit prefix.


---

## Pseudocode

Pseudocode to represent an integer `I` is as follows:
```
if I < 2^N - 1, encode I on N bits
else
    encode (2^N - 1) on N bits
    I = I - (2^N - 1)
    while I >= 128
        encode (I % 128 + 128) on 8 bits
             = I / 128
    encode I on 8 bits
```

That pseudocode was too complicated, so simplified, with better descriptions:

```
limit = 2^N - 1
if I is smaller than limit:
    write I as an N-bit integer
else:
    write limit as an N-bit integer
    subtract limit from I

    while I is at least 128:
        write the lowest 7 bits of I
        set the highest bit to 1
        divide I by 128

    write the remaining I as an 8-bit integer
```


---

### Scrap Notes
Will probably require bitwise ops to deter limit? `(1 << n) - 1` becomes the limit.
 - Mersenne number: `2^N - 1` == `(1 << n) - 1`

Might need to convert into binary repr - why? need to transfer and store binary data through HTTP
- `to_bytes`?
	 - `int.from_bytes(data, 'big')` - syntax
	     - `"Big"` = Big Endian order (Most Significant Byte) is places at lowest so numbers are                 in a left to right order.
	
- `bytearray()` - we need the returned array to be **mutable** as data may need to be changed.


---


***Final Implementation***:
```py
def _encode_integer(i: int, n: int) -> bytes:

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
```

----
## HPACK ENCODE IMPLEMENTATION


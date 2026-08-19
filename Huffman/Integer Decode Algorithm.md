## [Prerequisites]([https://datatracker.ietf.org/doc/html/rfc7541#section-5.1](https://datatracker.ietf.org/doc/html/rfc7541#section-5.1:~:text=HPACK%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20May%202015-,Pseudocode,-to%20decode%20an))

   This integer representation allows for values of indefinite size.  It
   is also possible for an encoder to send a large number of zero
   values, which can waste octets and could be used to overflow integer
   values.  Integer encodings that exceed implementation limits -- in
   value or octet length -- MUST be treated as decoding errors.
   Different limits can be set for each of the different uses of
   integers, based on implementation constraints.


---

Pseudocode to represent an integer `I` is as follows:
```
decode I from the next N bits
if I < 2^N - 1, return I
else
    M = 0
    repeat
        B = next octet
        I = I + (B & 127) * 2^M
        M = M + 7
    while B & 128 == 128
    return I
```

That pseudocode was too complicated, so simplified, with better descriptions:

```
Read the first N bits as I

If I < 2^N - 1:
    Return I

I = 2^N - 1
M = 0

Repeat:
    Read the next byte as B
    I = I + (B & 127) * 2^M
    M = M + 7

    If B & 128 == 0:
        Return I
```


---
### Notes

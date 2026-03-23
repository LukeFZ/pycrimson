# This is the JenkinsHash "hashlittle2" function with a different constant.
import struct

_M = 0xFFFFFFFF

_CHECKSUM_ELEMENT = struct.Struct("<III")


def _rot(x: int, k: int) -> int:
    return ((x << k) | (x >> (32 - k))) & _M


def _mix(a: int, b: int, c: int) -> tuple[int, int, int]:
    a = ((a - c) ^ _rot(c, 4)) & _M
    c = (c + b) & _M
    b = ((b - a) ^ _rot(a, 6)) & _M
    a = (a + c) & _M
    c = ((c - b) ^ _rot(b, 8)) & _M
    b = (b + a) & _M
    a = ((a - c) ^ _rot(c, 16)) & _M
    c = (c + b) & _M
    b = ((b - a) ^ _rot(a, 19)) & _M
    a = (a + c) & _M
    c = ((c - b) ^ _rot(b, 4)) & _M
    b = (b + a) & _M
    return a, b, c


def _final(a: int, b: int, c: int) -> tuple[int, int, int]:
    c = ((c ^ b) - _rot(b, 14)) & _M
    a = ((a ^ c) - _rot(c, 11)) & _M
    b = ((b ^ a) - _rot(a, 25)) & _M
    c = ((c ^ b) - _rot(b, 16)) & _M
    a = ((a ^ c) - _rot(c, 4)) & _M
    b = ((b ^ a) - _rot(a, 14)) & _M
    c = ((c ^ b) - _rot(b, 24)) & _M
    return a, b, c


def calculate_checksum(value: bytes | str) -> int:
    data = value.encode() if isinstance(value, str) else bytes(value)

    length = len(data)
    a = b = c = (length + 0xDEBA1DCD) & _M

    offset = 0
    remaining = length

    while remaining > 12:
        w0, w1, w2 = _CHECKSUM_ELEMENT.unpack_from(data, offset)
        a = (a + w0) & _M
        b = (b + w1) & _M
        c = (c + w2) & _M
        a, b, c = _mix(a, b, c)
        offset += 12
        remaining -= 12

    if remaining == 0:
        return c

    tail = data[offset:] + b"\x00" * (12 - remaining)
    w0, w1, w2 = struct.unpack("<III", tail)
    a = (a + w0) & _M
    b = (b + w1) & _M
    c = (c + w2) & _M

    _, _, c = _final(a, b, c)
    return c


def validate_checksum(value: bytes | str, expected: int):
    calculated = calculate_checksum(value)
    assert calculated == expected, (
        f"Checksum mismatch: expected {hex(expected)}, got {calculated}"
    )

def fnv1a32(val: bytes) -> int:
    hash_ = 0x811C9DC5

    for byte in val:
        hash_ = hash_ ^ byte
        hash_ = (hash_ * 0x01000193) % 0x100000000

    return hash_


def fnv1a16(val: bytes) -> int:
    hash_ = fnv1a32(val)
    return (hash_ >> 16) ^ (hash_ & 0xFFFF)


def fnv(val: str) -> int:
    return fnv1a16(val.encode())

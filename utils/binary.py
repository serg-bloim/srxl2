def add_bit(n: int, bit: int | bool) -> int:
    return (n << 1) | (int(bit) & 0b1)


def set_bit(v: int, bit_pos, bit_value=1):
    bit_mask = 1 << bit_pos
    if bit_value:
        return v | bit_mask
    else:
        return v & (~bit_mask)

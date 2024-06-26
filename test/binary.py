import struct
import unittest

from utils.binary import add_bit, set_bit


class MyTestCase(unittest.TestCase):
    def test_bitwise(self):
        v = 0b0
        v |= 0b1
        v <<= 1
        v |= 0b1

        print(bin(v))

    def test_add_bit(self):
        v = add_bit(0, 1)
        v = add_bit(v, 0)
        v = add_bit(v, 1)
        v = add_bit(v, 1)
        v = add_bit(v, 0)
        v = add_bit(v, 1)
        self.assertEqual(v, 0b101101)

    def test_struct_endianes(self):
        v = 32768
        print(struct.pack('H', v).hex(' ').upper())
        print(struct.pack('>H', v).hex(' ').upper())
        print(struct.pack('<H', v).hex(' ').upper())
        print(struct.pack('>5s', b'12345').hex(' ').upper())
        print(struct.pack('<5s', b'12345').hex(' ').upper())
        print(struct.pack('csc', b'a', b'12345', b'b').hex(' ').upper())

    def test_crc16(self):
        v = 32768
        print(struct.pack('H', v).hex(' ').upper())
        print(struct.pack('>H', v).hex(' ').upper())
        print(struct.pack('<H', v).hex(' ').upper())
        print(struct.pack('>5s', b'12345').hex(' ').upper())
        print(struct.pack('<5s', b'12345').hex(' ').upper())
        print(struct.pack('csc', b'a', b'12345', b'b').hex(' ').upper())

    def test_set_bit(self):
        v = 0b101001
        c = set_bit(v, 1)
        self.assertEqual('0b101011', bin(c))
        c = set_bit(v, 3)
        self.assertEqual(bin(v), bin(c))
        c = set_bit(v, 3, 0)
        self.assertEqual('0b100001', bin(c))
        c = set_bit(v, 2, 0)
        self.assertEqual(bin(v), bin(c))


if __name__ == '__main__':
    unittest.main()

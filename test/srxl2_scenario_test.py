import logging
import math
import time
import unittest

from protocols.srxl2 import SRXL2
from test.srxl2_test_utils import create_remote_receiver_device
from utils.common import delay

SERIAL_PORT = 'COM3'

logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler()])


class MyTestCase2(unittest.TestCase):
    def test_scenario1(self):
        device = create_remote_receiver_device()
        srxl2 = SRXL2(device, SERIAL_PORT)
        with srxl2.connect() as ser:
            delay(22)
            ser.write(b'\x00\x01\x02\x03')
            delay(22)
            srxl2.send_handshake(0x1)
            delay(22)
            srxl2.send_handshake(0x2)
            delay(22)
            srxl2.send_handshake(0x31)
            delay(22)
            srxl2.send_handshake(0x31)
            delay(22)
            srxl2.send_handshake(0xff)
            delay(22)
            while True:
                v = math.sin(time.time() / 2)
                v = int(v * 0x6000 + 0x8000)
                srxl2.send_control({0: v, 1: v, 2: v, 3: v, 4: v})
                delay(22)
            delay(5000)
            print("Response:")
            for line in ser.readlines():
                print(str(line))


if __name__ == '__main__':
    unittest.main()

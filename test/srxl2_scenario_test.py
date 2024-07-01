import math
import time
import unittest

from protocols.srxl2 import SRXL2
from srxl2_test_utils import create_remote_receiver_device
from utils.common import delay
from utils.my_logging import get_logger

SERIAL_PORT = 'loop://'
get_logger()

class MyTestCase2(unittest.TestCase):
    def test_scenario1(self):
        device = create_remote_receiver_device()
        srxl2 = SRXL2(device, SERIAL_PORT)
        with srxl2.connect() as ser:
            ser.write(b'\x00\x01\x02\x03')
            srxl2.send_handshake(0x1)
            srxl2.send_handshake(0x2)
            srxl2.send_handshake(0x31)
            srxl2.send_handshake(0x31)
            srxl2.send_handshake(0xff)
            while True:
                v = math.sin(time.time() / 2)
                v = int(v * 0x6000 + 0x8000)
                srxl2.send_control({0: v, 1: v, 2: v, 3: v, 4: v})
            delay(5000)
            print("Response:")
            for line in ser.readlines():
                print(str(line))


if __name__ == '__main__':
    unittest.main()

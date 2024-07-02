import math
import time
import unittest

from protocols.srxl2 import SRXL2, SRXL2Handshake, Srxl2PackType
from srxl2_test_utils import create_remote_receiver_device, create_student_device, create_transmitter_device
from utils.common import delay, normalize
from utils.my_logging import get_logger

SERIAL_PORT = 'COM3'


class MyTestCase2(unittest.TestCase):
    def test_scenario1(self):
        device = create_student_device()
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
                v = int(normalize(v, -1, 1, 0x2AA0, 0xD554))
                v &= 0xFFFC
                ch5_safe_mode = 0xD540  # beginner
                ch5_safe_mode = 0x8000  # advanced
                ch5_safe_mode = 0x2AC0  # expert
                ch6_no_panic = 0xD540  # no panic
                # ch6_no_panic = 0x8000  # maybe panic
                # ch6_no_panic = 0x2AC0  # maybe panic
                srxl2.send_control({0: v, 1: v, 2: v, 3: v, 4: ch5_safe_mode, 5: ch6_no_panic, 6: ch5_safe_mode})
                # srxl2.send_control({5: v, 6: 0xD540})
            delay(5000)
            print("Response:")
            for line in ser.readlines():
                print(str(line))

    def test_simulate_transmitter(self):
        device = create_transmitter_device()
        srxl2 = SRXL2(device, SERIAL_PORT, timeframe_ms=0)
        i = 0
        with srxl2.connect() as ser:
            while True:
                for msg in srxl2.read_all_ready_msgs():
                    i += 1
                    print(f"msg read: {i}")
                    if msg.p_type == Srxl2PackType.HANDSHAKE.value:
                        handshake = SRXL2Handshake.from_generic(msg)
                        if handshake.dst_id == device.id:
                            delay(2)
                            srxl2.send_handshake(handshake.src_id)
                            print(f"Got a Handshake request from {hex(handshake.src_id)} to me {hex(handshake.dst_id)}")


if __name__ == '__main__':
    unittest.main()

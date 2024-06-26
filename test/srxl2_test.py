import logging
import unittest

from protocols.srxl2 import SRXL2, DeviceDescriptor, TELEMETRY_RANGE
from utils.common import delay

logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler()])


def create_student_device():
    return DeviceDescriptor(b'\x52\x47\x53\x00', 0x10, TELEMETRY_RANGE.FLYBY)


def create_receiver_device():
    return DeviceDescriptor(b'\xA8\xD2\x1B\x0c', 0x21, TELEMETRY_RANGE.FLYBY)


class MyTestCase(unittest.TestCase):
    def test_handshake_1(self):
        device = create_student_device()
        srxl2 = SRXL2(device, '/dev/tty.usbserial-0001')
        with srxl2.connect():
            delay(22)
            srxl2.send_handshake(0xff)
            delay(22)

    def test_handshake(self):
        device = create_student_device()
        srxl2 = SRXL2(device, '/dev/tty.usbserial-0001')
        with srxl2.connect():
            for i in range(0x100):
                srxl2.send_handshake(0xff)
                delay(22)

    def test_handshake_all(self):
        device = create_student_device()
        srxl2 = SRXL2(device, '/dev/tty.usbserial-0001')
        with srxl2.connect():
            delay(50)
            for dev_id in range(0x100):
                srxl2.send_handshake(dev_id)
                delay(50)
                print(srxl2.serial.in_waiting)
                print(srxl2.serial.out_waiting)

    def test_handshake_all_src_id(self):
        device = create_student_device()
        srxl2 = SRXL2(device, '/dev/tty.usbserial-0001')
        with srxl2.connect():
            delay(50)
            for dev_id in range(0x100):
                srxl2.device.id = dev_id
                srxl2.send_handshake(0xff)
                delay(50)

    def test_control(self):
        device = create_student_device()
        srxl2 = SRXL2(device, 'loop://')
        with srxl2.connect():
            delay(50)
            # for dev_id in range(0x100):
            # srxl2.device.id = dev_id
            srxl2.send_control({
                0: 0x2a_c0,
                1: 0x7B_00,
                2: 0x98_B0,
                3: 0x75_40,
                4: 0x2a_c0,
                5: 0xD5_40,
                6: 0x2a_c0,
                7: 0x80_00,
            },rssi=0x9F, frame_losses=0xC)
            delay(50)


if __name__ == '__main__':
    unittest.main()

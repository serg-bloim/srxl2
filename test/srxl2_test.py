import unittest

import serial

from protocols.srxl2 import SRXL2
from srxl2_test_utils import create_remote_receiver_device, create_student_device
from utils.common import delay
from utils.my_logging import get_logger

SERIAL_PORT = 'COM3'

get_logger("MyTestCase")


class MyTestCase(unittest.TestCase):
    def test_handshake_1(self):
        device = create_remote_receiver_device()
        srxl2 = SRXL2(device, SERIAL_PORT)
        with srxl2.connect() as ser:
            delay(22)
            ser.write(b'\x00\x01\x02\x03')
            delay(22)
            srxl2.send_handshake(0x31)
            delay(22)
            srxl2.send_handshake(0x31)
            delay(22)
            srxl2.send_handshake(0x31)
            delay(22)
            srxl2.send_handshake(0xff)
            delay(22)
            print("Response:")
            print(ser.readlines())

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
        ser: serial.Serial
        with srxl2.connect() as ser:
            ser.setRTS(True)
            delay(500)
            ser.setRTS(False)
            delay(500)
            ser.setRTS(True)
            delay(500)
            ser.setRTS(False)
            delay(500)
            ser.setDTR(True)
            delay(500)
            ser.setDTR(False)
            delay(500)
            ser.setDTR(True)
            delay(500)
            ser.setDTR(False)
            delay(500)
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
            }, rssi=0x9F, frame_losses=0xC)
            delay(50)

    def test_control(self):
        device = create_student_device()
        srxl2 = SRXL2(device, 'loop://')
        with srxl2.connect():
            for src_id in range(0x100):
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
                }, rssi=0x9F, frame_losses=0xC)


if __name__ == '__main__':
    unittest.main()

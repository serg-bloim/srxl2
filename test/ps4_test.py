import glob
import struct
import sys
import unittest

import serial

from client.ps4serial import PS4Serial, PS4ControlPacket


class MyTestCase(unittest.TestCase):
    def test_list_ports(self):
        print("Serial ports:")
        for p in serial_ports():
            print(p)

    def test_serial_write(self):
        ps4 = PS4Serial("COM4", skip_crc_check=True)
        ps4.connect()
        with open("log.txt", "wt") as txt:
            with open("log.dat", "wb") as binf:
                i = 0
                while True:
                    i += 1
                    for msg in ps4.read_messages():
                        if msg.p_type == 0x10:
                            ctrl = PS4ControlPacket.from_generic(msg)

                            print(f"{i:<10} {ctrl.buttons_len} {ctrl.controls_len} {ctrl.gyro_len} {bin(ctrl.buttons)} {ctrl.sliders}")



def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


if __name__ == '__main__':
    unittest.main()

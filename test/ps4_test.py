import glob
import struct
import sys
import unittest

import serial

from client.ps4serial import PS4Serial


class MyTestCase(unittest.TestCase):
    def test_list_ports(self):
        print("Serial ports:")
        for p in serial_ports():
            print(p)

    def test_serial_write(self):
        ps4 = PS4Serial("/dev/tty.usbserial-10", skip_crc_check=True)
        ps4.connect()
        with open("log.txt", "wt") as txt:
            with open("log.dat", "wb") as bin:
                i = 0
                while True:
                    i += 1
                    for msg in ps4.read_messages():
                        if len(msg.data) == 4:
                            lx, ly, rx, ry = struct.unpack("4b", msg.data)
                            bin.write(i.to_bytes(4, 'big'))
                            bin.write(msg.data)
                            print(f"{i:<10} {lx} {ly} {rx} {ry} ", file=txt)

                            if lx == 82:
                                pass
                            else:
                                pass
                            print(f"{lx:>4}   {ly:>4}   {rx:>4}   {ry:>4}")


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

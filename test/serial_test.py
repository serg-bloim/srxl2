import glob
import sys
import unittest

import serial


class MyTestCase(unittest.TestCase):
    def test_list_ports(self):
        print("Serial ports:")
        for p in serial_ports():
            print(p)

    def test_serial_write(self):
        with serial.Serial('COM3', 115200, timeout=1) as ser:
            ser.write(b"hello from python\n")
            resp = ser.readall()
            print(resp)


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

import dataclasses
import struct
from typing import Iterator

import serial

from utils import crc16


@dataclasses.dataclass
class PS4Packet:
    p_type: int
    data: bytes

    def get_axis(self, control):
        return 0


class PS4Serial:
    _serial: serial.Serial

    def __init__(self, port: str) -> None:
        super().__init__()
        self.p_len = 0
        self.p_type = 0
        self.port = port
        self.data_processed = 0

    def connect(self):
        self._serial = serial.Serial(self.port)

    def read_messages(self) -> Iterator[PS4Packet]:
        if self._serial.in_waiting:
            while True:
                # Process if any packet body left for a previously read header
                if self.p_type:
                    if self._serial.in_waiting < self.p_len + 2:
                        break
                    data = self._serial.read(self.p_len)
                    crc = self._serial.read(2)
                    if self.check_crc(data, crc):
                        yield PS4Packet(self.p_type, data)
                        self.p_type, self.p_len = 0, 0
                # Look for a next header
                while self._serial.in_waiting > 3:
                    if self._serial.read() == b'\xA6':
                        break
                if self._serial.in_waiting < 3:
                    break
                header = self._serial.read(3)
                self.p_type, self.p_len, p_hend = struct.unpack("3B", header)
                if p_hend != 0xB5:
                    self.p_type, self.p_len = 0, 0

    def check_crc(self, data, p_crc):
        header = struct.pack('4B', 0xA6, self.p_type, self.p_len, 0xB5)
        crc = crc16.crc16xmodem(header)
        crc = crc16.crc16xmodem(data, crc)
        return crc.to_bytes(2, "big") == p_crc

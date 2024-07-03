import dataclasses
import logging
import struct
from typing import Iterator

import serial

from utils import crc16
from utils.my_logging import get_logger


@dataclasses.dataclass
class PS4Packet:
    p_type: int
    data: bytes


@dataclasses.dataclass
class PS4ControlPacket(PS4Packet):
    def __post_init__(self):
        data = self.data
        assert self.p_type == 0x10
        self.buttons_len, self.controls_len, self.gyro_len, self.buttons = struct.unpack_from("3BI", data)
        self.sliders = list(struct.unpack_from(f"{self.controls_len}b", data, 8))

    @staticmethod
    def from_generic(packet: PS4Packet) -> "PS4ControlPacket":
        return PS4ControlPacket(packet.p_type, packet.data)


logger = get_logger("PS4Serial")


class PS4Serial:
    _serial: serial.Serial

    def __init__(self, port: str, skip_crc_check=False) -> None:
        super().__init__()
        self.skip_crc_check = skip_crc_check
        self.p_len = 0
        self.p_type = 0
        self.port = port
        self.data_processed = 0

    def connect(self):
        self._serial = serial.Serial(self.port, 115200, timeout=0.001)

    def read_messages(self) -> Iterator[PS4Packet]:
        if self._serial.in_waiting:
            while True:
                # Process if any packet body left for a previously read header
                if self.p_type:
                    if self._serial.in_waiting < self.p_len + 2:
                        break
                    data = self._serial.read(self.p_len - 6)
                    crc = self._serial.read(2)
                    crc_actual = self.calc_crc(data)
                    crc_check = crc == crc_actual
                    if not crc_check:
                        logger.warn(f"Error while parsing message. CRC mismatch: {crc.hex(' ').upper()} != {crc_actual.hex(' ').upper()} ")
                    else:
                        pass
                    if self.skip_crc_check or crc_check:
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

    def calc_crc(self, data):
        header = struct.pack('4B', 0xA6, self.p_type, self.p_len, 0xB5)
        crc = crc16.crc16xmodem(header)
        crc = crc16.crc16xmodem(data, crc)
        return crc.to_bytes(2, "big")

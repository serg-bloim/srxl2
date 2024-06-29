import dataclasses
import logging
import struct
from enum import Enum
from typing import Dict

import serial

from utils import crc16
from utils.binary import set_bit


class TELEMETRY_RANGE(Enum):
    FULL = 1
    FLYBY = 2


@dataclasses.dataclass
class DeviceDescriptor:
    uid: bytes
    id: int
    supports_baud400 = False
    telemetry_enabled = False
    telemetry_range: TELEMETRY_RANGE = TELEMETRY_RANGE.FLYBY
    fwd_programming_enabled = False

    def get_info(self):
        return 1


class SRXL2:
    logger = logging.getLogger("SRXL2")

    def __init__(self, device: DeviceDescriptor, port: str):
        super().__init__()
        self.serial: serial.Serial = None
        self.device = device
        self.port = port

    def connect(self) -> serial.Serial:
        if self.port == 'loop://':
            self.serial = serial.serial_for_url(self.port, 115200, timeout=0.001)
        else:
            self.serial = serial.Serial(self.port, 115200, timeout=0.001)
        return self.serial

    def send_handshake(self, dst_id=0):
        packet = struct.pack('<5B4s', self.device.id, dst_id, 10, self.device.supports_baud400, self.device.get_info(), self.device.uid)
        message = self.prep_message(0x21, packet)
        self.send(message)

    pass

    @staticmethod
    def prep_message(p_type: int, data: bytes):
        header = struct.pack('3B', 0xA6, p_type, 5 + len(data))
        crc = crc16.crc16xmodem(header)
        crc = crc16.crc16xmodem(data, crc)
        pack = struct.pack(f'>3s{len(data)}sH', header, data, crc)
        return pack

    def send(self, msg):
        self.logger.debug(f"Sent msg ({len(msg)}): {msg.hex(' ').upper()}")
        self.serial.write(msg)
        self.serial.flush()

    def send_control(self, ch_data: Dict[int, int], cmd=0x0, reply_id=0x0, rssi=0, frame_losses=0):
        ch_mask = 0
        channels = [None] * 32
        for ch, dat in ch_data.items():
            ch_mask = set_bit(ch_mask, ch)
            channels[ch] = dat & 0xffff
        data = (c for c in channels if c is not None)
        packet = struct.pack(f'<2BBHI{len(ch_data)}H', cmd, reply_id, rssi, frame_losses, ch_mask, *data)
        message = self.prep_message(0xCD, packet)
        self.send(message)

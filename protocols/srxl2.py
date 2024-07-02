import dataclasses
import logging
import struct
import time
from enum import Enum
from queue import SimpleQueue
from typing import Dict

import serial

from utils import crc16
from utils.binary import set_bit
from utils.common import EventsHandler

SRXL2_PACKET_HANDSHAKE_FORMAT = '<5B4s'


class TELEMETRY_RANGE(Enum):
    FULL = 1
    FLYBY = 2


class Srxl2PackType(Enum):
    GENERIC = 0x0
    HANDSHAKE = 0x21
    BIND_INFO = 0x41
    PARAMETER_CONFIGURATION = 0x50
    SIGNAL_QUALITY = 0x55
    TELEMETRY_SENSOR_DATA = 0x80
    CONTROL_DATA = 0xCD


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


@dataclasses.dataclass
class SRXL2Packet:
    p_type: int = 0
    p_data: bytes = bytes()

    def len(self):
        return len(self.p_data) + 5


@dataclasses.dataclass
class SRXL2Handshake(SRXL2Packet):
    src_id: int = dataclasses.field(init=False)
    dst_id: int = dataclasses.field(init=False)
    priority: int = dataclasses.field(init=False)
    baud: int = dataclasses.field(init=False)
    info: int = dataclasses.field(init=False)
    uid: int = dataclasses.field(init=False)

    def __post_init__(self):
        data = self.p_data
        assert self.p_type == 0x21
        assert len(data) == 9
        self.src_id, self.dst_id, self.priority, self.baud, self.info, self.uid = struct.unpack(SRXL2_PACKET_HANDSHAKE_FORMAT, data)

    @staticmethod
    def from_generic(packet: SRXL2Packet) -> "SRXL2Handshake":
        return SRXL2Handshake(packet.p_type, packet.p_data)


class _State(Enum):
    NO_PACKET = 1,
    PACKET_HEADER = 2,
    PACKET_TYPE = 3,
    PACKET_LEN = 4,
    PACKET_DATA = 5,
    PACKET_CRC = 6,


class PacketBuilder:
    logger = logging.getLogger("PacketBuilder")
    state: _State = _State.NO_PACKET
    packet_type: int = None
    packet_len: int = None
    data: bytearray = None
    crc: bytearray = bytearray(2)
    data_processed: int = 0

    def process(self, byte: int):
        if self.state == _State.NO_PACKET and byte == 0xA6:
            self.state = _State.PACKET_HEADER
        elif self.state == _State.PACKET_HEADER:
            self.packet_type = byte
            self.state = _State.PACKET_LEN
        elif self.state == _State.PACKET_LEN:
            self.packet_len = byte
            if byte >= 5:
                self.state = _State.PACKET_DATA
                self.data = bytearray(self.packet_len - 5)
                self.data_processed = 0
            else:
                self.state = _State.NO_PACKET
        elif self.state == _State.PACKET_DATA:
            self.data[self.data_processed] = byte
            self.data_processed += 1
        elif self.state == _State.PACKET_CRC:
            self.crc[self.data_processed] = byte
            self.data_processed += 1

        if self.state == _State.PACKET_DATA and self.data_processed == len(self.data):
            self.state = _State.PACKET_CRC
            self.data_processed = 0
        if self.state == _State.PACKET_CRC and self.data_processed == 2:
            self.state = _State.NO_PACKET
            return self.release_packet()

    def release_packet(self):
        crc = self.calc_crc16()
        try:
            assert crc.to_bytes(2, "big", signed=False) == bytes(self.crc)
            return SRXL2Packet(self.packet_type, bytes(self.data))
        except:
            self.logger.warning("CRC check failed")
            pass

    def calc_crc16(self):
        header = struct.pack('3B', 0xA6, self.packet_type, 5 + len(self.data))
        return crc16.crc16xmodem(self.data, crc16.crc16xmodem(header))


class SRXL2Events:
    def on_before_message_sent(self, msg: SRXL2Packet):
        pass

    def on_after_message_sent(self, msg: SRXL2Packet):
        pass

    def on_message_received(self, msg: SRXL2Packet):
        pass


class SRXL2:
    logger = logging.getLogger("SRXL2")

    def __init__(self, device: DeviceDescriptor, port: str, timeframe_ms: int = 22):
        super().__init__()
        self.timeframe_s = timeframe_ms / 1000
        self.serial: serial.Serial = None
        self.device = device
        self.port = port
        self.last_packet_s = 0
        self.msg_queue: SimpleQueue[SRXL2Packet] = SimpleQueue()  # Infinite queue
        self.packet_builder = PacketBuilder()
        self.events: EventsHandler[SRXL2Events] = EventsHandler()

    def connect(self) -> serial.Serial:
        if self.port == 'loop://':
            self.serial = serial.serial_for_url(self.port, 115200, timeout=0.001)
        else:
            self.serial = serial.Serial(self.port, 115200, timeout=0.001)
        self.last_packet_s = time.time()
        return self.serial

    def send_handshake(self, dst_id=0):
        packet = struct.pack(SRXL2_PACKET_HANDSHAKE_FORMAT, self.device.id, dst_id, 10, self.device.supports_baud400, self.device.get_info(),
                             self.device.uid)
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
        next_timeframe = self.last_packet_s + self.timeframe_s
        delay = next_timeframe - time.time()
        if delay > 0:
            time.sleep(delay)
        self.last_packet_s = next_timeframe
        self.events.fire_event(SRXL2Events.on_before_message_sent, msg)
        self.serial.write(msg)
        self.serial.flush()
        self.events.fire_event(SRXL2Events.on_after_message_sent, msg)

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

    def read_all_ready_msgs(self):
        while self.has_next_msg():
            yield self.read_next_msg()

    def has_next_msg(self):
        self._read_available_data()
        return not self.msg_queue.empty()

    def _read_available_data(self):
        if self.serial.in_waiting:
            for byte in self.serial.read(self.serial.in_waiting):
                packet = self.packet_builder.process(byte)
                if packet:
                    self.msg_queue.put(packet)

    def read_next_msg(self):
        if not self.msg_queue.empty():
            return self.msg_queue.get(block=False)

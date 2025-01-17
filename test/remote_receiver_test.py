import logging
import unittest

from client.ps4serial import PS4Serial
from client.remote_receiver import RemoteReceiver, RemoteReceiverEvents
from protocols.srxl2 import SRXL2, Srxl2PackType, SRXL2Handshake, SRXL2Packet
from srxl2_test_utils import create_remote_receiver_device
from test.srxl2_test_utils import create_student_device
from utils.my_logging import get_logger

SERIAL_PORT = 'COM3'
logger = get_logger("RemoteReceiverTest")


class MyTestCase2(unittest.TestCase):
    def test_rr1(self):
        class Events(RemoteReceiverEvents):
            def on_message_received(self, msg):
                if msg.p_type == Srxl2PackType.HANDSHAKE:
                    handshake = SRXL2Handshake.from_generic(msg)
                    devices.add(handshake.src_id)

            def on_handshake_done(self, success):
                logger.info(f"Handshake is done {'successfully' if success else 'with failure'}\nDevices: {devices}")

            def on_after_message_sent(self, msg: SRXL2Packet):
                for msg in ps4.read_messages():
                    msg.get_axis("Lx")
                pass

        ps4 = PS4Serial("loop://")
        devices = set()
        device = create_student_device()
        rr = RemoteReceiver(SRXL2(device, SERIAL_PORT))
        rr.events.add_event_listener(Events())
        rr.begin()


if __name__ == '__main__':
    unittest.main()

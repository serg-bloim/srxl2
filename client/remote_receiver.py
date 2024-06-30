import dataclasses
import logging

from protocols.srxl2 import SRXL2, Srxl2PackType, SRXL2Handshake, SRXL2Events, SRXL2Packet
from utils.common import cap, EventsHandler


class RemoteReceiverEvents(SRXL2Events):
    def on_handshake_done(self, success: bool):
        pass


@dataclasses.dataclass
class ChannelHandler:
    enabled: bool = False
    val: float = 0

    def get_srxl_val(self):
        return int(cap(self.val, -1, 1) * 0x8000) + 0x8000


logger = logging.getLogger("RemoteReceiver")


class RemoteReceiver:
    def __init__(self, srxl_client: SRXL2) -> None:

        super().__init__()
        self.followers = None
        self._srxl2 = srxl_client
        self.events: EventsHandler[RemoteReceiverEvents] = EventsHandler()
        self._channels = [ChannelHandler() for n in range(32)]

        self._srxl2.events.add_event_listener(RemoteReceiver.SRXL2Events(self))

    def begin(self):
        with self._srxl2.connect() as ser:
            while True:
                if self.handshake():
                    self.main_cycle()

    def handshake(self):
        dev_ids = [0x11, 0x21, 0x30, 0x31, 0x40]
        self.followers = []
        for dev_id in dev_ids:
            self._srxl2.send_handshake(dev_id)
        for msg in self._srxl2.read_all_ready_msgs():
            if msg.p_type == Srxl2PackType.HANDSHAKE:
                msg = SRXL2Handshake.from_generic(msg)
                if msg.src_id != self._srxl2.device.id:
                    self.followers.append(msg.src_id)
                else:
                    logger.warning("Found my src_id in responses to me. Should not be like that.")
            else:
                logger.warning("Strange packet during handshake process.")
            pass
        if self.followers:
            self._srxl2.send_handshake(0xff)
            self.events.fire_event(RemoteReceiverEvents.on_handshake_done, True)
            return True
        else:
            logger.warning("No followers responded")
            self.events.fire_event(RemoteReceiverEvents.on_handshake_done, False)
            return False

    def main_cycle(self):
        while True:
            self._process_incoming_msgs()
            self._srxl2.send_control(self.prep_channel_data())

    def prep_channel_data(self):
        ch_data = {i: ch.get_srxl_val() for i, ch in enumerate(self._channels) if ch.enabled}
        return ch_data

    def _process_incoming_msgs(self):
        for msg in self._srxl2.read_all_ready_msgs():
            pass

    @dataclasses.dataclass
    class SRXL2Events(SRXL2Events):
        parent: "RemoteReceiver"

        def on_message_received(self, msg: SRXL2Packet):
            logger.info(f"Received message of type: {hex(msg.p_type)} x {msg.len()} len")
            self.parent.events.fire_event(RemoteReceiverEvents.on_message_received, msg)

        def on_before_message_sent(self, msg):
            logger.info(f"Sending message of type: {hex(msg.p_type)} x {msg.len()} len")
            self.parent.events.fire_event(RemoteReceiverEvents.on_before_message_sent, msg)
            pass

        def on_after_message_sent(self, msg):
            self.parent.events.fire_event(RemoteReceiverEvents.on_after_message_sent, msg)
            pass

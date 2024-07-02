from protocols.srxl2 import DeviceDescriptor, TELEMETRY_RANGE


def create_student_device():
    return DeviceDescriptor(b'\x52\x47\x53\x00', 0x10, TELEMETRY_RANGE.FLYBY)


def create_receiver_device():
    return DeviceDescriptor(b'\xA8\xD2\x1B\x0c', 0x21, TELEMETRY_RANGE.FLYBY)


def create_remote_receiver_device():
    return DeviceDescriptor(b'\x52\x47\x53\x00', 0x11, TELEMETRY_RANGE.FLYBY)

def create_transmitter_device():
    return DeviceDescriptor(b'\x52\x47\x53\x00', 0x31, TELEMETRY_RANGE.FLYBY)

import logging


def wrap_format(handler):
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s', datefmt='%M:%S')
    handler.setFormatter(formatter)
    return handler


logging.basicConfig(level=logging.DEBUG, handlers=[wrap_format(logging.StreamHandler())])


def get_logger(name):
    return logging.getLogger(name)

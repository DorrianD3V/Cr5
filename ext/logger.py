import logging
from colorlog import ColoredFormatter


level = logging.DEBUG

Logger = logging.getLogger(__name__)
Logger.setLevel(level)

stream = logging.StreamHandler()
stream.setLevel(level)
stream.setFormatter(ColoredFormatter('[%(asctime)s] %(log_color)s%(levelname)-8s%(reset)s | %(message)s%(reset)s'))

Logger.addHandler(stream)


import logging
logging.basicConfig(level=logging.DEBUG)
from gsmmodem.modem import GsmModem as GM
m = GM('/dev/ttyUSB1', 115200)
m.connect()

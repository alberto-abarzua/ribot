import serial
from serial.rfc2217 import Serial


class SerialCom:
    '''

        TODO:
        - Scan available ports and search for a esp32
        - Use argparse to specify a port
        - use the default espidf baudrate of 115200
        - Start a rfc2217 server on the port


    '''

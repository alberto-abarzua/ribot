import time
import os
from pathlib import Path
from arm_utils import bins

__author__ = "Alberto Abarzua"


class DummyArduino():
    """DummyArduino class, used for testing purposes. Simulates an arduino with serial comunication.
    """

    def __init__(self) -> None:
        """Constructor, creates a list to store all the lines (strings that end with a \n).
        """
        self.received_lines = []
        self.max_values = []
        # As this is a dummy arduino it should always be available.
        self.in_waiting = 12
        # 1 means the arduino is ready to receive instructions , 0 means it is working.
        self.output = "1"
        self.log = None
        self.wait = False
        p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.path = Path(os.path.join(p,"tests","test_data"))

    def set_log_file(self, filename):
        """Sets the name for the arduinoDummy log's file name (all the lines received)

        Args:
            filename (str): file where to store all lines received
        """
        self.log = open(self.path.joinpath(filename), "w")

    def readline(self):
        """Reads a line from arduino

        Returns:
            byte: enconded string.
        """
        return (str(self.output) + "\n").encode()

    def read(self, nbytes):
        """Reads nbytes from the serial buffer

        Args:
            nbytes (int): number of bytes
        """
        return self.output[:min(nbytes, len(self.output))].encode()

    def write(self, message):
        """Simulates the writing from serial to an arduino.

        Args:
            message (bytes): Encoded str that the arduino will receive.
        """

        message = bins.decode_message(message)
        message = str(message)
        self.received_lines.append(message)
        if (self.log != None):
            self.log.write(message + "\n")
        if (len(self.received_lines) > 100):
            self.received_lines.clear()
            self.max_values.clear()
        if (self.wait):
            time.sleep(5e-6)

    def max_value_from_command(self, command):
        """Gets the max value from a movement command:
        Example:
        "m7 0 0 0 0 50 0 0" -- > 50

        Args:
            command (str): move command to get the max value

        Returns:
            int: max value in the command
        """
        return max(command.args)

    def flush(self):
        pass

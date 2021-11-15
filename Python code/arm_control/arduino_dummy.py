
import time

__author__ = "Alberto Abarzua"

class DummyArduino():
    """DummyArduino class, used for testing purposes. Simulates an arduino with serial comunication.
    """
    def __init__(self) -> None:
        """Constructor, creates a list to store all the lines (strings that end with a \n).
        """
        self.received_lines = []
        self.output = "1" # 1 means the arduino is ready to receive instructions , 0 means it is working.

    def readline(self):
        """Reads a line from arduino

        Returns:
            byte: enconded string.
        """
        return (str(self.output) + "\n").encode()
    
    def write(self,message):
        """Simulates the writing from serial to an arduino.

        Args:
            message (bytes): Encoded str that the arduino will receive.
        """
        message = message.decode()
        self.received_lines.append(message)
        #Simulate the action
        self.output = "0"
        time.sleep(0.001)
        self.output= "1"
            


        

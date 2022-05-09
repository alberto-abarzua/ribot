
from dataclasses import dataclass

from numpy import character
import struct

class Message():
    """This class is used to encode the messages to the arduino as a series of bytes.
    All messages should follow this syntax:

    <Command> ::= <op> <code> <num_args> <args>* <end>

        <op> ::= <char>

        <code> ::= <int> 

        <num_args> ::= <int>

        <args> :: = <int>

        <end> ::= <char> //This is going to be ;
    
    """
    def __init__(self,op,code,args) -> None:
        self.op = op
        self.code = int(code)
        self.args= [int(arg) for arg in args]
        self.end = ";".encode()
        self.num_args = len(args)
    def encode(self):
        """Returns the message in bytes.
        """
        res = b""
        res+=self.op.encode()
        res+=struct.pack("i",self.code)
        res +=struct.pack("i",self.num_args)
        for arg in self.args:
            res+= struct.pack("i",arg)
        res+= self.end
        return res
        



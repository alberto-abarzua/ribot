
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
    def __init__(self,op,code,args = []) -> None:
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
    def __str__(self):
        return "{}{} ".format(self.op,self.code) + " ".join([str(x) for x in self.args])
        #return "OP: {}{} Aguments: {}".format(self.op,self.code,self.args)
def decode_message(bytes):
    """

    Args:
        bytes (b""): sequence of bytes

    Returns:
        Message: message that was stored in bytes.
    """
    op = str(struct.unpack_from("c",bytes,offset=0)[0].decode())
    code =int(struct.unpack_from("i",bytes,offset=1)[0])
    num_args = struct.unpack_from("i",bytes,offset=5)[0]
    args =[]
    for i in range(num_args):
        args.append(int(struct.unpack_from("i",bytes,i*4+9)[0]))

    return Message(op,code,args)



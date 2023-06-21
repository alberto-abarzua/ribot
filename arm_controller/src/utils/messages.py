import dataclasses
import struct
from utils.prints import console
__author__ = "Alberto Abarzua"


@dataclasses.dataclass
class Message:
    op: str
    code: int
    num_args: int
    args: list[float]


    def __init__(self,op: str, code: int, args: list[float]) -> None:
        self.op = op
        self.code = code
        self.num_args = len(args)
        self.args = args

    def __post_init__(self):
        error_msg_num_args = f"Number of arguments ({self.num_args}) does not match"
        error_msg_num_args += f" the length of the args list ({len(self.args)})"
        assert len(self.args) == self.num_args, error_msg_num_args
        assert isinstance(self.op, str), f"op must be a string, not {type(self.op)}"
        assert isinstance(self.code, int), f"code must be an int, not {type(self.code)}"
        assert isinstance(
            self.num_args, int
        ), f"num_args must be an int, not {type(self.num_args)}"
        assert isinstance(self.args, list), f"args must be a list, not {type(self.args)}"
        for arg in self.args:
            assert isinstance(arg, float), f"args must be a list of floats, not {type(arg)}"
        assert len(self.op) == 1, f"op must be a single character, not {self.op}"

    def encode(self):
        return struct.pack(
            "<cii" + "f" * len(self.args), self.op.encode(), self.code, self.num_args, *self.args
        )

    @staticmethod
    def decode(bytes):
        op, code, num_args = struct.unpack_from("<bii", bytes, offset=0)
        args = struct.unpack_from("<" + "f" * num_args, bytes, offset=9)
        return Message(op, code, num_args, args)

    def __str__(self):
        return (
            f"op: {self.op}, code: {self.code}, num_args: {self.num_args}, args: {self.args}"
        )

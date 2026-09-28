from dataclasses import dataclass
from enum import Enum


class OpCode(Enum):
    # XXX = ("XXX", arity)
    IPUSH = ("IPUSH", 1)
    POP = ("POP", 0)
    DUP = ("DUP", 0)

    LOADG = ("LOADG", 1)
    STOREG = ("STOREG", 1)
    LOADA = ("LOADA", 1)
    STOREA = ("STOREA", 1)
    LOADL = ("LOADL", 1)
    STOREL = ("STOREL", 1)

    IADD = ("IADD", 0)
    ISUB = ("ISUB", 0)
    IMUL = ("IMUL", 0)
    IDIV = ("IDIV", 0)
    INEG = ("INEG", 0)
    # --- opcodes for future language extensions ---
    IMOD = ("IMOD", 0)
    INOT = ("INOT", 0)
    # --- end of extension opcodes ---
    IEQ = ("IEQ", 0)
    INE = ("INE", 0)
    ILT = ("ILT", 0)
    ILE = ("ILE", 0)
    IGT = ("IGT", 0)
    IGE = ("IGE", 0)

    JMP = ("JMP", 1)
    JPZ = ("JPZ", 1)

    CALL = ("CALL", 1)
    ALLOC = ("ALLOC", 1)
    RET = ("RET", 0)
    CLEAN = ("CLEAN", 1)

    CPRINT = ("CPRINT", 0)
    HALT = ("HALT", 0)

    def __init__(self, mnemonic: str, arity: int):
        self.mnemonic = mnemonic
        self.arity = arity


@dataclass(frozen=True)
class Instruction:
    op: OpCode
    arg: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.op, OpCode):
            raise TypeError(f"op must be OpCode, got {type(self.op).__name__}")

        if self.op.arity == 0 and self.arg is not None:
            raise ValueError(f"{self.op.mnemonic} takes no argument")

        if self.op.arity == 1 and self.arg is None:
            raise ValueError(f"{self.op.mnemonic} requires an argument")

    def __repr__(self) -> str:
        if self.op.arity == 0:
            return self.op.mnemonic

        return f"{self.op.mnemonic} {self.arg}"

from .errors import VMError
from .instruction import Instruction
from .instruction import OpCode


class VirtualMachine:
    def __init__(
        self,
        code: list[Instruction],
        global_count: int = 0,
    ) -> None:
        self.code = code
        self.globals = [0] * global_count
        self.stack = [0] * 10000

        self.pc = 0
        self.sp = 0
        self.max_sp = 0 # for testing purposes
        self.fp = 0
        self.output: list[str] = []

        self.validate_code()

    def validate_code(self) -> None:
        for index, inst in enumerate(self.code):
            if not isinstance(inst, Instruction):
                raise VMError(
                    f"code[{index}] is not Instruction: {type(inst).__name__}"
                )

            if not isinstance(inst.op, OpCode):
                raise VMError(
                    f"code[{index}] has invalid opcode type: {type(inst.op).__name__}"
                )

            if inst.op.arity == 0 and inst.arg is not None:
                raise VMError(
                    f"code[{index}] {inst.op.mnemonic} must not have an argument"
                )

            if inst.op.arity == 1 and inst.arg is None:
                raise VMError(f"code[{index}] {inst.op.mnemonic} requires an argument")

    def push(self, value: int) -> None:
        self.stack[self.sp] = value
        self.sp += 1
        self.max_sp = max(self.max_sp, self.sp)

    def pop(self) -> int:
        if self.sp <= 0:
            raise VMError("stack underflow")

        self.sp -= 1
        return self.stack[self.sp]

    def format_instruction(self, inst: Instruction) -> str:
        if inst.op.arity == 0:
            return inst.op.mnemonic

        return f"{inst.op.mnemonic} {inst.arg}"

    def trace_state(self, inst: Instruction) -> None:
        print("-" * 50)
        print(f"NEXT : {self.format_instruction(inst)}")
        print(f"pc={self.pc}  sp={self.sp}  fp={self.fp}")
        print(f"stack  : {self.stack[: self.sp]}")
        print(f"globals: {self.globals}")

    def trace_halt(self) -> None:
        print("=" * 50)
        print("HALT")
        if self.sp > 0:
            print(f"result = {self.stack[self.sp - 1]}")
        print(f"pc={self.pc}  sp={self.sp}  fp={self.fp}")
        print(f"stack  : {self.stack[: self.sp]}")
        print(f"globals: {self.globals}")
        print("=" * 50)

    def check_global_index(self, index: int) -> None:
        if index < 0 or index >= len(self.globals):
            raise RuntimeError(f"global index out of range: {index}")

    def run(self, trace: bool = False) -> list[str]:
        while True:
            if not (0 <= self.pc < len(self.code)):
                raise VMError(f"invalid PC: {self.pc}")

            inst = self.code[self.pc]
            op = inst.op
            arg = inst.arg if inst.arg is not None else 0

            if trace:
                self.trace_state(inst)

            if op == OpCode.IPUSH:
                self.push(arg)
                self.pc += 1

            elif op == OpCode.POP:
                self.pop()
                self.pc += 1

            elif op == OpCode.DUP:
                if self.sp <= 0:
                    raise VMError("stack underflow on DUP")

                value = self.stack[self.sp - 1]
                self.push(value)
                self.pc += 1

            elif op == OpCode.LOADG:
                self.check_global_index(arg)
                value = self.globals[arg]
                self.push(value)
                self.pc += 1

            elif op == OpCode.STOREG:
                self.check_global_index(arg)
                value = self.pop()
                self.globals[arg] = value
                self.pc += 1

            elif op == OpCode.LOADA:
                value = self.stack[self.fp - (2 + arg)]
                self.push(value)
                self.pc += 1

            elif op == OpCode.STOREA:
                value = self.pop()
                self.stack[self.fp - (2 + arg)] = value
                self.pc += 1

            elif op == OpCode.LOADL:
                value = self.stack[self.fp + (1 + arg)]
                self.push(value)
                self.pc += 1

            elif op == OpCode.STOREL:
                value = self.pop()
                self.stack[self.fp + (1 + arg)] = value
                self.pc += 1

            elif op == OpCode.IADD:
                right = self.pop()
                left = self.pop()
                self.push(left + right)
                self.pc += 1

            elif op == OpCode.ISUB:
                right = self.pop()
                left = self.pop()
                self.push(left - right)
                self.pc += 1

            elif op == OpCode.IMUL:
                right = self.pop()
                left = self.pop()
                self.push(left * right)
                self.pc += 1

            elif op == OpCode.IDIV:
                right = int(self.pop())
                left = int(self.pop())
                self.push(left // right)
                self.pc += 1

            elif op == OpCode.IMOD:
                # TODO: EX2-3 Extending the Semantic Analyzer and Code Generator
                # Execute the integer modulo operation according to the VM specification.
                self.pc += 1

            elif op == OpCode.INOT:
                # TODO: EX2-3 Extending the Semantic Analyzer and Code Generator
                # Execute the integer logical NOT operation according to the VM specification.
                self.pc += 1

            elif op == OpCode.INEG:
                value = self.pop()
                self.push(-value)
                self.pc += 1

            elif op == OpCode.IEQ:
                right = self.pop()
                left = self.pop()
                self.push(1 if left == right else 0)
                self.pc += 1

            elif op == OpCode.INE:
                right = self.pop()
                left = self.pop()
                self.push(1 if left != right else 0)
                self.pc += 1

            elif op == OpCode.ILT:
                right = self.pop()
                left = self.pop()
                self.push(1 if left < right else 0)
                self.pc += 1

            elif op == OpCode.ILE:
                right = self.pop()
                left = self.pop()
                self.push(1 if left <= right else 0)
                self.pc += 1

            elif op == OpCode.IGT:
                right = self.pop()
                left = self.pop()
                self.push(1 if left > right else 0)
                self.pc += 1

            elif op == OpCode.IGE:
                right = self.pop()
                left = self.pop()
                self.push(1 if left >= right else 0)
                self.pc += 1

            elif op == OpCode.JMP:
                self.pc = arg

            elif op == OpCode.JPZ:
                value = self.pop()

                if value == 0:
                    self.pc = arg
                else:
                    self.pc += 1

            elif op == OpCode.CALL:
                return_address = self.pc + 1
                old_fp = self.fp

                self.push(return_address)
                self.push(old_fp)

                self.fp = self.sp - 1
                self.pc = arg

            elif op == OpCode.ALLOC:
                for _ in range(arg):
                    self.push(0)

                self.pc += 1

            elif op == OpCode.RET:
                return_value = self.pop()

                old_fp = self.stack[self.fp]
                return_address = self.stack[self.fp - 1]

                self.sp = self.fp - 1
                self.fp = old_fp

                self.push(return_value)
                self.pc = return_address

            elif op == OpCode.CLEAN:
                return_value = self.pop()
                self.sp = self.sp - arg
                self.push(return_value)
                self.pc += 1

            elif op == OpCode.CPRINT:
                value = self.pop()
                self.output.append(chr(value))
                print(chr(value), end="")
                self.pc += 1

            elif op == OpCode.HALT:
                if trace:
                    self.trace_halt()
                return self.output

            else:
                raise VMError(f"unknown opcode: {op}")

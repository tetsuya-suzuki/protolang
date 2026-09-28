from .instruction import Instruction
from .instruction import OpCode
from .semantic import ProgramInfo

JUMP_OPS = {OpCode.JMP.mnemonic, OpCode.JPZ.mnemonic, OpCode.CALL.mnemonic}


def build_function_name_map(program_info: ProgramInfo) -> dict[int, str]:
    name_map: dict[int, str] = {}

    for function_info in program_info.functions_map.values():
        if function_info.address is not None:
            name_map[function_info.address] = function_info.name

    return name_map


class AssemblyFormatter:
    def __init__(self, program_info: ProgramInfo, global_count: int) -> None:
        self.program_info = program_info
        self.global_count = global_count
        self.function_name_map = build_function_name_map(program_info)

    def label_width(self, code: list[Instruction]) -> int:
        return max(2, len(str(max(0, len(code) - 1))))

    def format_label(self, address: int, width: int) -> str:
        return f"L{address:0{width}d}"

    def format_instruction(self, inst: Instruction, width: int) -> str:
        op = inst.op
        arg = inst.arg

        if op.arity == 0:
            return op.mnemonic

        if op.mnemonic in JUMP_OPS:
            if arg is None:
                raise ValueError(f"{op.mnemonic} requires an argument")
            target = arg
            text = f"{op.mnemonic} {self.format_label(target, width)}"
            function_name = self.function_name_map.get(target)
            if function_name is not None:
                text += f" ; {function_name}"
            return text

        return f"{op.mnemonic} {arg}"

    def format_comment(self, address: int) -> str:
        function_name = self.function_name_map.get(address)
        if function_name is None:
            return ""
        return f" ; {function_name}"

    def format_program(self, code: list[Instruction]) -> str:
        width = self.label_width(code)
        lines = [f".globals {self.global_count}"]

        for address, inst in enumerate(code):
            label = self.format_label(address, width)
            text = self.format_instruction(inst, width)
            comment = self.format_comment(address)
            lines.append(f"{label}: {text}{comment}")

        return "\n".join(lines)

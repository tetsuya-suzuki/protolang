from __future__ import annotations

from dataclasses import dataclass

from .asm_parser import AsmBlock
from .asm_parser import AsmDirective
from .asm_parser import AsmInstruction
from .asm_parser import parse_asm_source
from .diagnostics import DiagnosticReporter
from .errors import AssemblerError
from .instruction import Instruction
from .instruction import OpCode
from .token import SourceSpan


@dataclass(frozen=True)
class AssemblyResult:
    code: list[Instruction]
    global_count: int
    unresolved_calls: list[tuple[int, str]]
    unresolved_call_spans: dict[int, SourceSpan]


class AsmLowerer:
    def __init__(
        self,
        block: AsmBlock,
        *,
        global_count: int = 0,
        function_targets: dict[str, int] | None = None,
        reporter: DiagnosticReporter | None = None,
    ) -> None:
        self.block = block
        self.global_count = global_count
        self.function_targets = function_targets or {}
        self.reporter = reporter
        self.labels: dict[str, int] = {}
        self.unresolved_calls: list[tuple[int, str]] = []
        self.unresolved_call_spans: dict[int, SourceSpan] = {}

    def lower(self) -> AssemblyResult:
        self.first_pass()
        code = self.second_pass()
        return AssemblyResult(
            code=code,
            global_count=self.global_count,
            unresolved_calls=self.unresolved_calls,
            unresolved_call_spans=self.unresolved_call_spans,
        )

    def _report_or_raise(self, error: AssemblerError) -> None:
        if self.reporter is None:
            raise error
        if error.line is not None and error.column is not None:
            self.reporter.error(error.message, error.line, error.column)
        else:
            self.reporter.error_at_span(error.message, self.block.span)

    def first_pass(self) -> None:
        pc = 0
        globals_seen = False
        for line in self.block.lines:
            if line.label is not None:
                if line.label in self.labels:
                    self._report_or_raise(
                        AssemblerError(
                            f"duplicate label: {line.label}",
                            line=line.span.start.line,
                            column=line.span.start.column,
                        )
                    )
                else:
                    self.labels[line.label] = pc
            if isinstance(line.item, AsmDirective):
                if line.item.name == ".globals":
                    if globals_seen:
                        self._report_or_raise(
                            AssemblerError(
                                "duplicate .globals directive",
                                line=line.item.span.start.line,
                                column=line.item.span.start.column,
                            )
                        )
                        continue
                    if line.item.operand is None:
                        continue
                    value = int(line.item.operand)
                    if value < 0:
                        self._report_or_raise(
                            AssemblerError(
                                ".globals operand must be non-negative",
                                line=line.item.span.start.line,
                                column=line.item.span.start.column,
                            )
                        )
                        continue
                    self.global_count = value
                    globals_seen = True
                continue
            if isinstance(line.item, AsmInstruction):
                pc += 1

    def second_pass(self) -> list[Instruction]:
        code: list[Instruction] = []
        for line in self.block.lines:
            if isinstance(line.item, AsmInstruction):
                inst = self.lower_instruction(line.item, len(code))
                if inst is not None:
                    code.append(inst)
        return code

    def lower_instruction(self, node: AsmInstruction, pc: int) -> Instruction | None:
        try:
            opcode = OpCode[node.mnemonic]
        except KeyError as exc:
            error = AssemblerError(
                f"unknown opcode: {node.mnemonic}",
                line=node.span.start.line,
                column=node.span.start.column,
            )
            if self.reporter is None:
                raise error from exc
            self._report_or_raise(error)
            return None

        if opcode.arity == 0:
            if node.operand is not None:
                self._report_or_raise(
                    AssemblerError(
                        f"{opcode.mnemonic} takes no operand",
                        line=node.span.start.line,
                        column=node.span.start.column,
                    )
                )
                return None
            return Instruction(opcode)

        if node.operand is None:
            self._report_or_raise(
                AssemblerError(
                    f"{opcode.mnemonic} requires one operand",
                    line=node.span.start.line,
                    column=node.span.start.column,
                )
            )
            return None

        arg = self.resolve_operand(opcode, node.operand, pc, node)
        if arg is None:
            return None
        return Instruction(opcode, arg)

    def resolve_operand(
        self,
        opcode: OpCode,
        operand: int | str,
        pc: int,
        node: AsmInstruction,
    ) -> int | None:
        if isinstance(operand, int):
            return operand
        if opcode in {OpCode.JMP, OpCode.JPZ}:
            if operand not in self.labels:
                self._report_or_raise(
                    AssemblerError(
                        f"undefined label: {operand}",
                        line=node.span.start.line,
                        column=node.span.start.column,
                    )
                )
                return None
            return self.labels[operand]
        if opcode == OpCode.CALL:
            if operand in self.labels:
                return self.labels[operand]
            if operand in self.function_targets:
                return self.function_targets[operand]
            self.unresolved_calls.append((pc, operand))
            self.unresolved_call_spans[pc] = node.span
            return 0
        self._report_or_raise(
            AssemblerError(
                f"{opcode.mnemonic} operand must be an integer",
                line=node.span.start.line,
                column=node.span.start.column,
            )
        )
        return None


def assemble_block(
    block: AsmBlock,
    *,
    function_targets: dict[str, int] | None = None,
    global_count: int = 0,
    reporter: DiagnosticReporter | None = None,
) -> AssemblyResult:
    return AsmLowerer(
        block,
        global_count=global_count,
        function_targets=function_targets,
        reporter=reporter,
    ).lower()


def assemble_source(
    source: str,
    *,
    reporter: DiagnosticReporter | None = None,
) -> AssemblyResult:
    block = parse_asm_source(source, reporter=reporter)
    return assemble_block(block, reporter=reporter)

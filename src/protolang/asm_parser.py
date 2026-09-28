from __future__ import annotations

from dataclasses import dataclass

from .ast import ASTNode
from .diagnostics import DiagnosticReporter
from .token import SourceLocation, SourceSpan
from .errors import AssemblerError


@dataclass
class AsmDirective(ASTNode):
    name: str
    operand: str | None


@dataclass
class AsmInstruction(ASTNode):
    mnemonic: str
    operand: int | str | None


@dataclass
class AsmLine(ASTNode):
    label: str | None
    item: AsmDirective | AsmInstruction | None


@dataclass
class AsmBlock(ASTNode):
    lines: list[AsmLine]

    def declared_functions(self) -> set[str]:
        result: set[str] = set()
        for line in self.lines:
            if (
                isinstance(line.item, AsmDirective)
                and line.item.name == ".function"
                and line.item.operand is not None
            ):
                result.add(line.item.operand)
        return result

    def labels(self) -> set[str]:
        return {line.label for line in self.lines if line.label is not None}


def _make_span(
    line: int,
    start_col: int,
    end_col: int,
    *,
    line_offset: int = 0,
    col_offset: int = 0,
) -> SourceSpan:
    actual_line = line + line_offset
    actual_start = start_col + (col_offset if line == 1 else 0)
    actual_end = end_col + (col_offset if line == 1 else 0)
    return SourceSpan(
        start=SourceLocation(actual_line, actual_start),
        end=SourceLocation(actual_line, actual_end),
    )


def _is_ident(text: str) -> bool:
    if not text:
        return False
    if not (text[0].isalpha() or text[0] == "_"):
        return False
    return all(ch.isalnum() or ch == "_" for ch in text)


def _report_or_raise(
    reporter: DiagnosticReporter | None,
    error: AssemblerError,
) -> None:
    if reporter is None:
        raise error

    if error.line is not None and error.column is not None:
        reporter.error(error.message, error.line, error.column)
    else:
        reporter.error(error.message, 1, 1)


def parse_asm_source(
    source: str,
    *,
    line_offset: int = 0,
    col_offset: int = 0,
    reporter: DiagnosticReporter | None = None,
) -> AsmBlock:
    lines: list[AsmLine] = []
    for lineno, raw_line in enumerate(source.splitlines(), start=1):
        line_no_comment = raw_line.split(";", 1)[0]
        if not line_no_comment.strip():
            continue

        label: str | None = None
        rest = line_no_comment
        colon = line_no_comment.find(":")
        if colon != -1:
            maybe_label = line_no_comment[:colon].strip()
            if maybe_label:
                if not _is_ident(maybe_label):
                    error = AssemblerError(
                        f"invalid label: {maybe_label}",
                        line=lineno + line_offset,
                        column=1 + (col_offset if lineno == 1 else 0),
                    )
                    _report_or_raise(reporter, error)
                    rest = line_no_comment[colon + 1 :]
                else:
                    label = maybe_label
                    rest = line_no_comment[colon + 1 :]

        rest = rest.strip()
        item: AsmDirective | AsmInstruction | None = None
        if rest:
            start_col = raw_line.find(rest) + 1
            try:
                if rest.startswith("."):
                    item = _parse_directive(
                        rest,
                        lineno,
                        start_col,
                        line_offset=line_offset,
                        col_offset=col_offset,
                    )
                else:
                    item = _parse_instruction(
                        rest,
                        lineno,
                        start_col,
                        line_offset=line_offset,
                        col_offset=col_offset,
                    )
            except AssemblerError as error:
                _report_or_raise(reporter, error)

        span = _make_span(
            lineno,
            1,
            max(1, len(raw_line) + 1),
            line_offset=line_offset,
            col_offset=col_offset,
        )
        lines.append(AsmLine(span, label, item))

    if lines:
        span = SourceSpan.combine(lines[0].span, lines[-1].span)
    else:
        span = _make_span(1, 1, 1, line_offset=line_offset, col_offset=col_offset)
    return AsmBlock(span, lines)


def _parse_directive(
    text: str, lineno: int, start_col: int, *, line_offset: int, col_offset: int
) -> AsmDirective:
    parts = text.split()
    name = parts[0]
    operand = parts[1] if len(parts) > 1 else None
    if len(parts) > 2:
        raise AssemblerError(
            f"{name} takes at most one operand",
            line=lineno + line_offset,
            column=start_col + (col_offset if lineno == 1 else 0),
        )
    if name not in {".globals", ".function"}:
        raise AssemblerError(
            f"unknown directive: {name}",
            line=lineno + line_offset,
            column=start_col + (col_offset if lineno == 1 else 0),
        )
    if operand is None:
        raise AssemblerError(
            f"{name} requires one operand",
            line=lineno + line_offset,
            column=start_col + (col_offset if lineno == 1 else 0),
        )
    if name == ".globals":
        try:
            int(operand)
        except ValueError as exc:
            raise AssemblerError(
                ".globals operand must be an integer",
                line=lineno + line_offset,
                column=start_col + (col_offset if lineno == 1 else 0),
            ) from exc
    elif not _is_ident(operand):
        raise AssemblerError(
            f"invalid function name: {operand}",
            line=lineno + line_offset,
            column=start_col + (col_offset if lineno == 1 else 0),
        )
    span = _make_span(
        lineno,
        start_col,
        start_col + len(text),
        line_offset=line_offset,
        col_offset=col_offset,
    )
    return AsmDirective(span, name, operand)


def _parse_instruction(
    text: str, lineno: int, start_col: int, *, line_offset: int, col_offset: int
) -> AsmInstruction:
    parts = text.split()
    mnemonic = parts[0]
    if not mnemonic.isupper():
        raise AssemblerError(
            f"mnemonic must be uppercase: {mnemonic}",
            line=lineno + line_offset,
            column=start_col + (col_offset if lineno == 1 else 0),
        )
    if len(parts) > 2:
        raise AssemblerError(
            "instructions take at most one operand",
            line=lineno + line_offset,
            column=start_col + (col_offset if lineno == 1 else 0),
        )
    operand: int | str | None = None
    if len(parts) == 2:
        operand_text = parts[1]
        if operand_text.lstrip("-").isdigit():
            operand = int(operand_text)
        elif _is_ident(operand_text):
            operand = operand_text
        else:
            raise AssemblerError(
                f"invalid operand: {operand_text}",
                line=lineno + line_offset,
                column=start_col + (col_offset if lineno == 1 else 0),
            )
    span = _make_span(
        lineno,
        start_col,
        start_col + len(text),
        line_offset=line_offset,
        col_offset=col_offset,
    )
    return AsmInstruction(span, mnemonic, operand)

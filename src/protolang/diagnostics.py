from dataclasses import dataclass
from enum import Enum
from typing import TextIO

from .token import SourceLocation
from .token import SourceSpan


class DiagnosticLevel(Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class Diagnostic:
    level: DiagnosticLevel
    message: str
    span: SourceSpan
    source_line: str | None = None
    filename: str | None = None

    @property
    def line(self) -> int:
        return self.span.start.line

    @property
    def column(self) -> int:
        return self.span.start.column


class DiagnosticReporter:
    def __init__(self, source: str = "", filename: str | None = None) -> None:
        self._diagnostics: list[Diagnostic] = []
        self._source_lines = source.splitlines()
        self.filename = filename

    def make_span(
        self,
        line: int,
        column: int,
        end_line: int | None = None,
        end_column: int | None = None,
    ) -> SourceSpan:
        if end_line is None:
            end_line = line
        if end_column is None:
            end_column = column + 1

        return SourceSpan(
            start=SourceLocation(line, column),
            end=SourceLocation(end_line, end_column),
        )

    def add(
        self,
        level: DiagnosticLevel,
        message: str,
        line: int,
        column: int,
        end_line: int | None = None,
        end_column: int | None = None,
    ) -> None:
        self.add_span(
            level,
            message,
            self.make_span(line, column, end_line, end_column),
        )

    def add_span(
        self,
        level: DiagnosticLevel,
        message: str,
        span: SourceSpan,
    ) -> None:
        source_line = None
        if 1 <= span.start.line <= len(self._source_lines):
            source_line = self._source_lines[span.start.line - 1]

        self._diagnostics.append(
            Diagnostic(
                level=level,
                message=message,
                span=span,
                source_line=source_line,
                filename=self.filename,
            )
        )

    def error(
        self,
        message: str,
        line: int,
        column: int,
        end_line: int | None = None,
        end_column: int | None = None,
    ) -> None:
        self.add(DiagnosticLevel.ERROR, message, line, column, end_line, end_column)

    def warning(
        self,
        message: str,
        line: int,
        column: int,
        end_line: int | None = None,
        end_column: int | None = None,
    ) -> None:
        self.add(
            DiagnosticLevel.WARNING,
            message,
            line,
            column,
            end_line,
            end_column,
        )

    def error_at_span(self, message: str, span: SourceSpan) -> None:
        self.add_span(DiagnosticLevel.ERROR, message, span)

    def warning_at_span(self, message: str, span: SourceSpan) -> None:
        self.add_span(DiagnosticLevel.WARNING, message, span)

    def extend(self, diagnostics: list[Diagnostic]) -> None:
        self._diagnostics.extend(diagnostics)

    def has_errors(self) -> bool:
        return any(d.level == DiagnosticLevel.ERROR for d in self._diagnostics)

    def has_warnings(self) -> bool:
        return any(d.level == DiagnosticLevel.WARNING for d in self._diagnostics)

    def sorted_diagnostics(self) -> list[Diagnostic]:
        return sorted(
            self._diagnostics,
            key=lambda d: (
                d.line,
                d.column,
                0 if d.level == DiagnosticLevel.ERROR else 1,
                d.message,
            ),
        )

    def _underline_width(self, diagnostic: Diagnostic) -> int:
        if diagnostic.span.start.line != diagnostic.span.end.line:
            return 1

        width = diagnostic.span.end.column - diagnostic.span.start.column
        return max(width, 1)

    def format_diagnostic(self, diagnostic: Diagnostic) -> str:
        location_prefix = ""
        if diagnostic.filename:
            location_prefix = f"{diagnostic.filename}:"

        lines = [
            f"{location_prefix}{diagnostic.line}:{diagnostic.column}: "
            f"{diagnostic.level.value}: {diagnostic.message}"
        ]

        if diagnostic.source_line is not None:
            lines.append(f"    {diagnostic.source_line}")
            caret_column = max(diagnostic.column - 1, 0)
            underline = "^" * self._underline_width(diagnostic)
            lines.append("    " + " " * caret_column + underline)

        return "\n".join(lines)

    def format(self) -> str:
        return "\n\n".join(self.format_diagnostic(d) for d in self.sorted_diagnostics())

    def print(self, stream: TextIO | None = None) -> None:
        if stream is None:
            import sys

            stream = sys.stdout

        text = self.format()
        if text:
            print(text, file=stream)

    def __len__(self) -> int:
        return len(self._diagnostics)

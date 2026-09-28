from dataclasses import dataclass
from enum import Enum, auto


class TokenKind(Enum):
    FUNCTION = auto()
    VAR = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    # --- keywords for future language extensions ---
    DO = auto()
    REPEAT = auto()
    UNTIL = auto()
    # --- end of extension keywords ---
    RETURN = auto()
    ASM = auto()

    IDENT = auto()
    NUMBER = auto()

    ASSIGN = auto()
    EQ = auto()
    NE = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()

    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    # --- operators for future language extensions ---
    PERCENT = auto()
    LAND = auto()
    LOR = auto()
    LNOT = auto()
    # -- end of extension operators ---

    COMMA = auto()
    SEMICOLON = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()

    EOF = auto()


@dataclass(frozen=True, order=True)
class SourceLocation:
    line: int
    column: int


@dataclass(frozen=True)
class SourceSpan:
    start: SourceLocation
    end: SourceLocation

    @staticmethod
    def combine(first: "SourceSpan", second: "SourceSpan") -> "SourceSpan":
        return SourceSpan(start=first.start, end=second.end)


@dataclass(frozen=True)
class Token:
    kind: TokenKind
    value: int | str | None = None
    span: SourceSpan | None = None

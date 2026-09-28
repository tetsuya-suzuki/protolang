import string

from .diagnostics import DiagnosticReporter
from .token import SourceLocation
from .token import SourceSpan
from .token import Token
from .token import TokenKind


class Lexer:
    def __init__(self, text: str, reporter: DiagnosticReporter | None = None) -> None:
        self.text = text
        self.reporter = reporter
        self.index = 0
        self.line = 1
        self.column = 1
        self.next_char: str | None = None
        self.next_line = 1
        self.next_column = 1

        self.spaces = set(string.whitespace)
        self.digits = set(string.digits)
        self.letters = set(string.ascii_letters)

        self.advance()

    def advance(self) -> None:
        if self.index < len(self.text):
            ch = self.text[self.index]
            self.next_char = ch
            self.next_line = self.line
            self.next_column = self.column
            self.index += 1

            if ch == "\n":
                self.line += 1
                self.column = 1
            else:
                self.column += 1
        else:
            self.next_char = None
            self.next_line = self.line
            self.next_column = self.column

    def is_space(self, ch: str | None) -> bool:
        return ch is not None and ch in self.spaces

    def is_digit(self, ch: str | None) -> bool:
        return ch is not None and ch in self.digits

    def is_letter(self, ch: str | None) -> bool:
        return ch is not None and ch in self.letters

    def is_identifier_start(self, ch: str | None) -> bool:
        return self.is_letter(ch) or ch == "_"

    def is_identifier_part(self, ch: str | None) -> bool:
        return self.is_identifier_start(ch) or self.is_digit(ch)

    def make_span(
        self,
        start_line: int,
        start_column: int,
        end_line: int,
        end_column: int,
    ) -> SourceSpan:
        return SourceSpan(
            start=SourceLocation(start_line, start_column),
            end=SourceLocation(end_line, end_column),
        )

    def current_span(self) -> SourceSpan:
        return self.make_span(
            self.next_line,
            self.next_column,
            self.next_line,
            self.next_column + 1,
        )

    def skip_spaces(self) -> None:
        while self.is_space(self.next_char):
            self.advance()

    def report_error(
        self,
        message: str,
        line: int,
        column: int,
        end_line: int | None = None,
        end_column: int | None = None,
    ) -> None:
        if self.reporter is not None:
            self.reporter.error(message, line, column, end_line, end_column)

    def capture_until_matching_rbrace(self) -> tuple[str, SourceSpan]:
        start_line = self.next_line
        start_column = self.next_column
        chars: list[str] = []

        while self.next_char is not None and self.next_char != "}":
            chars.append(self.next_char)
            self.advance()

        if self.next_char != "}":
            self.report_error(
                "expected '}' to close asm block",
                start_line,
                start_column,
                self.next_line,
                self.next_column,
            )
            return "".join(chars), self.make_span(
                start_line,
                start_column,
                self.next_line,
                self.next_column,
            )

        end_line = self.next_line
        end_column = self.next_column + 1
        self.advance()
        return "".join(chars), self.make_span(
            start_line, start_column, end_line, end_column
        )

    def get_next_token(self) -> Token:
        self.skip_spaces()

        if self.next_char is None:
            return Token(
                TokenKind.EOF,
                span=self.make_span(
                    self.next_line,
                    self.next_column,
                    self.next_line,
                    self.next_column,
                ),
            )

        if self.is_digit(self.next_char):
            start_line = self.next_line
            start_column = self.next_column
            lexeme = self.next_char
            self.advance()

            while self.is_digit(self.next_char):
                lexeme += self.next_char
                self.advance()

            return Token(
                TokenKind.NUMBER,
                int(lexeme),
                self.make_span(
                    start_line,
                    start_column,
                    self.next_line,
                    self.next_column,
                ),
            )

        if self.is_identifier_start(self.next_char):
            start_line = self.next_line
            start_column = self.next_column
            lexeme = self.next_char
            self.advance()

            while self.is_identifier_part(self.next_char):
                lexeme += self.next_char
                self.advance()

            keywords = {
                "function": TokenKind.FUNCTION,
                "var": TokenKind.VAR,
                "if": TokenKind.IF,
                "else": TokenKind.ELSE,
                "while": TokenKind.WHILE,
                "return": TokenKind.RETURN,
                "asm": TokenKind.ASM,
                # TODO: EX2-1 Extending the Lexer
                # Add the keywords "do", "repeat", and "until" to the keywords table
            }

            kind = keywords.get(lexeme)
            span = self.make_span(
                start_line,
                start_column,
                self.next_line,
                self.next_column,
            )
            if kind is not None:
                return Token(kind, span=span)

            return Token(TokenKind.IDENT, lexeme, span)

        if self.next_char == "=":
            start_line = self.next_line
            start_column = self.next_column
            self.advance()
            if self.next_char == "=":
                self.advance()
                return Token(
                    TokenKind.EQ,
                    span=self.make_span(
                        start_line,
                        start_column,
                        self.next_line,
                        self.next_column,
                    ),
                )
            return Token(
                TokenKind.ASSIGN,
                span=self.make_span(
                    start_line,
                    start_column,
                    self.next_line,
                    self.next_column,
                ),
            )

        # TODO: EX2-1 Extending the Lexer
        # Support the logical AND (&&) as a token.

        # TODO: EX2-1 Extending the Lexer
        # Support the logical OR (||) as a token.

        if self.next_char == "!":
            start_line = self.next_line
            start_column = self.next_column
            self.advance()
            if self.next_char == "=":
                self.advance()
                return Token(
                    TokenKind.NE,
                    span=self.make_span(
                        start_line,
                        start_column,
                        self.next_line,
                        self.next_column,
                    ),
                )

            # TODO: EX2-1 Extending the Lexer
            # Support the logical NOT operator (!) as a token.
            self.report_error("unexpected '!'", start_line, start_column)
            return self.get_next_token()

        if self.next_char == "<":
            start_line = self.next_line
            start_column = self.next_column
            self.advance()
            if self.next_char == "=":
                self.advance()
                return Token(
                    TokenKind.LE,
                    span=self.make_span(
                        start_line,
                        start_column,
                        self.next_line,
                        self.next_column,
                    ),
                )
            return Token(
                TokenKind.LT,
                span=self.make_span(
                    start_line,
                    start_column,
                    self.next_line,
                    self.next_column,
                ),
            )

        if self.next_char == ">":
            start_line = self.next_line
            start_column = self.next_column
            self.advance()
            if self.next_char == "=":
                self.advance()
                return Token(
                    TokenKind.GE,
                    span=self.make_span(
                        start_line,
                        start_column,
                        self.next_line,
                        self.next_column,
                    ),
                )
            return Token(
                TokenKind.GT,
                span=self.make_span(
                    start_line,
                    start_column,
                    self.next_line,
                    self.next_column,
                ),
            )

        one_char_tokens = {
            "+": TokenKind.PLUS,
            "-": TokenKind.MINUS,
            "*": TokenKind.STAR,
            "/": TokenKind.SLASH,
            ",": TokenKind.COMMA,
            ";": TokenKind.SEMICOLON,
            "(": TokenKind.LPAREN,
            ")": TokenKind.RPAREN,
            "{": TokenKind.LBRACE,
            "}": TokenKind.RBRACE,
            # TODO: EX2-1 Extending the Lexer
            # Add the modulo operator (%) to the one_char_token table.
        }

        kind = one_char_tokens.get(self.next_char)
        if kind is not None:
            span = self.current_span()
            self.advance()
            return Token(kind, span=span)

        self.report_error(
            f"invalid character: {self.next_char!r}",
            self.next_line,
            self.next_column,
        )
        self.advance()
        return self.get_next_token()

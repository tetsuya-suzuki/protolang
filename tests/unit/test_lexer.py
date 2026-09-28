import unittest

from protolang.diagnostics import DiagnosticReporter
from protolang.lexer import Lexer
from protolang.token import TokenKind


class LexerTests(unittest.TestCase):
    def collect_kinds(self, source: str):
        lexer = Lexer(source)
        kinds = []

        while True:
            token = lexer.get_next_token()
            kinds.append(token.kind)

            if token.kind == TokenKind.EOF:
                return kinds

    def test_keywords_and_symbols(self):
        """Tokenize ProtoLang keywords and symbols"""
        source = "function main() { return 1; }"

        actual = self.collect_kinds(source)

        expected = [
            TokenKind.FUNCTION,
            TokenKind.IDENT,
            TokenKind.LPAREN,
            TokenKind.RPAREN,
            TokenKind.LBRACE,
            TokenKind.RETURN,
            TokenKind.NUMBER,
            TokenKind.SEMICOLON,
            TokenKind.RBRACE,
            TokenKind.EOF,
        ]

        self.assertEqual(actual, expected)

    def test_asm_keyword(self):
        """Tokenize the asm keyword"""
        actual = self.collect_kinds("function main() asm { RET }")
        self.assertIn(TokenKind.ASM, actual)

    def test_invalid_character_is_reported_and_skipped(self):
        """Report and skip an invalid input character"""
        reporter = DiagnosticReporter("1 @ 2")
        lexer = Lexer("1 @ 2", reporter=reporter)

        actual = []
        while True:
            token = lexer.get_next_token()
            actual.append(token.kind)
            if token.kind == TokenKind.EOF:
                break

        self.assertEqual(actual, [TokenKind.NUMBER, TokenKind.NUMBER, TokenKind.EOF])
        self.assertTrue(reporter.has_errors())
        self.assertIn("invalid character: '@'", reporter.format())

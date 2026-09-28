import unittest

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

    def test_01_keywords_and_symbols(self):
        """EX2-1_01 Tokenize a sequence of keywords and symbols 'do repeat until % && || ! !='"""
        source = "do repeat until % && || ! !="

        actual = self.collect_kinds(source)

        expected = [
            TokenKind.DO,
            TokenKind.REPEAT,
            TokenKind.UNTIL,
            TokenKind.PERCENT,
            TokenKind.LAND,
            TokenKind.LOR,
            TokenKind.LNOT,
            TokenKind.NE,
            TokenKind.EOF,
        ]

        self.assertEqual(
            actual, expected, 'Cannot recognize "% do repeat until && || ! !=".'
        )

    def test_02_symbol_mod(self):
        """EX2-1_02 Tokenize the modulo operator %"""
        source = "%"

        actual = self.collect_kinds(source)

        expected = [
            TokenKind.PERCENT,
            TokenKind.EOF,
        ]

        self.assertEqual(actual, expected, msg='Cannot recognize "%".')

    def test_03_keyword_do(self):
        """EX2-1_03 Tokenize the do keyword"""
        source = "do"

        actual = self.collect_kinds(source)

        expected = [
            TokenKind.DO,
            TokenKind.EOF,
        ]

        self.assertEqual(actual, expected, msg='Cannot recognize "do".')

    def test_04_keyword_repeat(self):
        """EX2-1_04 Tokenize the repeat keyword"""
        source = "repeat"

        actual = self.collect_kinds(source)

        expected = [
            TokenKind.REPEAT,
            TokenKind.EOF,
        ]

        self.assertEqual(actual, expected, msg='Cannot recognize "repeat".')

    def test_05_keyword_until(self):
        """EX2-1_05 Tokenize the until keyword"""
        source = "until"

        actual = self.collect_kinds(source)

        expected = [
            TokenKind.UNTIL,
            TokenKind.EOF,
        ]

        self.assertEqual(actual, expected, msg='Cannot recognize "until".')

    def test_06_symbol_land(self):
        """EX2-1_06 Tokenize the logical AND operator &&"""
        source = "&&"

        actual = self.collect_kinds(source)

        expected = [
            TokenKind.LAND,
            TokenKind.EOF,
        ]

        self.assertEqual(actual, expected, msg='Cannot recognize "&&".')

    def test_07_symbol_lor(self):
        """EX2-1_07 Tokenize the logical OR operator ||"""
        source = "||"

        actual = self.collect_kinds(source)

        expected = [
            TokenKind.LOR,
            TokenKind.EOF,
        ]

        self.assertEqual(actual, expected, msg='Cannot recognize "||".')

    def test_08_symbol_lnot(self):
        """EX2-1_08 Tokenize the logical NOT operator !"""
        source = "!"

        actual = self.collect_kinds(source)

        expected = [
            TokenKind.LNOT,
            TokenKind.EOF,
        ]

        self.assertEqual(actual, expected, msg='Cannot recognize "!".')

    def test_09_symbol_ne(self):
        """EX2-1_09 Tokenize the not-equal operator !="""
        source = "!="

        actual = self.collect_kinds(source)

        expected = [
            TokenKind.NE,
            TokenKind.EOF,
        ]

        self.assertEqual(actual, expected, msg='Cannot recognize "!=".')

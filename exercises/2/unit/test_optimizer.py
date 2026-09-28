import unittest

from protolang.ast import BinaryOp
from protolang.ast import Identifier
from protolang.ast import LogicalAnd
from protolang.ast import LogicalOr
from protolang.ast import Number
from protolang.ast import UnaryOp
from protolang.optimizer import Optimizer
from protolang.token import SourceLocation
from protolang.token import SourceSpan
from protolang.token import TokenKind


SPAN = SourceSpan(
    start=SourceLocation(line=1, column=1),
    end=SourceLocation(line=1, column=2),
)


def number(value: int) -> Number:
    return Number(span=SPAN, value=value)


def identifier(name: str = "x") -> Identifier:
    return Identifier(span=SPAN, name=name)


def binary(op: TokenKind, left, right) -> BinaryOp:
    return BinaryOp(span=SPAN, op=op, left=left, right=right)


def unary(op: TokenKind, expr) -> UnaryOp:
    return UnaryOp(span=SPAN, op=op, expr=expr)


def optimize(expr):
    return Optimizer(level=1).optimize(expr)


class OptimizerTests(unittest.TestCase):
    def test_01_constant_folding_arithmetic(self):
        """EX2-4_01 Fold constant arithmetic expressions"""
        expr = binary(
            TokenKind.MINUS,
            binary(TokenKind.PLUS, number(2), number(3)),
            binary(TokenKind.STAR, number(4), number(2)),
        )

        self.assertEqual(optimize(expr), number(-3))

    def test_02_constant_folding_division_and_modulo(self):
        """EX2-4_02 Fold constant division and modulo expressions"""
        division = binary(TokenKind.SLASH, number(17), number(5))
        modulo = binary(TokenKind.PERCENT, number(17), number(5))

        self.assertEqual(optimize(division), number(3))
        self.assertEqual(optimize(modulo), number(2))

    def test_03_constant_folding_unary_operators(self):
        """EX2-4_03 Fold constant unary minus and logical NOT expressions"""
        self.assertEqual(optimize(unary(TokenKind.MINUS, number(4))), number(-4))
        self.assertEqual(optimize(unary(TokenKind.LNOT, number(0))), number(1))
        self.assertEqual(optimize(unary(TokenKind.LNOT, number(7))), number(0))

    def test_04_simplify_addition(self):
        """EX2-4_04 Simplify addition by zero"""
        x = identifier()

        self.assertEqual(optimize(binary(TokenKind.PLUS, number(0), x)), x)
        self.assertEqual(optimize(binary(TokenKind.PLUS, x, number(0))), x)

    def test_05_simplify_subtraction(self):
        """EX2-4_05 Simplify subtraction by zero"""
        x = identifier()

        self.assertEqual(optimize(binary(TokenKind.MINUS, x, number(0))), x)
        self.assertEqual(
            optimize(binary(TokenKind.MINUS, number(0), x)),
            unary(TokenKind.MINUS, x),
        )

    def test_06_simplify_multiplication_and_division(self):
        """EX2-4_06 Simplify multiplication and division by one"""
        x = identifier()

        self.assertEqual(optimize(binary(TokenKind.STAR, number(1), x)), x)
        self.assertEqual(optimize(binary(TokenKind.STAR, x, number(1))), x)
        self.assertEqual(optimize(binary(TokenKind.SLASH, x, number(1))), x)

    def test_07_simplify_logical_or(self):
        """EX2-4_07 Remove zero operands from logical OR expressions"""
        x = identifier()

        self.assertEqual(
            optimize(LogicalOr(span=SPAN, operands=[number(0), x, number(0)])),
            LogicalOr(span=SPAN, operands=[x]),
        )
        self.assertEqual(
            optimize(LogicalOr(span=SPAN, operands=[number(0), number(0)])),
            number(0),
        )

    def test_08_simplify_logical_and(self):
        """EX2-4_08 Remove nonzero constant operands from logical AND expressions"""
        x = identifier()

        self.assertEqual(
            optimize(LogicalAnd(span=SPAN, operands=[number(7), x, number(-3)])),
            LogicalAnd(span=SPAN, operands=[x]),
        )
        self.assertEqual(
            optimize(LogicalAnd(span=SPAN, operands=[number(1), number(1)])),
            number(1),
        )

    def test_09_short_circuit_simplification(self):
        """EX2-4_09 Remove unreachable operands using short-circuit evaluation"""
        x = identifier("x")
        y = identifier("y")

        self.assertEqual(
            optimize(LogicalOr(span=SPAN, operands=[x, number(7), y])),
            LogicalOr(span=SPAN, operands=[x, number(7)]),
        )
        self.assertEqual(
            optimize(LogicalAnd(span=SPAN, operands=[x, number(0), y])),
            LogicalAnd(span=SPAN, operands=[x, number(0)]),
        )

    def test_10_apply_optimizations_until_fixed_point(self):
        """EX2-4_10 Apply constant folding and algebraic simplification repeatedly"""
        expr = binary(
            TokenKind.MINUS,
            number(0),
            binary(TokenKind.PLUS, number(1), number(2)),
        )

        self.assertEqual(optimize(expr), number(-3))


if __name__ == "__main__":
    unittest.main()

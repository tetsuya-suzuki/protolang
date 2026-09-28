import unittest

from protolang.ast import BinaryOp
from protolang.ast import Identifier
from protolang.ast import LogicalAnd
from protolang.ast import LogicalOr
from protolang.ast import Number
from protolang.ast import UnaryOp
from protolang.optimizer import AlgebraicSimplifier
from protolang.optimizer import ConstantFolder
from protolang.optimizer import Optimizer
from protolang.main import compile_source
from protolang.token import SourceLocation
from protolang.token import SourceSpan
from protolang.token import TokenKind


SPAN = SourceSpan(SourceLocation(1, 1), SourceLocation(1, 2))


def number(value):
    return Number(span=SPAN, value=value)


def ident(name="x"):
    return Identifier(span=SPAN, name=name)


def binary(op, left, right):
    return BinaryOp(span=SPAN, op=op, left=left, right=right)


class ConstantFolderTests(unittest.TestCase):
    def test_folds_nested_arithmetic_bottom_up(self):
        """Fold nested constant arithmetic expressions bottom-up"""
        expr = binary(
            TokenKind.PLUS,
            number(1),
            binary(TokenKind.STAR, number(2), number(3)),
        )

        result = ConstantFolder().transform(expr)

        self.assertEqual(result, number(7))

    def test_folds_unary_minus_and_logical_not(self):
        """Fold constant unary minus and logical NOT expressions"""
        minus = UnaryOp(span=SPAN, op=TokenKind.MINUS, expr=number(4))
        logical_not = UnaryOp(span=SPAN, op=TokenKind.LNOT, expr=number(0))

        self.assertEqual(ConstantFolder().transform(minus), number(-4))
        self.assertEqual(ConstantFolder().transform(logical_not), number(1))

    def test_does_not_fold_division_or_modulo_by_zero(self):
        """Leave division and modulo by zero unfolded"""
        division = binary(TokenKind.SLASH, number(4), number(0))
        modulo = binary(TokenKind.PERCENT, number(4), number(0))

        self.assertIs(ConstantFolder().transform(division), division)
        self.assertIs(ConstantFolder().transform(modulo), modulo)


class AlgebraicSimplifierTests(unittest.TestCase):
    def test_simplifies_binary_identities(self):
        """Simplify arithmetic identity expressions"""
        x = ident()
        cases = [
            (binary(TokenKind.PLUS, number(0), x), x),
            (binary(TokenKind.PLUS, x, number(0)), x),
            (binary(TokenKind.MINUS, x, number(0)), x),
            (binary(TokenKind.STAR, number(1), x), x),
            (binary(TokenKind.STAR, x, number(1)), x),
            (binary(TokenKind.SLASH, x, number(1)), x),
        ]

        for expression, expected in cases:
            with self.subTest(expression=expression):
                self.assertEqual(AlgebraicSimplifier().transform(expression), expected)

    def test_rewrites_zero_minus_expression_to_unary_minus(self):
        """Rewrite zero minus an expression as unary minus"""
        x = ident()
        expression = binary(TokenKind.MINUS, number(0), x)

        result = AlgebraicSimplifier().transform(expression)

        self.assertEqual(
            result,
            UnaryOp(span=SPAN, op=TokenKind.MINUS, expr=x),
        )

    def test_simplifies_logical_or(self):
        """Remove redundant constant operands from logical OR"""
        x = ident("x")
        y = ident("y")
        expression = LogicalOr(span=SPAN, operands=[number(0), x, number(1), y])

        result = AlgebraicSimplifier().transform(expression)

        self.assertEqual(result, LogicalOr(span=SPAN, operands=[x, number(1)]))

    def test_simplifies_logical_and(self):
        """Remove redundant constant operands from logical AND"""
        x = ident("x")
        y = ident("y")
        expression = LogicalAnd(span=SPAN, operands=[number(1), x, number(0), y])

        result = AlgebraicSimplifier().transform(expression)

        self.assertEqual(result, LogicalAnd(span=SPAN, operands=[x, number(0)]))


class OptimizerTests(unittest.TestCase):
    def test_runs_to_fixed_point(self):
        """Apply optimization passes repeatedly to a fixed point"""
        expression = binary(
            TokenKind.MINUS,
            number(0),
            binary(TokenKind.PLUS, number(1), number(2)),
        )

        result = Optimizer(level=1).optimize(expression)

        self.assertEqual(result, number(-3))

    def test_level_zero_does_not_optimize(self):
        """Leave the AST unchanged at optimization level 0"""
        expression = binary(TokenKind.PLUS, number(1), number(2))

        result = Optimizer(level=0).optimize(expression)

        self.assertIs(result, expression)

    def test_level_two_includes_level_one_optimizations(self):
        """Apply level 1 optimizations at optimization level 2"""
        expression = binary(TokenKind.PLUS, number(1), number(2))

        result = Optimizer(level=2).optimize(expression)

        self.assertEqual(result, number(3))

    def test_rejects_unknown_optimization_level(self):
        """Reject an unsupported optimization level"""
        with self.assertRaises(ValueError):
            Optimizer(level=3)

    def test_compile_source_uses_selected_optimization_level(self):
        """Compile source using the selected optimization level"""
        source = "function main() { return 0 - (1 + 2); }"

        unoptimized = compile_source(source, optimization_level=0)
        optimized = compile_source(source, optimization_level=1)

        unoptimized_return = unoptimized.ast.items[0].body.items[0]
        optimized_return = optimized.ast.items[0].body.items[0]
        self.assertIsInstance(unoptimized_return.expr, BinaryOp)
        self.assertEqual(optimized_return.expr.value, -3)
        self.assertFalse(optimized.reporter.has_errors())


if __name__ == "__main__":
    unittest.main()


class TailRecursionIntegrationTests(unittest.TestCase):
    def test_level_two_rewrites_and_executes_tail_recursion(self):
        """Rewrite and execute a tail-recursive call at optimization level 2"""
        from protolang.ast import TailRecursiveCallStatement
        from protolang.main import run_source

        source = """
        function factorial(n, acc) {
            if (n <= 1) {
                return acc;
            }
            return factorial(n - 1, acc * n);
        }
        function main() { return factorial(5, 1); }
        """

        result = compile_source(source, optimization_level=2)
        tail_stmt = result.ast.items[0].body.items[1]
        self.assertIsInstance(tail_stmt, TailRecursiveCallStatement)
        self.assertFalse(result.reporter.has_errors())

        vm = run_source(source, optimization_level=2)
        self.assertEqual(vm.stack[vm.sp - 1], 120)

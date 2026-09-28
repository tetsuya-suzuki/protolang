import unittest

from protolang.ast import (
    BinaryOp,
    DoWhileStatement,
    ExpressionStatement,
    ReturnStatement,
    FunctionDefinition,
    IfStatement,
    LogicalAnd,
    LogicalOr,
    RepeatUntilStatement,
    UnaryOp,
)
from protolang.diagnostics import DiagnosticReporter
from protolang.lexer import Lexer
from protolang.normalizer import ASTNormalizer
from protolang.parser import Parser
from protolang.semantic import INT_TYPE, SemanticAnalyzer


class SemanticTests(unittest.TestCase):
    def analyze(self, source: str):
        reporter = DiagnosticReporter(source, filename="test_code")
        lexer = Lexer(source, reporter=reporter)
        parser = Parser(lexer, reporter=reporter)
        ast = parser.parse_program()
        ast = ASTNormalizer().transform(ast)
        SemanticAnalyzer(reporter).analyze(ast)
        return ast, reporter

    def main_body(self, ast):
        function = ast.items[0]
        self.assertIsInstance(function, FunctionDefinition)
        return function.body

    def assert_no_errors(self, reporter):
        self.assertFalse(reporter.has_errors(), msg=reporter.format())

    def test_01_mod_operator_type(self):
        """EX2-3_01 Analyze the type of the modulo operator"""
        ast, reporter = self.analyze("function main() { 10 % 3; }")
        self.assert_no_errors(reporter)
        stmt = self.main_body(ast).items[0]
        self.assertIsInstance(stmt, ReturnStatement)
        self.assertIsInstance(stmt.expr, BinaryOp)
        self.assertEqual(stmt.expr.type, INT_TYPE)

    def test_02_do_while_condition(self):
        """EX2-3_02 Analyze a do-while statement"""
        ast, reporter = self.analyze(
            "function main() { var x=0; do { x=x+1; } while (x); }"
        )
        self.assert_no_errors(reporter)
        stmt = self.main_body(ast).items[1]
        self.assertIsInstance(stmt, DoWhileStatement)
        self.assertEqual(stmt.condition.type, INT_TYPE)

    def test_03_do_while_body(self):
        """EX2-3_03 Analyze the body of a do-while statement"""
        _, reporter = self.analyze("function main() { do { x; } while (1); }")
        self.assertTrue(reporter.has_errors())
        self.assertIn("undefined variable: x", reporter.format())

    def test_04_repeat_until_condition(self):
        """EX2-3_04 Analyze a repeat-until statement"""
        ast, reporter = self.analyze(
            "function main() { var x=0; repeat { x=x+1; } until (x); }"
        )
        self.assert_no_errors(reporter)
        stmt = self.main_body(ast).items[1]
        self.assertIsInstance(stmt, RepeatUntilStatement)
        self.assertEqual(stmt.condition.type, INT_TYPE)

    def test_05_repeat_until_body(self):
        """EX2-3_05 Analyze the body of a repeat-until statement"""
        _, reporter = self.analyze("function main() { repeat { x; } until (1); }")
        self.assertTrue(reporter.has_errors())
        self.assertIn("undefined variable: x", reporter.format())

    def test_06_if_without_else(self):
        """EX2-3_06 Analyze an if statement without else part"""
        ast, reporter = self.analyze("function main() { if (1) { 1; } }")
        self.assert_no_errors(reporter)
        stmt = self.main_body(ast).items[0]
        self.assertIsInstance(stmt, IfStatement)
        self.assertEqual(stmt.condition.type, INT_TYPE)
        self.assertIsNone(stmt.else_stmt)

    def test_07_if_then_and_else(self):
        """EX2-3_07 Analyze both branches of an if statement"""
        _, reporter = self.analyze("function main() { if (1) { x; } else { y; } }")
        text = reporter.format()
        self.assertIn("undefined variable: x", text)
        self.assertIn("undefined variable: y", text)

    def test_08_lnot_operator_type(self):
        """EX2-3_08 Analyze the type of logical NOT"""
        ast, reporter = self.analyze("function main() { !0; }")
        self.assert_no_errors(reporter)
        stmt = self.main_body(ast).items[0]
        self.assertIsInstance(stmt.expr, UnaryOp)
        self.assertEqual(stmt.expr.type, INT_TYPE)

    def test_09_land_operator_type(self):
        """EX2-3_09 Analyze the type of logical AND"""
        ast, reporter = self.analyze("function main() { 1 && 2 && 3; }")
        self.assert_no_errors(reporter)
        stmt = self.main_body(ast).items[0]
        self.assertIsInstance(stmt.expr, LogicalAnd)
        self.assertEqual(stmt.expr.type, INT_TYPE)
        self.assertTrue(all(operand.type == INT_TYPE for operand in stmt.expr.operands))

    def test_10_land_operands(self):
        """EX2-3_10 Analyze all operands of logical AND"""
        _, reporter = self.analyze("function main() { 1 && x && y; }")
        text = reporter.format()
        self.assertIn("undefined variable: x", text)
        self.assertIn("undefined variable: y", text)

    def test_11_lor_operator_type(self):
        """EX2-3_11 Analyze the type of logical OR"""
        ast, reporter = self.analyze("function main() { 1 || 2 || 3; }")
        self.assert_no_errors(reporter)
        stmt = self.main_body(ast).items[0]
        self.assertIsInstance(stmt.expr, LogicalOr)
        self.assertEqual(stmt.expr.type, INT_TYPE)
        self.assertTrue(all(operand.type == INT_TYPE for operand in stmt.expr.operands))

    def test_12_lor_operands(self):
        """EX2-3_12 Analyze all operands of logical OR"""
        _, reporter = self.analyze("function main() { 1 || x || y; }")
        text = reporter.format()
        self.assertIn("undefined variable: x", text)
        self.assertIn("undefined variable: y", text)

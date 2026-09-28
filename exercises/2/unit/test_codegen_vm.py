import unittest

from protolang.lexer import Lexer
from protolang.token import TokenKind
from protolang.parser import Parser
from protolang.normalizer import ASTNormalizer
from protolang.ast import FunctionDefinition
from protolang.ast import Block
from protolang.diagnostics import DiagnosticReporter
from protolang.ast import UnaryOp
from protolang.ast import BinaryOp
from protolang.ast import ExpressionStatement
from protolang.ast import Number
from protolang.ast import Program
from protolang.token import SourceLocation
from protolang.token import SourceSpan
from protolang.token import TokenKind
from protolang.ast import DoWhileStatement
from protolang.ast import RepeatUntilStatement
from protolang.ast import IfStatement
from protolang.ast import LogicalAnd
from protolang.ast import LogicalOr
from protolang.ast import Assignment
from dataclasses import is_dataclass, fields
from protolang.semantic import SemanticAnalyzer
from protolang.vm import VirtualMachine
from protolang.codegen import CodeGenerator
from dataclasses import dataclass


@dataclass
class CompilationResult:
    ast: object | None
    code: object | None
    global_count: int | None
    program_info: object | None
    reporter: DiagnosticReporter


class CodeGenVMTests(unittest.TestCase):
    def run_program(self, source: str):
        reporter = DiagnosticReporter(source, filename="test_code")

        lexer = Lexer(source, reporter=reporter)
        parser = Parser(lexer, reporter=reporter)
        ast = parser.parse_program()
        normalizer = ASTNormalizer()
        ast = normalizer.transform(ast)
        analyzer = SemanticAnalyzer(reporter)
        program_info = analyzer.analyze(ast)
        generator = CodeGenerator(program_info, reporter=reporter)
        code, global_count = generator.generate(ast)
        result = CompilationResult(ast, code, global_count, program_info, reporter)
        vm = VirtualMachine(result.code, global_count=result.global_count)
        vm.run()
        return vm

    def test_13_mod_operator(self):
        """EX2-3_13 Evaluate an expression with the modulo operator"""
        source = "function main() { 10 % 3; }"
        vm = self.run_program(source)
        actual = vm.stack[vm.sp - 1]
        expected = 1
        self.assertEqual(actual, expected, msg="Cannot evaluate '10 % 3' correctly.")

    def test_14_do_while_statement(self):
        """EX2-3_14 Evaluate a do-while statement"""
        source = (
            "function main() { var sum=0; do { sum = sum + 1; } while (sum < 10); }"
        )
        vm = self.run_program(source)
        actual = vm.stack[vm.sp - 1]
        expected = 10
        self.assertEqual(
            actual, expected, msg="Cannot evaluate do-while statement correctly."
        )

    def test_15_repeat_until_statement(self):
        """EX2-3_15 Evaluate a repeat-until statement"""
        source = "function main() { var sum=0; repeat { sum = sum + 1; } until (sum == 10); }"
        vm = self.run_program(source)
        actual = vm.stack[vm.sp - 1]
        expected = 10
        self.assertEqual(
            actual, expected, msg="Cannot evaluate repeat-until statement correctly."
        )

    def test_16_if_statement_without_else_part(self):
        """EX2-3_16 Evaluate an if statement without else part"""
        source = "function main() { if (0) { 1; } }"
        vm = self.run_program(source)
        actual = vm.stack[vm.sp - 1]
        expected = 0
        self.assertEqual(
            actual,
            expected,
            msg="Cannot evaluate if-statement without else part correctly.",
        )

    def test_17_lnot_operator(self):
        """EX2-3_17 Evaluate an expression with logical NOT"""
        source = "function main() { !0; }"
        vm = self.run_program(source)
        actual = vm.stack[vm.sp - 1]
        expected = 1
        self.assertEqual(actual, expected, msg="Cannot evaluate logical NOT correctly.")

    def test_18_land_operator_0(self):
        """EX2-3_18 Evaluate an expression with logical AND '0 && 1'"""
        source = "function main() { 0 && 1; }"
        vm = self.run_program(source)
        actual = vm.stack[vm.sp - 1]
        expected = 0
        self.assertEqual(actual, expected, msg="Cannot evaluate logical AND correctly.")

    def test_19_land_operator_1(self):
        """EX2-3_19 Evaluate an expression with logical AND '1 && 1'"""
        source = "function main() { 1 && 1; }"
        vm = self.run_program(source)
        actual = vm.stack[vm.sp - 1]
        expected = 1
        self.assertEqual(actual, expected, msg="Cannot evaluate logical AND correctly.")

    def test_20_lor_operator_0(self):
        """EX2-3_20 Evaluate an expression with logical OR '0 || 0'"""
        source = "function main() { 0 || 0; }"
        vm = self.run_program(source)
        actual = vm.stack[vm.sp - 1]
        expected = 0
        self.assertEqual(actual, expected, msg="Cannot evaluate logical OR correctly.")

    def test_21_lor_operator_1(self):
        """EX2-3_21 Evaluate an expression with logical OR '0 || 1'"""
        source = "function main() { 0 || 1; }"
        vm = self.run_program(source)
        actual = vm.stack[vm.sp - 1]
        expected = 1
        self.assertEqual(actual, expected, msg="Cannot evaluate logical OR correctly.")

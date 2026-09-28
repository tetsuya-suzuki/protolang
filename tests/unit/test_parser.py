import unittest

from protolang.asm_parser import AsmBlock
from protolang.ast import BinaryOp
from protolang.ast import FunctionDefinition
from protolang.ast import Program
from protolang.diagnostics import DiagnosticReporter
from protolang.lexer import Lexer
from protolang.main import compile_source
from protolang.parser import Parser
from protolang.token import TokenKind


def parse(source: str, reporter: DiagnosticReporter | None = None):
    lexer = Lexer(source, reporter=reporter)
    parser = Parser(lexer, reporter=reporter)
    return parser.parse_program()


class ParserTests(unittest.TestCase):
    def test_function_definition(self):
        """Parse a function definition"""
        ast = parse("function main() { return 1; }")

        self.assertIsInstance(ast, Program)
        self.assertIsInstance(ast.items[0], FunctionDefinition)

    def test_precedence(self):
        """Parse binary operators with the correct precedence"""
        ast = parse("function main() { return 1 + 2 * 3; }")

        return_stmt = ast.items[0].body.items[0]
        expr = return_stmt.expr

        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, TokenKind.PLUS)
        self.assertEqual(expr.right.op, TokenKind.STAR)

    def test_function_definition_with_asm_body(self):
        """Parse a function definition with an assembly body"""
        ast = parse(
            """
            function main() asm {
                .function helper
                CALL helper
                RET
            }
            """
        )

        func = ast.items[0]
        self.assertIsInstance(func.body, AsmBlock)
        self.assertEqual(func.body.lines[0].item.name, ".function")
        self.assertEqual(func.body.lines[1].item.mnemonic, "CALL")
        self.assertEqual(func.body.lines[1].item.operand, "helper")

    def test_parser_reports_missing_semicolon_without_raising(self):
        """Report a missing semicolon without raising an exception"""
        source = "function main() { return 1 }"
        reporter = DiagnosticReporter(source)

        ast = parse(source, reporter=reporter)

        self.assertIsInstance(ast, Program)
        self.assertTrue(reporter.has_errors())
        self.assertIn("expected SEMICOLON, got RBRACE", reporter.format())

    def test_parser_reports_asm_block_errors_without_raising(self):
        """Report assembly-block syntax errors without raising an exception"""
        source = """
function main() asm {
    bad-label!: IPUSH 1
    push 2
    .bogus foo
}
"""
        reporter = DiagnosticReporter(source)

        ast = parse(source, reporter=reporter)

        self.assertIsInstance(ast, Program)
        self.assertTrue(reporter.has_errors())
        text = reporter.format()
        self.assertIn("invalid label: bad-label!", text)
        self.assertIn("mnemonic must be uppercase: push", text)
        self.assertIn("unknown directive: .bogus", text)

    def test_compile_source_collects_multiple_lexer_and_parser_errors(self):
        """Collect multiple lexer and parser errors in one compilation"""
        source = """
function main() {
    return @
}
"""
        result = compile_source(source)

        self.assertTrue(result.reporter.has_errors())
        text = result.reporter.format()
        self.assertIn("invalid character: '@'", text)
        self.assertIn("unexpected token in primary: RBRACE", text)

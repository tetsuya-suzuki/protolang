import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from protolang.main import main


class DumpOptionTests(unittest.TestCase):
    def run_main_with_source(self, source, arguments):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.ptl"
            path.write_text(source, encoding="utf-8")
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = main([*arguments, str(path)])
            return exit_code, stdout.getvalue(), stderr.getvalue()

    def test_dump_tokens_prints_token_sequence(self):
        """Print the token sequence with --dump-tokens"""
        exit_code, output, errors = self.run_main_with_source(
            "function main() { return 42; }",
            ["--dump-tokens"],
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(errors, "")
        self.assertEqual(
            output.splitlines(),
            [
                "FUNCTION",
                "IDENT(main)",
                "LPAREN",
                "RPAREN",
                "LBRACE",
                "RETURN",
                "NUMBER(42)",
                "SEMICOLON",
                "RBRACE",
                "EOF",
            ],
        )

    def test_dump_tokens_does_not_parse_or_run_program(self):
        """Stop after lexical analysis with --dump-tokens"""
        exit_code, output, errors = self.run_main_with_source(
            "function main( { return 1 / 0; }",
            ["--dump-tokens"],
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(errors, "")
        self.assertIn("NUMBER(0)", output)
        self.assertNotIn("result =", output)

    def test_dump_tokens_reports_lexical_errors(self):
        """Report lexical errors while dumping tokens"""
        exit_code, output, errors = self.run_main_with_source(
            "function main() { return @; }",
            ["--dump-tokens"],
        )

        self.assertEqual(exit_code, 1)
        self.assertIn("EOF", output)
        self.assertIn("invalid character: '@'", errors)

    def test_dump_ast_prints_ast_immediately_after_parsing(self):
        """Print the AST before normalization with --dump-ast"""
        exit_code, output, errors = self.run_main_with_source(
            "function main() { 1 + 2; }",
            ["--dump-ast"],
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(errors, "")
        self.assertIn("graph TD", output)
        self.assertIn("ExpressionStatement", output)
        self.assertNotIn("ReturnStatement", output)

    def test_dump_transformed_ast_prints_normalized_ast_at_o0(self):
        """Print the normalized AST at -O0 with --dump-transformed-ast"""
        exit_code, output, errors = self.run_main_with_source(
            "function main() { 1 + 2; }",
            ["-O0", "--dump-transformed-ast"],
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(errors, "")
        self.assertIn("graph TD", output)
        self.assertIn("ReturnStatement", output)
        self.assertNotIn("ExpressionStatement", output)

    def test_dump_transformed_ast_prints_optimized_ast_at_o1(self):
        """Print the optimized AST at -O1 with --dump-transformed-ast"""
        exit_code, output, errors = self.run_main_with_source(
            "function main() { return 0 - (1 + 2); }",
            ["-O1", "--dump-transformed-ast"],
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(errors, "")
        self.assertIn("graph TD", output)
        self.assertIn("value=-3", output)
        self.assertNotIn("BinaryOp", output)


if __name__ == "__main__":
    unittest.main()

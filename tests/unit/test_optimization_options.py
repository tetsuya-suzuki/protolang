import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from unittest.mock import patch

from protolang.main import build_argument_parser
from protolang.main import build_ast
from protolang.main import main
from protolang.semantic import SemanticAnalyzer


SOURCE = "function main() { return 0 - (1 + 2); }"


class OptimizationOptionTests(unittest.TestCase):
    def test_parser_accepts_compact_optimization_options(self):
        """Accept compact -O0, -O1, and -O2 optimization options"""
        parser = build_argument_parser()

        self.assertEqual(parser.parse_args(["-O0", "sample.ptl"]).optimization_level, 0)
        self.assertEqual(parser.parse_args(["-O1", "sample.ptl"]).optimization_level, 1)
        self.assertEqual(parser.parse_args(["-O2", "sample.ptl"]).optimization_level, 2)

    def run_main_with_source(self, arguments):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.ptl"
            path.write_text(SOURCE, encoding="utf-8")
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = main([*arguments, str(path)])
            return exit_code, stdout.getvalue(), stderr.getvalue()

    def test_o1_runs_semantic_analysis_once(self):
        """Run semantic analysis once at optimization level 1"""
        with patch(
            "protolang.main.SemanticAnalyzer", wraps=SemanticAnalyzer
        ) as analyzer:
            _, _, reporter = build_ast(SOURCE, optimization_level=1)

        self.assertFalse(reporter.has_errors())
        self.assertEqual(analyzer.call_count, 1)

    def test_o2_runs_semantic_analysis_twice(self):
        """Run semantic analysis again after level 2 transformation"""
        with patch(
            "protolang.main.SemanticAnalyzer", wraps=SemanticAnalyzer
        ) as analyzer:
            ast, program_info, reporter = build_ast(SOURCE, optimization_level=2)

        self.assertFalse(reporter.has_errors())
        self.assertEqual(analyzer.call_count, 2)
        self.assertIs(ast.items[0].function_info, program_info.functions_map["main"])

    def test_run_asm_rejects_optimization_option(self):
        """Reject optimization options together with --run-asm"""
        exit_code, _, errors = self.run_main_with_source(["--run-asm", "-O1"])

        self.assertEqual(exit_code, 2)
        self.assertIn("optimization options cannot be used", errors)


if __name__ == "__main__":
    unittest.main()

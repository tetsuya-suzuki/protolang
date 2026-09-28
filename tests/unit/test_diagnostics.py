import io
import unittest

from protolang.diagnostics import DiagnosticLevel
from protolang.diagnostics import DiagnosticReporter
from protolang.main import compile_source
from protolang.main import run_source
from protolang.token import SourceLocation
from protolang.token import SourceSpan


class DiagnosticTests(unittest.TestCase):
    def test_diagnostics_are_sorted_by_line_and_column(self):
        """Sort diagnostics by source line and column"""
        source = "a\nb\nc\n"
        reporter = DiagnosticReporter(source)
        reporter.warning("later warning", 3, 1)
        reporter.error("first error", 1, 2)
        reporter.error("second error", 1, 5)

        diagnostics = reporter.sorted_diagnostics()

        self.assertEqual(diagnostics[0].message, "first error")
        self.assertEqual(diagnostics[1].message, "second error")
        self.assertEqual(diagnostics[2].message, "later warning")
        self.assertEqual(diagnostics[2].level, DiagnosticLevel.WARNING)

    def test_compile_source_collects_semantic_error_with_location(self):
        """Collect semantic errors with source locations during compilation"""
        source = """
function main() {
    return missing + 1;
}
"""
        result = compile_source(source)

        self.assertTrue(result.reporter.has_errors())
        diagnostic = result.reporter.sorted_diagnostics()[0]
        self.assertEqual(diagnostic.line, 3)
        self.assertEqual(diagnostic.column, 12)
        self.assertIn("undefined variable: missing", diagnostic.message)

    def test_run_source_returns_none_when_there_is_an_error(self):
        """Return no VM result when source execution has an error"""
        source = """
function main() {
    return missing + 1;
}
"""
        vm = run_source(source)
        self.assertIsNone(vm)

    def test_reporter_print_includes_file_name_and_underlines_span(self):
        """Print the file name and underline the diagnostic source span"""
        source = "x = y + 1;\n"
        reporter = DiagnosticReporter(source, filename="sample.ptl")
        reporter.error_at_span(
            "undefined variable: y",
            SourceSpan(SourceLocation(1, 5), SourceLocation(1, 6)),
        )

        buffer = io.StringIO()
        reporter.print(buffer)
        text = buffer.getvalue()

        self.assertIn("sample.ptl:1:5: error: undefined variable: y", text)
        self.assertIn("x = y + 1;", text)
        self.assertIn("^", text)

    def test_reporter_print_uses_multiple_carets_for_wider_span(self):
        """Use multiple carets to underline a multi-column source span"""
        source = "return missing + 1;\n"
        reporter = DiagnosticReporter(source, filename="sample.ptl")
        reporter.error_at_span(
            "undefined variable: missing",
            SourceSpan(SourceLocation(1, 8), SourceLocation(1, 15)),
        )

        buffer = io.StringIO()
        reporter.print(buffer)
        text = buffer.getvalue()

        self.assertIn("sample.ptl:1:8: error: undefined variable: missing", text)
        self.assertIn("^^^^^^^", text)

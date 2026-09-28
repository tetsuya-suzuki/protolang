import io
import re
import unittest
from contextlib import redirect_stdout

from protolang.assembly_formatter import AssemblyFormatter
from protolang.main import compile_source
from protolang.main import main


class AssemblyListingTests(unittest.TestCase):
    def test_listing_starts_with_globals_directive(self):
        """Start an assembly listing with the .globals directive"""
        source = """
        var g = 0;

        function main() {
            return g;
        }
        """

        result = compile_source(source, filename="sample.ptl")
        formatter = AssemblyFormatter(result.program_info, result.global_count)
        listing = formatter.format_program(result.code)

        self.assertTrue(listing.startswith(".globals 1\n"))

    def test_function_entries_use_numeric_labels_and_function_comments(self):
        """Use numeric labels and function comments for function entries"""
        source = """
        function helper() {
            return 7;
        }

        function main() {
            return helper();
        }
        """

        result = compile_source(source, filename="sample.ptl")
        formatter = AssemblyFormatter(result.program_info, result.global_count)
        listing = formatter.format_program(result.code)

        self.assertRegex(listing, r"L\d+: ALLOC 0 ; main")
        self.assertRegex(listing, r"L\d+: ALLOC 0 ; helper")
        self.assertNotIn("_main", listing)
        self.assertNotIn("_helper", listing)

    def test_call_uses_numeric_label_and_function_comment(self):
        """Show numeric call targets with function comments"""
        source = """
        function helper() {
            return 7;
        }

        function main() {
            return helper();
        }
        """

        result = compile_source(source, filename="sample.ptl")
        formatter = AssemblyFormatter(result.program_info, result.global_count)
        listing = formatter.format_program(result.code)

        self.assertRegex(listing, r"CALL L\d+ ; main")
        self.assertRegex(listing, r"CALL L\d+ ; helper")

    def test_every_instruction_gets_a_label(self):
        """Assign a numeric label to every listed instruction"""
        source = """
        function main() {
            return 42;
        }
        """

        result = compile_source(source, filename="sample.ptl")
        formatter = AssemblyFormatter(result.program_info, result.global_count)
        listing = formatter.format_program(result.code)
        instruction_lines = [line for line in listing.splitlines()[1:] if line.strip()]

        self.assertTrue(instruction_lines)
        self.assertTrue(all(re.match(r"L\d+: ", line) for line in instruction_lines))

    def test_main_dump_asm_option_prints_listing_without_result(self):
        """Print an assembly listing without executing it with --dump-asm"""
        source = """
        function main() {
            return 42;
        }
        """

        from pathlib import Path
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sample.ptl"
            path.write_text(source, encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                exit_code = main(["--dump-asm", str(path)])

        output = buf.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn(".globals 0", output)
        self.assertRegex(output, r"L\d+: CALL L\d+ ; main")
        self.assertNotIn("result =", output)

    def test_main_dump_ast_takes_priority_over_dump_asm(self):
        """Give --dump-ast priority over --dump-asm"""
        source = """
        function main() {
            return 42;
        }
        """

        from pathlib import Path
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sample.ptl"
            path.write_text(source, encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                exit_code = main(["--dump-ast", "--dump-asm", str(path)])

        output = buf.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("Program", output)
        self.assertIn("graph TD", output)
        self.assertNotIn("CALL L", output)

    def test_main_trace_vm_prints_trace_and_final_result(self):
        """Print the VM trace and final result with --trace-vm"""
        source = """
        function main() {
            return 42;
        }
        """

        from pathlib import Path
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sample.ptl"
            path.write_text(source, encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                exit_code = main(["--trace-vm", str(path)])

        output = buf.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("NEXT : CALL ", output)
        self.assertIn("stack  :", output)
        self.assertIn("globals:", output)
        self.assertIn("HALT", output)
        self.assertIn("result = 42", output)

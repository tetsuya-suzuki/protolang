import io
import tempfile
import unittest
from contextlib import redirect_stdout
from contextlib import redirect_stderr
from pathlib import Path

from protolang.assembler import assemble_source
from protolang.asm_parser import parse_asm_source
from protolang.diagnostics import DiagnosticReporter
from protolang.errors import AssemblerError
from protolang.instruction import OpCode
from protolang.main import main


class AssemblerTests(unittest.TestCase):
    def test_assemble_with_globals_and_general_labels(self):
        """Assemble global declarations and general labels"""
        source = """
        .globals 2

        start: IPUSH 3
               IPUSH 4
               IADD
               HALT
        """

        result = assemble_source(source)

        self.assertEqual(result.global_count, 2)
        self.assertEqual(
            [inst.op for inst in result.code],
            [OpCode.IPUSH, OpCode.IPUSH, OpCode.IADD, OpCode.HALT],
        )
        self.assertEqual(result.code[0].arg, 3)
        self.assertEqual(result.code[1].arg, 4)

    def test_jump_label_resolution(self):
        """Resolve jump labels to instruction addresses"""
        source = """
        loop: IPUSH 0
              JPZ end
              JMP loop
        end:  HALT
        """

        result = assemble_source(source)

        self.assertEqual(result.code[1].arg, 3)
        self.assertEqual(result.code[2].arg, 0)

    def test_function_directive_records_unresolved_call(self):
        """Record unresolved calls declared by a function directive"""
        source = """
        .function foo
        CALL foo
        HALT
        """
        result = assemble_source(source)
        self.assertEqual(result.unresolved_calls, [(0, "foo")])

    def test_label_is_optional(self):
        """Assemble instructions without labels"""
        source = """
        IPUSH 1
        IPUSH 2
        IADD
        HALT
        """

        result = assemble_source(source)
        self.assertEqual(len(result.code), 4)

    def test_duplicate_label_is_error(self):
        """Reject duplicate assembly labels"""
        with self.assertRaises(AssemblerError):
            assemble_source("""
            loop: IPUSH 1
            loop: HALT
            """)

    def test_undefined_label_is_error(self):
        """Reject jumps to undefined assembly labels"""
        with self.assertRaises(AssemblerError):
            assemble_source("JMP nowhere")

    def test_parse_asm_source_reports_multiple_errors_with_reporter(self):
        """Report multiple assembly syntax errors in one parse"""
        source = """
        bad-label!: IPUSH 1
        push 2
        .bogus foo
        """
        reporter = DiagnosticReporter(source)

        block = parse_asm_source(source, reporter=reporter)

        self.assertEqual(len(block.lines), 3)
        self.assertTrue(reporter.has_errors())
        text = reporter.format()
        self.assertIn("invalid label: bad-label!", text)
        self.assertIn("mnemonic must be uppercase: push", text)
        self.assertIn("unknown directive: .bogus", text)

    def test_main_run_asm_executes_program(self):
        """Execute an assembly source file with --run-asm"""
        source = """
        .globals 0
        start: IPUSH 3
               IPUSH 4
               IADD
               HALT
        """

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sample.asm"
            path.write_text(source, encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["--run-asm", str(path)])

        self.assertEqual(exit_code, 0)
        self.assertIn("result = 7", stdout.getvalue())

    def test_main_run_asm_rejects_unresolved_function_calls(self):
        """Reject unresolved function calls when running assembly source"""
        source = ".function foo\nCALL foo\nHALT\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sample.asm"
            path.write_text(source, encoding="utf-8")

            stderr = io.StringIO()
            with redirect_stderr(stderr):
                exit_code = main(["--run-asm", str(path)])

        self.assertEqual(exit_code, 1)
        self.assertIn("unresolved function call: foo", stderr.getvalue())

    def test_main_run_asm_trace_vm_executes_program(self):
        """Trace VM execution when running assembly source"""
        source = """
        .globals 0
        IPUSH 3
        IPUSH 4
        IADD
        HALT
        """

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sample.asm"
            path.write_text(source, encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["--run-asm", "--trace-vm", str(path)])

        self.assertEqual(exit_code, 0)
        out = stdout.getvalue()
        self.assertIn("NEXT : IPUSH 3", out)
        self.assertIn("HALT", out)
        self.assertIn("result = 7", out)

    def test_main_rejects_dump_ast_with_run_asm(self):
        """Reject --dump-ast together with --run-asm"""
        source = "HALT\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sample.asm"
            path.write_text(source, encoding="utf-8")

            stderr = io.StringIO()
            with redirect_stderr(stderr):
                exit_code = main(["--run-asm", "--dump-ast", str(path)])

        self.assertEqual(exit_code, 2)
        self.assertIn("cannot be used", stderr.getvalue())

    def test_main_rejects_dump_tokens_with_run_asm(self):
        """Reject --dump-tokens together with --run-asm"""
        source = "HALT\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sample.asm"
            path.write_text(source, encoding="utf-8")

            stderr = io.StringIO()
            with redirect_stderr(stderr):
                exit_code = main(["--run-asm", "--dump-tokens", str(path)])

        self.assertEqual(exit_code, 2)
        self.assertIn("cannot be used", stderr.getvalue())

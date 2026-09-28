import unittest

from protolang.codegen import CodeGenerator
from protolang.diagnostics import DiagnosticReporter
from protolang.errors import CodeGenError
from protolang.errors import SemanticError
from protolang.instruction import OpCode
from protolang.lexer import Lexer
from protolang.main import run_source
from protolang.parser import Parser
from protolang.semantic import INT_TYPE
from protolang.semantic import SemanticAnalyzer


def analyze_program(source: str):
    lexer = Lexer(source)
    parser = Parser(lexer)
    ast = parser.parse_program()

    analyzer = SemanticAnalyzer()
    program_info = analyzer.analyze(ast)
    return ast, program_info


def analyze_program_with_reporter(source: str):
    reporter = DiagnosticReporter(source)
    lexer = Lexer(source, reporter=reporter)
    parser = Parser(lexer, reporter=reporter)
    ast = parser.parse_program()

    analyzer = SemanticAnalyzer(reporter)
    program_info = analyzer.analyze(ast)
    return ast, program_info, reporter


def compile_program(source: str):
    ast, program_info = analyze_program(source)
    generator = CodeGenerator(program_info)
    return generator.generate(ast)


def generate_program_with_reporter(source: str):
    ast, program_info, reporter = analyze_program_with_reporter(source)
    generator = CodeGenerator(program_info, reporter=reporter)
    code, global_count = generator.generate(ast)
    return code, global_count, reporter


def build_codegen(source: str) -> CodeGenerator:
    ast, program_info = analyze_program(source)
    generator = CodeGenerator(program_info)
    generator.generate(ast)
    return generator


class SemanticAndCodeGenTests(unittest.TestCase):
    def test_call_argument_order_is_right_to_left(self):
        """Push function call arguments from right to left"""
        source = """
        function f(x, y) {
            return x - y;
        }

        function main() {
            return f(1, 2);
        }
        """

        generator = build_codegen(source)
        code = generator.instructions
        f_addr = generator.functions_map["f"].address

        call_index = next(
            i
            for i, inst in enumerate(code)
            if inst.op == OpCode.CALL and inst.arg == f_addr
        )

        self.assertEqual(code[call_index - 2].op, OpCode.IPUSH)
        self.assertEqual(code[call_index - 2].arg, 2)
        self.assertEqual(code[call_index - 1].op, OpCode.IPUSH)
        self.assertEqual(code[call_index - 1].arg, 1)

    def test_call_addresses_are_patched(self):
        """Patch function call targets after code generation"""
        source = """
        function main() {
            return sub();
        }

        function sub() {
            return 99;
        }
        """

        code, _ = compile_program(source)
        for inst in code:
            if inst.op == OpCode.CALL:
                self.assertIsInstance(inst.arg, int)

    def test_shadowing_in_nested_block_is_allowed(self):
        """Allow a nested block to shadow an outer local variable"""
        source = """
        function main() {
            var x = 1;
            {
                var x = 2;
                return x;
            }
        }
        """

        code, _ = compile_program(source)
        self.assertTrue(len(code) > 0)

    def test_duplicate_local_in_same_scope_is_error(self):
        """Reject duplicate local variables in the same scope"""
        source = """
        function main() {
            var x = 1;
            var x = 2;
            return x;
        }
        """

        with self.assertRaises(SemanticError):
            analyze_program(source)

    def test_duplicate_local_in_same_scope_is_reported_with_reporter(self):
        """Report duplicate local variables through the diagnostic reporter"""
        source = """
        function main() {
            var x = 1;
            var x = 2;
            return x;
        }
        """

        _, _, reporter = analyze_program_with_reporter(source)
        self.assertTrue(reporter.has_errors())
        self.assertTrue(
            any(
                "duplicate local variable in same scope: x" in d.message
                for d in reporter.sorted_diagnostics()
            )
        )

    def test_outer_variable_visible_inside_inner_block(self):
        """Resolve an outer local variable from an inner block"""
        source = """
        function main() {
            var x = 10;
            {
                var y = 20;
                x = x + y;
            }
            return x;
        }
        """

        code, _ = compile_program(source)
        self.assertTrue(len(code) > 0)

    def test_local_scope_metadata_is_recorded(self):
        """Record scope metadata for local variables"""
        source = """
        function main(a, b) {
            var x = 1;
            {
                var y = 2;
                x = x + y;
            }
            return a + b + x;
        }
        """

        _, program_info = analyze_program(source)
        function_info = program_info.functions_map["main"]

        self.assertEqual(function_info.name, "main")
        self.assertEqual(len(function_info.params), 2)
        self.assertEqual(function_info.params[0].name, "a")
        self.assertEqual(function_info.params[0].type, INT_TYPE)
        self.assertEqual(function_info.params[1].name, "b")
        self.assertEqual(function_info.params[1].type, INT_TYPE)
        self.assertEqual(function_info.return_type, INT_TYPE)
        self.assertEqual(function_info.local_count, 2)

    def test_global_variable_metadata_is_recorded(self):
        """Record metadata for global variables"""
        source = """
        var g = 123;

        function main() {
            return g;
        }
        """

        _, program_info = analyze_program(source)
        g = program_info.globals_map["g"]

        self.assertEqual(g.name, "g")
        self.assertEqual(g.kind.value, "global")
        self.assertEqual(g.index, 0)
        self.assertEqual(g.type, INT_TYPE)

    def test_argument_count_check(self):
        """Reject function calls with the wrong number of arguments"""
        source = """
        function add(x, y) {
            return x + y;
        }

        function main() {
            return add(1);
        }
        """

        with self.assertRaises(SemanticError):
            analyze_program(source)

    def test_argument_count_is_reported_with_reporter(self):
        """Report wrong argument counts through the diagnostic reporter"""
        source = """
        function add(x, y) {
            return x + y;
        }

        function main() {
            return add(1);
        }
        """

        _, _, reporter = analyze_program_with_reporter(source)
        self.assertTrue(reporter.has_errors())
        self.assertTrue(
            any(
                "wrong number of arguments for add: expected 2, got 1" in d.message
                for d in reporter.sorted_diagnostics()
            )
        )

    def test_forward_reference_function_call_is_patched(self):
        """Patch a call to a function defined later in the source"""
        source = """
        function main() {
            return sub(10);
        }

        function sub(x) {
            return x + 1;
        }
        """

        generator = build_codegen(source)
        sub_addr = generator.functions_map["sub"].address
        call_insts = [inst for inst in generator.instructions if inst.op == OpCode.CALL]

        self.assertTrue(any(inst.arg == sub_addr for inst in call_insts))

    def test_assignment_to_non_identifier_is_error(self):
        """Reject assignment to a non-identifier expression"""
        source = """
        function main() {
            var x = 1;
            (x + 1) = 2;
            return x;
        }
        """

        with self.assertRaises(SemanticError):
            analyze_program(source)

    def test_assignment_to_non_identifier_is_reported_with_reporter(self):
        """Report assignment to a non-identifier through the diagnostic reporter"""
        source = """
        function main() {
            var x = 1;
            (x + 1) = 2;
            return x;
        }
        """

        _, _, reporter = analyze_program_with_reporter(source)
        self.assertTrue(reporter.has_errors())
        self.assertTrue(
            any(
                "left-hand side of assignment must be identifier" in d.message
                for d in reporter.sorted_diagnostics()
            )
        )

    def test_undefined_function_is_error(self):
        """Reject a call to an undefined function"""
        source = """
        function main() {
            return missing(1, 2);
        }
        """

        with self.assertRaises(SemanticError):
            analyze_program(source)

    def test_undefined_function_is_reported_with_reporter(self):
        """Report an undefined function through the diagnostic reporter"""
        source = """
        function main() {
            return missing(1, 2);
        }
        """

        _, _, reporter = analyze_program_with_reporter(source)
        self.assertTrue(reporter.has_errors())
        self.assertTrue(
            any(
                "undefined function: missing" in d.message
                for d in reporter.sorted_diagnostics()
            )
        )

    def test_undefined_variable_is_error_in_semantic_phase(self):
        """Reject an undefined variable during semantic analysis"""
        source = """
        function main() {
            return missing + 1;
        }
        """

        with self.assertRaises(SemanticError):
            analyze_program(source)

    def test_multiple_semantic_errors_are_collected_with_reporter(self):
        """Collect multiple semantic errors in one analysis"""
        source = """
        function foo(x, x) {
            return missing(1) + unknown;
        }

        function main() {
            var y = 1;
            var y = 2;
            return foo();
        }
        """

        _, _, reporter = analyze_program_with_reporter(source)
        messages = [d.message for d in reporter.sorted_diagnostics()]

        self.assertTrue(reporter.has_errors())
        self.assertTrue(
            any("duplicate parameter in function foo: x" in m for m in messages)
        )
        self.assertTrue(any("undefined function: missing" in m for m in messages))
        self.assertTrue(any("undefined variable: unknown" in m for m in messages))
        self.assertTrue(
            any("duplicate local variable in same scope: y" in m for m in messages)
        )
        self.assertTrue(
            any(
                "wrong number of arguments for foo: expected 1, got 0" in m
                for m in messages
            )
        )

    def test_asm_function_body_can_call_declared_function(self):
        """Allow an assembly body to call a declared ProtoLang function"""
        source = """
        function helper() {
            return 7;
        }

        function main() asm {
            .function helper
            CALL helper
            RET
        }
        """
        vm = run_source(source)
        self.assertIsNotNone(vm)
        self.assertEqual(vm.stack[vm.sp - 1], 7)

    def test_asm_function_call_requires_function_directive(self):
        """Require a .function directive for calls from an assembly body"""
        source = """
        function helper() {
            return 7;
        }

        function main() asm {
            CALL helper
            RET
        }
        """
        with self.assertRaises(SemanticError):
            analyze_program(source)

    def test_asm_function_call_requires_function_directive_is_reported_with_reporter(
        self,
    ):
        """Report a missing .function directive through the diagnostic reporter"""
        source = """
        function helper() {
            return 7;
        }

        function main() asm {
            CALL helper
            RET
        }
        """
        _, _, reporter = analyze_program_with_reporter(source)
        self.assertTrue(reporter.has_errors())
        self.assertTrue(
            any(
                "CALL target must be a local label or declared with .function: helper"
                in d.message
                for d in reporter.sorted_diagnostics()
            )
        )

    def test_codegen_missing_main_is_error_without_reporter(self):
        """Raise a code-generation error when main is missing without a reporter"""
        source = "var g = 1;"
        ast, program_info = analyze_program(source)
        generator = CodeGenerator(program_info)
        with self.assertRaises(CodeGenError):
            generator.generate(ast)

    def test_codegen_missing_main_is_reported_with_reporter(self):
        """Report a missing main function through the diagnostic reporter"""
        source = "var g = 1;"
        code, global_count, reporter = generate_program_with_reporter(source)
        self.assertIsNone(code)
        self.assertIsNone(global_count)
        self.assertTrue(reporter.has_errors())
        self.assertTrue(
            any(
                "undefined function: main" in d.message
                for d in reporter.sorted_diagnostics()
            )
        )

    def test_codegen_undefined_function_address_in_asm_is_reported_with_reporter(self):
        """Report an unresolved assembly function address through the diagnostic reporter"""
        source = """
        function main() asm {
            .function helper
            CALL helper
            RET
        }
        """

        code, global_count, reporter = generate_program_with_reporter(source)
        self.assertIsNone(code)
        self.assertIsNone(global_count)
        self.assertTrue(reporter.has_errors())
        self.assertTrue(
            any(
                "undefined function address: helper" in d.message
                for d in reporter.sorted_diagnostics()
            )
        )

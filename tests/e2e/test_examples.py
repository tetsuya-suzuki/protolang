import unittest

from protolang.main import run_file
from protolang.main import run_source


class ExampleTests(unittest.TestCase):
    def check_result(self, relpath: str, expected: int):
        vm = run_file(relpath)
        self.assertEqual(vm.stack[vm.sp - 1], expected)

    def test_examples(self):
        """Execute all bundled example programs and verify their results"""
        self.check_result("examples/00_gcd.ptl", 6)
        self.check_result("examples/01_return_expression_value.ptl", 3)
        self.check_result(
            "examples/02_return_the_latest_expression_statement_value.ptl", 42
        )
        self.check_result("examples/03_return_the_default_value.ptl", 0)
        self.check_result("examples/04_global_variable.ptl", 15)
        self.check_result("examples/05_local_variable.ptl", 15)
        self.check_result("examples/06_shadowing.ptl", 2)
        self.check_result("examples/07_assign.ptl", 14)
        self.check_result("examples/08_if_else.ptl", 1)
        self.check_result("examples/09_while.ptl", 55)
        self.check_result("examples/10_call.ptl", 55)
        self.check_result("examples/11_recursive_call.ptl", 55)
        self.check_result("examples/12_tail_recursive_call.ptl", 55)
        self.check_result("examples/13_asm_body.ptl", 5)

    def test_nested_scope_shadowing(self):
        """Execute a program that shadows a variable in a nested block"""
        source = """
        function main() {
            var x = 1;
            {
                var x = 2;
                return x;
            }
        }
        """

        vm = run_source(source)
        self.assertEqual(vm.stack[vm.sp - 1], 2)

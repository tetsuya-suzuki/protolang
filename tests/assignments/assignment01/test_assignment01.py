import unittest

from protolang.main import run_file


class Assignment01Tests(unittest.TestCase):
    def test_return_constant(self):
        """Execute a program that returns a constant value"""
        vm = run_file("tests/assignments/assignment01/cases/ok_01.ptl")
        self.assertEqual(vm.stack[vm.sp - 1], 123)

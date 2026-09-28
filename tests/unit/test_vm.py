import unittest

from protolang.instruction import Instruction
from protolang.instruction import OpCode
from protolang.vm import VirtualMachine


class VMTests(unittest.TestCase):
    def test_simple_arithmetic(self):
        """Execute simple integer arithmetic on the virtual machine"""
        code = [
            Instruction(OpCode.IPUSH, 1),
            Instruction(OpCode.IPUSH, 2),
            Instruction(OpCode.IPUSH, 3),
            Instruction(OpCode.IMUL),
            Instruction(OpCode.IADD),
            Instruction(OpCode.HALT),
        ]

        vm = VirtualMachine(code)
        vm.run()

        self.assertEqual(vm.stack[vm.sp - 1], 7)

    def test_validate_arity(self):
        """Reject an instruction with an invalid operand arity"""
        with self.assertRaises(ValueError):
            Instruction(OpCode.IADD, 1)

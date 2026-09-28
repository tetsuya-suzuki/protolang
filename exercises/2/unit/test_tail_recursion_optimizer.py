import unittest

from protolang.ast import BinaryOp
from protolang.ast import Block
from protolang.ast import Call
from protolang.ast import FunctionDefinition
from protolang.ast import Identifier
from protolang.ast import IfStatement
from protolang.ast import Number
from protolang.ast import Program
from protolang.ast import ReturnStatement
from protolang.ast import TailRecursiveCallStatement
from protolang.main import run_source
from protolang.optimizer import Optimizer
from protolang.token import SourceLocation
from protolang.token import SourceSpan
from protolang.token import TokenKind


SPAN = SourceSpan(
    start=SourceLocation(line=1, column=1),
    end=SourceLocation(line=1, column=2),
)


def ident(name: str) -> Identifier:
    return Identifier(span=SPAN, name=name)


def number(value: int) -> Number:
    return Number(span=SPAN, value=value)


def call(name: str, args) -> Call:
    return Call(span=SPAN, func_name=name, args=args)


def function(name: str, statements) -> FunctionDefinition:
    return FunctionDefinition(
        span=SPAN,
        name=name,
        params=["n"],
        body=Block(span=SPAN, items=statements),
    )


def optimize(program: Program) -> Program:
    return Optimizer(level=2).optimize(program)


class TailRecursionOptimizerTests(unittest.TestCase):
    def test_01_transform_tail_call_to_current_function(self):
        """EX2-5_01 Transform a tail call to the current function"""
        program = Program(
            span=SPAN,
            items=[
                function(
                    "f", [ReturnStatement(span=SPAN, expr=call("f", [ident("n")]))]
                )
            ],
        )

        result = optimize(program)

        stmt = result.items[0].body.items[0]
        self.assertEqual(stmt, TailRecursiveCallStatement(span=SPAN, args=[ident("n")]))

    def test_02_do_not_transform_call_to_another_function(self):
        """EX2-5_02 Do not transform a tail call to another function"""
        stmt = ReturnStatement(span=SPAN, expr=call("g", [ident("n")]))
        program = Program(span=SPAN, items=[function("f", [stmt])])

        result = optimize(program)

        self.assertIsInstance(result.items[0].body.items[0], ReturnStatement)

    def test_03_do_not_transform_non_tail_recursive_call(self):
        """EX2-5_03 Do not transform a recursive call inside another expression"""
        expr = BinaryOp(
            span=SPAN,
            op=TokenKind.PLUS,
            left=number(1),
            right=call("f", [ident("n")]),
        )
        program = Program(
            span=SPAN,
            items=[function("f", [ReturnStatement(span=SPAN, expr=expr)])],
        )

        result = optimize(program)

        self.assertIsInstance(result.items[0].body.items[0], ReturnStatement)
        self.assertIsInstance(result.items[0].body.items[0].expr.right, Call)

    def test_04_transform_tail_calls_inside_control_structures(self):
        """EX2-5_04 Transform tail calls nested in blocks and if statements"""
        then_stmt = ReturnStatement(span=SPAN, expr=call("f", [number(0)]))
        else_stmt = Block(
            span=SPAN,
            items=[ReturnStatement(span=SPAN, expr=call("f", [number(1)]))],
        )
        program = Program(
            span=SPAN,
            items=[
                function(
                    "f",
                    [
                        IfStatement(
                            span=SPAN,
                            condition=ident("n"),
                            then_stmt=then_stmt,
                            else_stmt=else_stmt,
                        )
                    ],
                )
            ],
        )

        result = optimize(program)
        if_stmt = result.items[0].body.items[0]

        self.assertIsInstance(if_stmt.then_stmt, TailRecursiveCallStatement)
        self.assertIsInstance(if_stmt.else_stmt.items[0], TailRecursiveCallStatement)

    def test_05_use_each_function_name_as_transformation_context(self):
        """EX2-5_05 Optimize only self tail calls"""
        f = function("f", [ReturnStatement(span=SPAN, expr=call("f", [ident("n")]))])
        g = function("g", [ReturnStatement(span=SPAN, expr=call("f", [ident("n")]))])
        program = Program(span=SPAN, items=[f, g])

        result = optimize(program)

        self.assertIsInstance(result.items[0].body.items[0], TailRecursiveCallStatement)
        self.assertIsInstance(result.items[1].body.items[0], ReturnStatement)

    def test_06_execute_tail_recursive_function_with_O2(self):
        """EX2-5_06 Generate executable code for an optimized tail-recursive call"""
        source = """
        function factorial(n, acc) {
            if (n <= 1) {
                return acc;
            }
            return factorial(n - 1, acc * n);
        }

        function main() {
            return factorial(5, 1);
        }
        """

        vm = run_source(source, optimization_level=2)

        self.assertIsNotNone(vm)
        self.assertEqual(vm.stack[vm.sp - 1], 120)
        self.assertLessEqual(vm.max_sp, 10)  # Ensure that the stack size is small


if __name__ == "__main__":
    unittest.main()

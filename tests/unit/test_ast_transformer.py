import unittest

from protolang.ast import ASTNode
from protolang.ast import BinaryOp
from protolang.ast import Block
from protolang.ast import ExpressionStatement
from protolang.ast import FunctionDefinition
from protolang.ast import LogicalAnd
from protolang.ast import Number
from protolang.ast import Program
from protolang.ast import ReturnStatement
from protolang.ast import UnaryOp
from protolang.ast_transformer import ASTTransformer
from protolang.asm_parser import AsmBlock
from protolang.asm_parser import AsmInstruction
from protolang.asm_parser import AsmLine
from protolang.token import SourceLocation
from protolang.token import SourceSpan
from protolang.token import TokenKind


LOCATION = SourceLocation(1, 1)
SPAN = SourceSpan(LOCATION, LOCATION)


class IncrementNumbers(ASTTransformer):
    def transform_Number(self, node: Number) -> ASTNode:
        return self.replace(node, Number(span=node.span, value=node.value + 1))


class ASTTransformerTests(unittest.TestCase):
    def test_transform_recursively_transforms_ast_children(self):
        """Recursively transform child nodes throughout an AST"""
        expression = LogicalAnd(
            span=SPAN,
            operands=[
                UnaryOp(
                    span=SPAN,
                    op=TokenKind.MINUS,
                    expr=BinaryOp(
                        span=SPAN,
                        op=TokenKind.PLUS,
                        left=Number(span=SPAN, value=1),
                        right=Number(span=SPAN, value=2),
                    ),
                ),
                Number(span=SPAN, value=3),
            ],
        )
        program = Program(
            span=SPAN,
            items=[
                FunctionDefinition(
                    span=SPAN,
                    name="main",
                    params=[],
                    body=Block(
                        span=SPAN,
                        items=[
                            ExpressionStatement(span=SPAN, expr=expression),
                            ReturnStatement(
                                span=SPAN,
                                expr=Number(span=SPAN, value=4),
                            ),
                        ],
                    ),
                )
            ],
        )

        transformed = IncrementNumbers().transform(program)

        self.assertIs(transformed, program)
        function = program.items[0]
        self.assertIsInstance(function, FunctionDefinition)
        assert isinstance(function, FunctionDefinition)
        self.assertIsInstance(function.body, Block)
        assert isinstance(function.body, Block)
        expression_statement = function.body.items[0]
        assert isinstance(expression_statement, ExpressionStatement)
        logical_and = expression_statement.expr
        assert isinstance(logical_and, LogicalAnd)
        unary = logical_and.operands[0]
        assert isinstance(unary, UnaryOp)
        binary = unary.expr
        assert isinstance(binary, BinaryOp)
        self.assertEqual(binary.left.value, 2)
        self.assertEqual(binary.right.value, 3)
        self.assertEqual(logical_and.operands[1].value, 4)
        return_statement = function.body.items[1]
        assert isinstance(return_statement, ReturnStatement)
        assert isinstance(return_statement.expr, Number)
        self.assertEqual(return_statement.expr.value, 5)

    def test_transform_rejects_an_unknown_ast_node(self):
        """Reject unsupported AST node types"""

        class UnknownNode(ASTNode):
            pass

        with self.assertRaisesRegex(TypeError, "unsupported AST node: UnknownNode"):
            ASTTransformer().transform(UnknownNode(span=SPAN))

    def test_transform_accepts_an_assembly_body(self):
        """Traverse an assembly function body without changing it"""
        instruction = AsmInstruction(span=SPAN, mnemonic="HALT", operand=None)
        body = AsmBlock(
            span=SPAN,
            lines=[AsmLine(span=SPAN, label=None, item=instruction)],
        )

        transformed = ASTTransformer().transform(body)

        self.assertIs(transformed, body)
        self.assertIs(body.lines[0].item, instruction)


if __name__ == "__main__":
    unittest.main()

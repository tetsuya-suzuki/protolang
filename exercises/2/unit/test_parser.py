import unittest

from protolang.lexer import Lexer
from protolang.token import TokenKind
from protolang.parser import Parser
from protolang.ast import FunctionDefinition
from protolang.ast import Block
from protolang.diagnostics import DiagnosticReporter
from protolang.ast import UnaryOp
from protolang.ast import BinaryOp
from protolang.ast import ExpressionStatement
from protolang.ast import Number
from protolang.ast import Program
from protolang.token import SourceLocation
from protolang.token import SourceSpan
from protolang.token import TokenKind
from protolang.ast import DoWhileStatement
from protolang.ast import RepeatUntilStatement
from protolang.ast import IfStatement
from protolang.ast import LogicalAnd
from protolang.ast import LogicalOr
from protolang.ast import Assignment
from dataclasses import is_dataclass, fields


def ast_equal(a, b, ignore_fields={"span"}):
    if type(a) is not type(b):
        return False

    if is_dataclass(a):
        for f in fields(a):
            if f.name in ignore_fields:
                continue
            if not ast_equal(getattr(a, f.name), getattr(b, f.name), ignore_fields):
                return False
        return True

    if isinstance(a, list):
        if len(a) != len(b):
            return False
        return all(ast_equal(x, y, ignore_fields) for x, y in zip(a, b))

    return a == b


class ParseTests(unittest.TestCase):
    def assertASTEqual(self, actual, expected, msg, ignore_fields={"span"}):
        self.assertTrue(ast_equal(actual, expected, ignore_fields), msg)

    def parse(self, source: str):
        reporter = DiagnosticReporter(source, filename="test_code")

        lexer = Lexer(source, reporter=reporter)
        parser = Parser(lexer, reporter=reporter)
        ast = parser.parse_program()
        return ast

    def test_01_mod_operator(self):
        """EX2-2_01 Parse an expression with the modulo operator"""
        source = "function main() { 10 % 3; }"
        actual_ast = self.parse(source=source)
        expected_ast = Program(
            span=SourceSpan(
                start=SourceLocation(line=1, column=1),
                end=SourceLocation(line=1, column=28),
            ),
            items=[
                FunctionDefinition(
                    span=SourceSpan(
                        start=SourceLocation(line=1, column=1),
                        end=SourceLocation(line=1, column=28),
                    ),
                    name="main",
                    params=[],
                    body=Block(
                        span=SourceSpan(
                            start=SourceLocation(line=1, column=17),
                            end=SourceLocation(line=1, column=28),
                        ),
                        items=[
                            ExpressionStatement(
                                span=SourceSpan(
                                    start=SourceLocation(line=1, column=19),
                                    end=SourceLocation(line=1, column=26),
                                ),
                                expr=BinaryOp(
                                    span=SourceSpan(
                                        start=SourceLocation(line=1, column=19),
                                        end=SourceLocation(line=1, column=25),
                                    ),
                                    op=TokenKind.PERCENT,
                                    left=Number(
                                        span=SourceSpan(
                                            start=SourceLocation(line=1, column=19),
                                            end=SourceLocation(line=1, column=21),
                                        ),
                                        value=10,
                                    ),
                                    right=Number(
                                        span=SourceSpan(
                                            start=SourceLocation(line=1, column=24),
                                            end=SourceLocation(line=1, column=25),
                                        ),
                                        value=3,
                                    ),
                                ),
                            )
                        ],
                    ),
                    name_span=SourceSpan(
                        start=SourceLocation(line=1, column=10),
                        end=SourceLocation(line=1, column=14),
                    ),
                    param_spans=[],
                )
            ],
        )
        msg = "The AST does not match the expected structure for the expression with the modulo operator."
        self.assertASTEqual(actual_ast, expected_ast, msg, ignore_fields={"span"})

    def test_02_do_while_statement(self):
        """EX2-2_02 Parse a do-while statement"""
        source = "function main() { do { 1; } while (0); }"
        actual_ast = self.parse(source=source)
        expected_ast = Program(
            span=SourceSpan(
                start=SourceLocation(line=1, column=1),
                end=SourceLocation(line=1, column=41),
            ),
            items=[
                FunctionDefinition(
                    span=SourceSpan(
                        start=SourceLocation(line=1, column=1),
                        end=SourceLocation(line=1, column=41),
                    ),
                    name="main",
                    params=[],
                    body=Block(
                        span=SourceSpan(
                            start=SourceLocation(line=1, column=17),
                            end=SourceLocation(line=1, column=41),
                        ),
                        items=[
                            DoWhileStatement(
                                span=SourceSpan(
                                    start=SourceLocation(line=1, column=19),
                                    end=SourceLocation(line=1, column=37),
                                ),
                                body=Block(
                                    span=SourceSpan(
                                        start=SourceLocation(line=1, column=22),
                                        end=SourceLocation(line=1, column=28),
                                    ),
                                    items=[
                                        ExpressionStatement(
                                            span=SourceSpan(
                                                start=SourceLocation(line=1, column=24),
                                                end=SourceLocation(line=1, column=26),
                                            ),
                                            expr=Number(
                                                span=SourceSpan(
                                                    start=SourceLocation(
                                                        line=1, column=24
                                                    ),
                                                    end=SourceLocation(
                                                        line=1, column=25
                                                    ),
                                                ),
                                                value=1,
                                            ),
                                        )
                                    ],
                                ),
                                condition=Number(
                                    span=SourceSpan(
                                        start=SourceLocation(line=1, column=36),
                                        end=SourceLocation(line=1, column=37),
                                    ),
                                    value=0,
                                ),
                            )
                        ],
                    ),
                    name_span=SourceSpan(
                        start=SourceLocation(line=1, column=10),
                        end=SourceLocation(line=1, column=14),
                    ),
                    param_spans=[],
                )
            ],
        )
        msg = (
            "The AST does not match the expected structure for the do-while statement."
        )
        self.assertASTEqual(actual_ast, expected_ast, msg, ignore_fields={"span"})

    def test_03_repeat_until_statement(self):
        """EX2-2_03 Parse a repeat-until statement"""
        source = "function main() { repeat { 1; } until (0); }"
        actual_ast = self.parse(source=source)
        expected_ast = Program(
            span=SourceSpan(
                start=SourceLocation(line=1, column=1),
                end=SourceLocation(line=1, column=45),
            ),
            items=[
                FunctionDefinition(
                    span=SourceSpan(
                        start=SourceLocation(line=1, column=1),
                        end=SourceLocation(line=1, column=45),
                    ),
                    name="main",
                    params=[],
                    body=Block(
                        span=SourceSpan(
                            start=SourceLocation(line=1, column=17),
                            end=SourceLocation(line=1, column=45),
                        ),
                        items=[
                            RepeatUntilStatement(
                                span=SourceSpan(
                                    start=SourceLocation(line=1, column=19),
                                    end=SourceLocation(line=1, column=41),
                                ),
                                body=Block(
                                    span=SourceSpan(
                                        start=SourceLocation(line=1, column=26),
                                        end=SourceLocation(line=1, column=32),
                                    ),
                                    items=[
                                        ExpressionStatement(
                                            span=SourceSpan(
                                                start=SourceLocation(line=1, column=28),
                                                end=SourceLocation(line=1, column=30),
                                            ),
                                            expr=Number(
                                                span=SourceSpan(
                                                    start=SourceLocation(
                                                        line=1, column=28
                                                    ),
                                                    end=SourceLocation(
                                                        line=1, column=29
                                                    ),
                                                ),
                                                value=1,
                                            ),
                                        )
                                    ],
                                ),
                                condition=Number(
                                    span=SourceSpan(
                                        start=SourceLocation(line=1, column=40),
                                        end=SourceLocation(line=1, column=41),
                                    ),
                                    value=0,
                                ),
                            )
                        ],
                    ),
                    name_span=SourceSpan(
                        start=SourceLocation(line=1, column=10),
                        end=SourceLocation(line=1, column=14),
                    ),
                    param_spans=[],
                )
            ],
        )
        msg = "The AST does not match the expected structure for the repeat-until statement."
        self.assertASTEqual(actual_ast, expected_ast, msg, ignore_fields={"span"})

    def test_04_if_statement_without_else_part(self):
        """EX2-2_04 Parse an if statement without else part"""
        source = "function main() { if (0) { 1; } }"
        actual_ast = self.parse(source=source)
        expected_ast = Program(
            span=SourceSpan(
                start=SourceLocation(line=1, column=1),
                end=SourceLocation(line=1, column=34),
            ),
            items=[
                FunctionDefinition(
                    span=SourceSpan(
                        start=SourceLocation(line=1, column=1),
                        end=SourceLocation(line=1, column=34),
                    ),
                    name="main",
                    params=[],
                    body=Block(
                        span=SourceSpan(
                            start=SourceLocation(line=1, column=17),
                            end=SourceLocation(line=1, column=34),
                        ),
                        items=[
                            IfStatement(
                                span=SourceSpan(
                                    start=SourceLocation(line=1, column=19),
                                    end=SourceLocation(line=1, column=32),
                                ),
                                condition=Number(
                                    span=SourceSpan(
                                        start=SourceLocation(line=1, column=23),
                                        end=SourceLocation(line=1, column=24),
                                    ),
                                    value=0,
                                ),
                                then_stmt=Block(
                                    span=SourceSpan(
                                        start=SourceLocation(line=1, column=26),
                                        end=SourceLocation(line=1, column=32),
                                    ),
                                    items=[
                                        ExpressionStatement(
                                            span=SourceSpan(
                                                start=SourceLocation(line=1, column=28),
                                                end=SourceLocation(line=1, column=30),
                                            ),
                                            expr=Number(
                                                span=SourceSpan(
                                                    start=SourceLocation(
                                                        line=1, column=28
                                                    ),
                                                    end=SourceLocation(
                                                        line=1, column=29
                                                    ),
                                                ),
                                                value=1,
                                            ),
                                        )
                                    ],
                                ),
                                else_stmt=None,
                            )
                        ],
                    ),
                    name_span=SourceSpan(
                        start=SourceLocation(line=1, column=10),
                        end=SourceLocation(line=1, column=14),
                    ),
                    param_spans=[],
                )
            ],
        )
        msg = "The AST does not match the expected structure for the if-statement without else part."
        self.assertASTEqual(actual_ast, expected_ast, msg, ignore_fields={"span"})

    def test_05_lnot_operator(self):
        """EX2-2_05 Parse an expression with logical NOT"""
        source = "function main() { !0; }"
        actual_ast = self.parse(source=source)
        expected_ast = Program(
            span=SourceSpan(
                start=SourceLocation(line=1, column=1),
                end=SourceLocation(line=1, column=24),
            ),
            items=[
                FunctionDefinition(
                    span=SourceSpan(
                        start=SourceLocation(line=1, column=1),
                        end=SourceLocation(line=1, column=24),
                    ),
                    name="main",
                    params=[],
                    body=Block(
                        span=SourceSpan(
                            start=SourceLocation(line=1, column=17),
                            end=SourceLocation(line=1, column=24),
                        ),
                        items=[
                            ExpressionStatement(
                                span=SourceSpan(
                                    start=SourceLocation(line=1, column=19),
                                    end=SourceLocation(line=1, column=22),
                                ),
                                expr=UnaryOp(
                                    span=SourceSpan(
                                        start=SourceLocation(line=1, column=19),
                                        end=SourceLocation(line=1, column=21),
                                    ),
                                    op=TokenKind.LNOT,
                                    expr=Number(
                                        span=SourceSpan(
                                            start=SourceLocation(line=1, column=20),
                                            end=SourceLocation(line=1, column=21),
                                        ),
                                        value=0,
                                    ),
                                ),
                            )
                        ],
                    ),
                    name_span=SourceSpan(
                        start=SourceLocation(line=1, column=10),
                        end=SourceLocation(line=1, column=14),
                    ),
                    param_spans=[],
                )
            ],
        )
        msg = "The AST does not match the expected structure for the expression with logical NOT."
        self.assertASTEqual(actual_ast, expected_ast, msg, ignore_fields={"span"})

    def test_06_land_operator(self):
        """EX2-2_06 Parse an expression with logical AND"""
        source = "function main() { 0 && 1; }"
        actual_ast = self.parse(source=source)
        expected_ast = Program(
            span=SourceSpan(
                start=SourceLocation(line=1, column=1),
                end=SourceLocation(line=1, column=28),
            ),
            items=[
                FunctionDefinition(
                    span=SourceSpan(
                        start=SourceLocation(line=1, column=1),
                        end=SourceLocation(line=1, column=28),
                    ),
                    name="main",
                    params=[],
                    body=Block(
                        span=SourceSpan(
                            start=SourceLocation(line=1, column=17),
                            end=SourceLocation(line=1, column=28),
                        ),
                        items=[
                            ExpressionStatement(
                                span=SourceSpan(
                                    start=SourceLocation(line=1, column=19),
                                    end=SourceLocation(line=1, column=26),
                                ),
                                expr=LogicalAnd(
                                    span=SourceSpan(
                                        start=SourceLocation(line=1, column=19),
                                        end=SourceLocation(line=1, column=25),
                                    ),
                                    operands=[
                                        Number(
                                            span=SourceSpan(
                                                start=SourceLocation(line=1, column=19),
                                                end=SourceLocation(line=1, column=20),
                                            ),
                                            value=0,
                                        ),
                                        Number(
                                            span=SourceSpan(
                                                start=SourceLocation(line=1, column=24),
                                                end=SourceLocation(line=1, column=25),
                                            ),
                                            value=1,
                                        ),
                                    ],
                                ),
                            )
                        ],
                    ),
                    name_span=SourceSpan(
                        start=SourceLocation(line=1, column=10),
                        end=SourceLocation(line=1, column=14),
                    ),
                    param_spans=[],
                )
            ],
        )
        msg = "The AST does not match the expected structure for the expression with logical AND."
        self.assertASTEqual(actual_ast, expected_ast, msg, ignore_fields={"span"})

    def test_07_lor_operator(self):
        """EX2-2_07 Parse an expression with logical OR"""
        source = "function main() { 0 || 1; }"
        actual_ast = self.parse(source=source)
        expected_ast = Program(
            span=SourceSpan(
                start=SourceLocation(line=1, column=1),
                end=SourceLocation(line=1, column=28),
            ),
            items=[
                FunctionDefinition(
                    span=SourceSpan(
                        start=SourceLocation(line=1, column=1),
                        end=SourceLocation(line=1, column=28),
                    ),
                    name="main",
                    params=[],
                    body=Block(
                        span=SourceSpan(
                            start=SourceLocation(line=1, column=17),
                            end=SourceLocation(line=1, column=28),
                        ),
                        items=[
                            ExpressionStatement(
                                span=SourceSpan(
                                    start=SourceLocation(line=1, column=19),
                                    end=SourceLocation(line=1, column=26),
                                ),
                                expr=LogicalOr(
                                    span=SourceSpan(
                                        start=SourceLocation(line=1, column=19),
                                        end=SourceLocation(line=1, column=25),
                                    ),
                                    operands=[
                                        Number(
                                            span=SourceSpan(
                                                start=SourceLocation(line=1, column=19),
                                                end=SourceLocation(line=1, column=20),
                                            ),
                                            value=0,
                                        ),
                                        Number(
                                            span=SourceSpan(
                                                start=SourceLocation(line=1, column=24),
                                                end=SourceLocation(line=1, column=25),
                                            ),
                                            value=1,
                                        ),
                                    ],
                                ),
                            )
                        ],
                    ),
                    name_span=SourceSpan(
                        start=SourceLocation(line=1, column=10),
                        end=SourceLocation(line=1, column=14),
                    ),
                    param_spans=[],
                )
            ],
        )
        msg = "The AST does not match the expected structure for the expression with logical OR."
        self.assertASTEqual(actual_ast, expected_ast, msg, ignore_fields={"span"})

    def test_08_logical_expression(self):
        """EX2-2_08 Parse a logical expression with logical NOT, logical AND, and logical OR"""
        source = "function main() { !0 && (1 || 2) || 3; }"
        actual_ast = self.parse(source=source)
        expected_ast = Program(
            span=SourceSpan(
                start=SourceLocation(line=1, column=1),
                end=SourceLocation(line=1, column=41),
            ),
            items=[
                FunctionDefinition(
                    span=SourceSpan(
                        start=SourceLocation(line=1, column=1),
                        end=SourceLocation(line=1, column=41),
                    ),
                    name="main",
                    params=[],
                    body=Block(
                        span=SourceSpan(
                            start=SourceLocation(line=1, column=17),
                            end=SourceLocation(line=1, column=41),
                        ),
                        items=[
                            ExpressionStatement(
                                span=SourceSpan(
                                    start=SourceLocation(line=1, column=19),
                                    end=SourceLocation(line=1, column=39),
                                ),
                                expr=LogicalOr(
                                    span=SourceSpan(
                                        start=SourceLocation(line=1, column=19),
                                        end=SourceLocation(line=1, column=38),
                                    ),
                                    operands=[
                                        LogicalAnd(
                                            span=SourceSpan(
                                                start=SourceLocation(line=1, column=19),
                                                end=SourceLocation(line=1, column=33),
                                            ),
                                            operands=[
                                                UnaryOp(
                                                    span=SourceSpan(
                                                        start=SourceLocation(
                                                            line=1, column=19
                                                        ),
                                                        end=SourceLocation(
                                                            line=1, column=21
                                                        ),
                                                    ),
                                                    op=TokenKind.LNOT,
                                                    expr=Number(
                                                        span=SourceSpan(
                                                            start=SourceLocation(
                                                                line=1, column=20
                                                            ),
                                                            end=SourceLocation(
                                                                line=1, column=21
                                                            ),
                                                        ),
                                                        value=0,
                                                    ),
                                                ),
                                                LogicalOr(
                                                    span=SourceSpan(
                                                        start=SourceLocation(
                                                            line=1, column=25
                                                        ),
                                                        end=SourceLocation(
                                                            line=1, column=33
                                                        ),
                                                    ),
                                                    operands=[
                                                        Number(
                                                            span=SourceSpan(
                                                                start=SourceLocation(
                                                                    line=1, column=26
                                                                ),
                                                                end=SourceLocation(
                                                                    line=1, column=27
                                                                ),
                                                            ),
                                                            value=1,
                                                        ),
                                                        Number(
                                                            span=SourceSpan(
                                                                start=SourceLocation(
                                                                    line=1, column=31
                                                                ),
                                                                end=SourceLocation(
                                                                    line=1, column=32
                                                                ),
                                                            ),
                                                            value=2,
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                        Number(
                                            span=SourceSpan(
                                                start=SourceLocation(line=1, column=37),
                                                end=SourceLocation(line=1, column=38),
                                            ),
                                            value=3,
                                        ),
                                    ],
                                ),
                            )
                        ],
                    ),
                    name_span=SourceSpan(
                        start=SourceLocation(line=1, column=10),
                        end=SourceLocation(line=1, column=14),
                    ),
                    param_spans=[],
                )
            ],
        )
        msg = "The AST does not match the expected structure for the expression with logical NOT, logical AND, and logical OR."
        self.assertASTEqual(actual_ast, expected_ast, msg, ignore_fields={"span"})

    def test_09_invalid_assignment_expression(self):
        """EX2-2_09 Parse an invalid assignment expression"""
        source = "function main() { 0 = 1; }"
        actual_ast = self.parse(source=source)
        expected_ast = Program(
            span=SourceSpan(
                start=SourceLocation(line=1, column=1),
                end=SourceLocation(line=1, column=27),
            ),
            items=[
                FunctionDefinition(
                    span=SourceSpan(
                        start=SourceLocation(line=1, column=1),
                        end=SourceLocation(line=1, column=27),
                    ),
                    name="main",
                    params=[],
                    body=Block(
                        span=SourceSpan(
                            start=SourceLocation(line=1, column=17),
                            end=SourceLocation(line=1, column=27),
                        ),
                        items=[
                            ExpressionStatement(
                                span=SourceSpan(
                                    start=SourceLocation(line=1, column=19),
                                    end=SourceLocation(line=1, column=25),
                                ),
                                expr=Assignment(
                                    span=SourceSpan(
                                        start=SourceLocation(line=1, column=19),
                                        end=SourceLocation(line=1, column=24),
                                    ),
                                    left=Number(
                                        span=SourceSpan(
                                            start=SourceLocation(line=1, column=19),
                                            end=SourceLocation(line=1, column=20),
                                        ),
                                        value=0,
                                    ),
                                    right=Number(
                                        span=SourceSpan(
                                            start=SourceLocation(line=1, column=23),
                                            end=SourceLocation(line=1, column=24),
                                        ),
                                        value=1,
                                    ),
                                ),
                            )
                        ],
                    ),
                    name_span=SourceSpan(
                        start=SourceLocation(line=1, column=10),
                        end=SourceLocation(line=1, column=14),
                    ),
                    param_spans=[],
                )
            ],
        )
        msg = "The AST does not match the expected structure for the invalid assignment expression."
        self.assertASTEqual(actual_ast, expected_ast, msg, ignore_fields={"span"})

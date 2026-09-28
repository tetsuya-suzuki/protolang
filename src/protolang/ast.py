from __future__ import annotations

from dataclasses import dataclass

from .token import SourceSpan
from .token import TokenKind

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .asm_parser import AsmBlock
    from .semantic import FunctionInfo, Type, VarInfo


@dataclass
class ASTNode:
    span: SourceSpan


class Statement(ASTNode):
    pass


class Expression(ASTNode):
    type: Type | None = None


@dataclass
class Number(Expression):
    value: int


@dataclass
class Identifier(Expression):
    name: str
    var_info: VarInfo | None = None


@dataclass
class UnaryOp(Expression):
    op: TokenKind
    expr: Expression


@dataclass
class BinaryOp(Expression):
    op: TokenKind
    left: Expression
    right: Expression


# --- AST nodes for future language extensions ---
@dataclass
class LogicalAnd(Expression):
    operands: list[Expression]


@dataclass
class LogicalOr(Expression):
    operands: list[Expression]


# --- end of extension nodes ---


@dataclass
class Assignment(Expression):
    left: Expression
    right: Expression


@dataclass
class Call(Expression):
    func_name: str
    args: list[Expression]
    func_name_span: SourceSpan | None = None
    function_info: FunctionInfo | None = (
        None  # This field is set during semantic analysis
    )


@dataclass
class ExpressionStatement(Statement):
    expr: Expression


@dataclass
class ReturnStatement(Statement):
    expr: Expression | None


@dataclass
class TailRecursiveCallStatement(Statement):
    """Internal AST node produced only by tail-recursion optimization."""

    args: list[Expression]


@dataclass
class IfStatement(Statement):
    condition: Expression
    then_stmt: Statement
    else_stmt: Statement | None = None


@dataclass
class WhileStatement(Statement):
    condition: Expression
    body: Statement


@dataclass
class DoWhileStatement(Statement):  # for future extension
    body: Statement
    condition: Expression


@dataclass
class RepeatUntilStatement(Statement):  # for future extension
    body: Statement
    condition: Expression


@dataclass
class Declaration(ASTNode):
    name: str
    initializer: Expression
    name_span: SourceSpan | None = None
    var_info: VarInfo | None = None


@dataclass
class Block(Statement):
    items: list[Declaration | Statement]


@dataclass
class GlobalDeclaration(ASTNode):
    name: str
    initializer: Expression
    name_span: SourceSpan | None = None
    var_info: VarInfo | None = None


@dataclass
class FunctionDefinition(ASTNode):
    name: str
    params: list[str]
    body: Block | AsmBlock
    name_span: SourceSpan | None = None
    param_spans: list[SourceSpan] | None = None
    function_info: FunctionInfo | None = None


@dataclass
class Program(ASTNode):
    items: list[ASTNode]

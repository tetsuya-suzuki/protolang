from .ast import ASTNode
from .ast import Assignment
from .ast import BinaryOp
from .ast import Block
from .ast import Call
from .ast import Declaration
from .ast import DoWhileStatement
from .ast import Expression
from .ast import ExpressionStatement
from .ast import FunctionDefinition
from .ast import GlobalDeclaration
from .ast import Identifier
from .ast import IfStatement
from .ast import LogicalAnd
from .ast import LogicalOr
from .ast import Number
from .ast import Program
from .ast import RepeatUntilStatement
from .ast import ReturnStatement
from .ast import Statement
from .ast import TailRecursiveCallStatement
from .ast import UnaryOp
from .ast import WhileStatement
from .asm_parser import AsmBlock
from .asm_parser import AsmDirective
from .asm_parser import AsmInstruction
from .asm_parser import AsmLine


class ASTTransformer:
    """Bottom-up transformer for ProtoLang ASTs.

    Child nodes are transformed before the method for the current node is
    called. Subclasses may return the original node or a replacement node.
    The transformer updates nodes in place except where a rule replaces a node.
    """

    def __init__(self) -> None:
        self.changed = False

    def transform(self, node: ASTNode) -> ASTNode:
        if isinstance(node, Program):
            node.items = [self.transform(item) for item in node.items]
            return self.transform_Program(node)

        if isinstance(node, GlobalDeclaration):
            node.initializer = self.transform_expression(node.initializer)
            return self.transform_GlobalDeclaration(node)

        if isinstance(node, FunctionDefinition):
            if isinstance(node.body, ASTNode):
                body = self.transform(node.body)
                if not isinstance(body, (Block, AsmBlock)):
                    raise TypeError("a function body must remain a Block or AsmBlock")
                node.body = body
            return self.transform_FunctionDefinition(node)

        if isinstance(node, AsmBlock):
            lines = []
            for line in node.lines:
                transformed = self.transform(line)
                if not isinstance(transformed, AsmLine):
                    raise TypeError("an assembly line must remain an AsmLine")
                lines.append(transformed)
            node.lines = lines
            return self.transform_AsmBlock(node)

        if isinstance(node, AsmLine):
            if node.item is not None:
                item = self.transform(node.item)
                if not isinstance(item, (AsmDirective, AsmInstruction)):
                    raise TypeError(
                        "an assembly line item must remain an AsmDirective or AsmInstruction"
                    )
                node.item = item
            return self.transform_AsmLine(node)

        if isinstance(node, AsmDirective):
            return self.transform_AsmDirective(node)

        if isinstance(node, AsmInstruction):
            return self.transform_AsmInstruction(node)

        if isinstance(node, Declaration):
            node.initializer = self.transform_expression(node.initializer)
            return self.transform_Declaration(node)

        if isinstance(node, Block):
            items = []
            for item in node.items:
                transformed = self.transform(item)
                if not isinstance(transformed, (Declaration, Statement)):
                    raise TypeError(
                        "a block item must remain a declaration or statement"
                    )
                items.append(transformed)
            node.items = items
            return self.transform_Block(node)

        if isinstance(node, ExpressionStatement):
            node.expr = self.transform_expression(node.expr)
            return self.transform_ExpressionStatement(node)

        if isinstance(node, ReturnStatement):
            if node.expr is not None:
                node.expr = self.transform_expression(node.expr)
            return self.transform_ReturnStatement(node)

        if isinstance(node, TailRecursiveCallStatement):
            node.args = [self.transform_expression(arg) for arg in node.args]
            return self.transform_TailRecursiveCallStatement(node)

        if isinstance(node, IfStatement):
            node.condition = self.transform_expression(node.condition)
            node.then_stmt = self.transform_statement(node.then_stmt)
            if node.else_stmt is not None:
                node.else_stmt = self.transform_statement(node.else_stmt)
            return self.transform_IfStatement(node)

        if isinstance(node, WhileStatement):
            node.condition = self.transform_expression(node.condition)
            node.body = self.transform_statement(node.body)
            return self.transform_WhileStatement(node)

        if isinstance(node, DoWhileStatement):
            node.body = self.transform_statement(node.body)
            node.condition = self.transform_expression(node.condition)
            return self.transform_DoWhileStatement(node)

        if isinstance(node, RepeatUntilStatement):
            node.body = self.transform_statement(node.body)
            node.condition = self.transform_expression(node.condition)
            return self.transform_RepeatUntilStatement(node)

        if isinstance(node, Number):
            return self.transform_Number(node)

        if isinstance(node, Identifier):
            return self.transform_Identifier(node)

        if isinstance(node, UnaryOp):
            node.expr = self.transform_expression(node.expr)
            return self.transform_UnaryOp(node)

        if isinstance(node, BinaryOp):
            node.left = self.transform_expression(node.left)
            node.right = self.transform_expression(node.right)
            return self.transform_BinaryOp(node)

        if isinstance(node, LogicalAnd):
            node.operands = [self.transform_expression(expr) for expr in node.operands]
            return self.transform_LogicalAnd(node)

        if isinstance(node, LogicalOr):
            node.operands = [self.transform_expression(expr) for expr in node.operands]
            return self.transform_LogicalOr(node)

        if isinstance(node, Assignment):
            node.left = self.transform_expression(node.left)
            node.right = self.transform_expression(node.right)
            return self.transform_Assignment(node)

        if isinstance(node, Call):
            node.args = [self.transform_expression(arg) for arg in node.args]
            return self.transform_Call(node)

        raise TypeError(f"unsupported AST node: {type(node).__name__}")

    def transform_expression(self, node: Expression) -> Expression:
        transformed = self.transform(node)
        if not isinstance(transformed, Expression):
            raise TypeError("an expression must be transformed into an expression")
        return transformed

    def transform_statement(self, node: Statement) -> Statement:
        transformed = self.transform(node)
        if not isinstance(transformed, Statement):
            raise TypeError("a statement must be transformed into a statement")
        return transformed

    def transform_Program(self, node: Program) -> ASTNode:
        return node

    def transform_GlobalDeclaration(self, node: GlobalDeclaration) -> ASTNode:
        return node

    def transform_FunctionDefinition(self, node: FunctionDefinition) -> ASTNode:
        return node

    def transform_AsmBlock(self, node: AsmBlock) -> ASTNode:
        return node

    def transform_AsmLine(self, node: AsmLine) -> ASTNode:
        return node

    def transform_AsmDirective(self, node: AsmDirective) -> ASTNode:
        return node

    def transform_AsmInstruction(self, node: AsmInstruction) -> ASTNode:
        return node

    def transform_Declaration(self, node: Declaration) -> ASTNode:
        return node

    def transform_Block(self, node: Block) -> ASTNode:
        return node

    def transform_ExpressionStatement(self, node: ExpressionStatement) -> ASTNode:
        return node

    def transform_ReturnStatement(self, node: ReturnStatement) -> ASTNode:
        return node

    def transform_TailRecursiveCallStatement(
        self, node: TailRecursiveCallStatement
    ) -> ASTNode:
        return node

    def transform_IfStatement(self, node: IfStatement) -> ASTNode:
        return node

    def transform_WhileStatement(self, node: WhileStatement) -> ASTNode:
        return node

    def transform_DoWhileStatement(self, node: DoWhileStatement) -> ASTNode:
        return node

    def transform_RepeatUntilStatement(self, node: RepeatUntilStatement) -> ASTNode:
        return node

    def transform_Number(self, node: Number) -> ASTNode:
        return node

    def transform_Identifier(self, node: Identifier) -> ASTNode:
        return node

    def transform_UnaryOp(self, node: UnaryOp) -> ASTNode:
        return node

    def transform_BinaryOp(self, node: BinaryOp) -> ASTNode:
        return node

    def transform_LogicalAnd(self, node: LogicalAnd) -> ASTNode:
        return node

    def transform_LogicalOr(self, node: LogicalOr) -> ASTNode:
        return node

    def transform_Assignment(self, node: Assignment) -> ASTNode:
        return node

    def transform_Call(self, node: Call) -> ASTNode:
        return node

    def replace(self, old_node: ASTNode, new_node: ASTNode) -> ASTNode:
        if new_node is not old_node:
            self.changed = True
        return new_node

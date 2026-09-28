from .ast import ASTNode
from .ast import Block
from .ast import ExpressionStatement
from .ast import FunctionDefinition
from .ast import ReturnStatement
from .ast_transformer import ASTTransformer
from .ast import Program
from .ast import IfStatement


class ASTNormalizer(ASTTransformer):
    """Normalize ProtoLang ASTs for later compiler phases.

    In a ProtoLang function, falling off the end returns the latest expression
    value already kept on the stack. Normalization makes that implicit return
    explicit in the AST so later phases only need to handle ReturnStatement.
    """

    def normalize(self, node: Program) -> Program:
        program = self.transform(node)
        if not isinstance(program, Program):
            raise ValueError("Expected Program node after normalization")
        return program

    def _normalize_tail_IfStatement(self, node: IfStatement) -> IfStatement:
        if isinstance(node.then_stmt, Block):
            self._normalize_tail_Block(node.then_stmt)
        if node.else_stmt and isinstance(node.else_stmt, Block):
            self._normalize_tail_Block(node.else_stmt)
        elif node.else_stmt and isinstance(node.else_stmt, IfStatement):
            self._normalize_tail_IfStatement(node.else_stmt)
        return node

    def _normalize_tail_Block(self, node: Block) -> None:
        items = node.items

        if items and isinstance(items[-1], ReturnStatement):
            return

        if items and isinstance(items[-1], ExpressionStatement):
            trailing_exp_stmt = items[-1]
            items[-1] = ReturnStatement(
                span=trailing_exp_stmt.span, expr=trailing_exp_stmt.expr
            )
            self.changed = True
            return

        if items and isinstance(items[-1], IfStatement):
            trailing_if_stmt = items[-1]
            self._normalize_tail_IfStatement(trailing_if_stmt)

            if trailing_if_stmt.else_stmt is not None:
                return

            # The false path of an if without else still reaches
            # the end of the function.
            items.append(ReturnStatement(span=node.span, expr=None))
            self.changed = True
            return

        if items and isinstance(items[-1], Block):
            self._normalize_tail_Block(items[-1])
            return

        items.append(ReturnStatement(span=node.span, expr=None))
        self.changed = True

    def transform_FunctionDefinition(self, node: FunctionDefinition) -> ASTNode:
        if not isinstance(node.body, Block):
            return node

        self._normalize_tail_Block(node.body)
        return node

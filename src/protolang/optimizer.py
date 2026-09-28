from .ast import ASTNode
from .ast_transformer import ASTTransformer
from .ast import BinaryOp
from .ast import Call
from .ast import FunctionDefinition
from .ast import LogicalAnd
from .ast import LogicalOr
from .ast import Number
from .ast import ReturnStatement
from .ast import TailRecursiveCallStatement
from .ast import UnaryOp
from .asm_parser import AsmBlock
from .ast import Block
from .token import TokenKind
from .ast import Program


class ConstantFolder(ASTTransformer):
    """Fold expressions whose operands are integer constants."""

    def transform_BinaryOp(self, node: BinaryOp) -> ASTNode:
        # TODO: EX2-4 Extending the Optimizer (1)
        # Fold the binary operation if both operands are constants.

        return node

    def transform_UnaryOp(self, node: UnaryOp) -> ASTNode:
        # TODO: EX2-4 Extending the Optimizer (1)
        # Fold the unary operation if the operand is a constant.

        return node


class AlgebraicSimplifier(ASTTransformer):
    """Apply identity and short-circuit simplifications to expressions."""

    @staticmethod
    def _is_number(node: ASTNode, value: int) -> bool:
        return isinstance(node, Number) and node.value == value

    @staticmethod
    def _is_different_number(node: ASTNode, value: int) -> bool:
        return isinstance(node, Number) and node.value != value

    def transform_BinaryOp(self, node: BinaryOp) -> ASTNode:
        # TODO: EX2-4 Extending the Optimizer (1)
        # Simplify the binary operation according to the specification.

        return node

    def transform_LogicalOr(self, node: LogicalOr) -> ASTNode:
        operands = []
        for operand in node.operands:
            # TODO: EX2-4 Extending the Optimizer (1)
            pass

        if not operands:
            return self.replace(node, Number(span=node.span, value=0))
        if operands != node.operands:
            node.operands = operands
        return node

    def transform_LogicalAnd(self, node: LogicalAnd) -> ASTNode:
        operands = []
        for operand in node.operands:
            # TODO: EX2-4 Extending the Optimizer (1)
            pass

        if not operands:
            return self.replace(node, Number(span=node.span, value=1))
        if operands != node.operands:
            node.operands = operands
        return node


class TailRecursionOptimizer(ASTTransformer):
    """Replace tail calls to the current function with internal AST nodes."""

    def __init__(self) -> None:
        super().__init__()
        self.current_function_name: str | None = None

    def transform(self, node: ASTNode) -> ASTNode:
        if isinstance(node, FunctionDefinition):
            if self.current_function_name is not None:
                raise ValueError("Nested function definitions are not supported")

            self.current_function_name = node.name
            try:
                if isinstance(node.body, ASTNode):
                    body = self.transform(node.body)
                    if not isinstance(body, (Block | AsmBlock)):
                        raise ValueError("Expected Block or AsmBlock for function body")
                    node.body = body
                return node
            finally:
                self.current_function_name = None

        return super().transform(node)

    def transform_ReturnStatement(self, node: ReturnStatement) -> ASTNode:
        # TODO: EX2-5 Extending the Optimizer (2)
        # If this return statement returns a call to the current function,
        # replace it with a TailRecursiveCallStatement.
        return node


class Optimizer:
    """Apply AST optimizations selected by an optimization level.

    Level 0 performs no optimization.
    Level 1 performs local expression optimizations: constant folding and
    algebraic simplification.
    Level 2 includes level 1 and tail-recursion optimization.
    """

    def __init__(self, level: int = 0) -> None:
        if level not in (0, 1, 2):
            raise ValueError(f"unsupported optimization level: {level}")
        self.level = level

    def optimize(self, node: ASTNode) -> ASTNode:
        if self.level == 0:
            return node

        node = self._optimize_expressions(node)

        if self.level >= 2:
            node = self._optimize_control_structures(node)

        return node

    def _optimize_expressions(self, node: ASTNode) -> ASTNode:
        while True:
            folder = ConstantFolder()
            node = folder.transform(node)

            simplifier = AlgebraicSimplifier()
            node = simplifier.transform(node)

            if not folder.changed and not simplifier.changed:
                return node

    def _optimize_control_structures(self, node: ASTNode) -> ASTNode:
        return TailRecursionOptimizer().transform(node)

from dataclasses import dataclass
from enum import Enum, auto

from .asm_parser import AsmBlock
from .asm_parser import AsmDirective
from .asm_parser import AsmInstruction
from .ast import Assignment
from .ast import BinaryOp
from .ast import LogicalAnd
from .ast import LogicalOr
from .ast import Block
from .ast import Call
from .ast import Declaration
from .ast import Expression
from .ast import ExpressionStatement
from .ast import FunctionDefinition
from .ast import GlobalDeclaration
from .ast import Identifier
from .ast import IfStatement
from .ast import Number
from .ast import Program
from .ast import ReturnStatement
from .ast import Statement
from .ast import TailRecursiveCallStatement
from .ast import UnaryOp
from .ast import WhileStatement
from .ast import DoWhileStatement
from .ast import RepeatUntilStatement
from .diagnostics import DiagnosticReporter
from .errors import SemanticError
from .token import TokenKind
from .token import SourceSpan


class TypeKind(Enum):
    INT = auto()
    ERROR = auto()


class VarKind(Enum):
    GLOBAL = "global"
    LOCAL = "local"
    ARG = "arg"


@dataclass(frozen=True)
class Type:
    kind: TypeKind
    element_type: "Type | None" = None


INT_TYPE = Type(TypeKind.INT)
ERROR_TYPE = Type(TypeKind.ERROR)


@dataclass
class VarInfo:
    name: str
    kind: VarKind
    index: int
    type: Type


@dataclass
class ParameterInfo:
    name: str
    type: Type


@dataclass
class FunctionInfo:
    name: str
    params: list[ParameterInfo]
    return_type: Type
    address: int | None = None
    local_count: int = 0


@dataclass
class ProgramInfo:
    globals_map: dict[str, VarInfo]
    functions_map: dict[str, FunctionInfo]


class FunctionEnv:
    def __init__(self, function_info: FunctionInfo) -> None:
        self.function_info = function_info
        self.arg_map: dict[str, VarInfo] = {}

        for index, param in enumerate(function_info.params):
            self.arg_map[param.name] = VarInfo(
                name=param.name,
                kind=VarKind.ARG,
                index=index,
                type=param.type,
            )

        self.local_scopes: list[dict[str, VarInfo]] = []
        self.next_local_index = 0

    def enter_scope(self) -> None:
        self.local_scopes.append({})

    def exit_scope(self) -> None:
        if not self.local_scopes:
            raise SemanticError("no local scope to exit")
        self.local_scopes.pop()

    def lookup_current_scope(self, name: str) -> VarInfo | None:
        if not self.local_scopes:
            return None
        return self.local_scopes[-1].get(name)

    def add_local(self, name: str, var_type: Type) -> VarInfo:
        if not self.local_scopes:
            raise SemanticError("no local scope to add variable into")

        info = VarInfo(
            name=name,
            kind=VarKind.LOCAL,
            index=self.next_local_index,
            type=var_type,
        )
        self.next_local_index += 1
        self.local_scopes[-1][name] = info
        return info

    def lookup(self, name: str) -> VarInfo | None:
        for scope in reversed(self.local_scopes):
            if name in scope:
                return scope[name]
        return self.arg_map.get(name)


class SemanticAnalyzer:
    def __init__(self, reporter: DiagnosticReporter | None = None) -> None:
        self.reporter = reporter
        self.globals_map: dict[str, VarInfo] = {}
        self.functions_map: dict[str, FunctionInfo] = {}
        self.current_function: FunctionInfo | None = None
        self.current_env: FunctionEnv | None = None

    def report_error(self, span: SourceSpan, message: str) -> None:
        if self.reporter is None:
            raise SemanticError(message)
        self.reporter.error_at_span(message, span)

    def analyze(self, program: Program) -> ProgramInfo:
        self.collect_globals_and_functions(program)

        for item in program.items:
            if isinstance(item, GlobalDeclaration):
                self.analyze_global(item)
            elif isinstance(item, FunctionDefinition):
                self.analyze_function(item)
            else:
                raise SemanticError(f"unexpected top-level node: {type(item).__name__}")

        return ProgramInfo(
            globals_map=self.globals_map,
            functions_map=self.functions_map,
        )

    def collect_globals_and_functions(self, program: Program) -> None:
        for item in program.items:
            if isinstance(item, GlobalDeclaration):
                self.collect_global(item)
            elif isinstance(item, FunctionDefinition):
                self.collect_function(item)
            else:
                raise SemanticError(f"unexpected top-level node: {type(item).__name__}")

    def collect_global(self, node: GlobalDeclaration) -> None:
        if node.name in self.globals_map:
            self.report_error(
                node.name_span or node.span,
                f"duplicate global variable: {node.name}",
            )
            node.var_info = self.globals_map[node.name]
            return

        info = VarInfo(
            name=node.name,
            kind=VarKind.GLOBAL,
            index=len(self.globals_map),
            type=INT_TYPE,
        )
        self.globals_map[node.name] = info
        node.var_info = info

    def collect_function(self, node: FunctionDefinition) -> None:
        if node.name in self.functions_map:
            self.report_error(
                node.name_span or node.span, f"duplicate function: {node.name}"
            )
            node.function_info = self.functions_map[node.name]
            return

        params: list[ParameterInfo] = []
        seen_params: set[str] = set()
        param_spans = node.param_spans or []
        for index, param_name in enumerate(node.params):
            param_span = param_spans[index] if index < len(param_spans) else node.span
            if param_name in seen_params:
                self.report_error(
                    param_span,
                    f"duplicate parameter in function {node.name}: {param_name}",
                )
                continue
            seen_params.add(param_name)
            params.append(ParameterInfo(name=param_name, type=INT_TYPE))

        info = FunctionInfo(
            name=node.name,
            params=params,
            return_type=INT_TYPE,
        )
        self.functions_map[node.name] = info
        node.function_info = info

    def analyze_global(self, node: GlobalDeclaration) -> None:
        initializer_type = self.infer_expression_type(node.initializer)
        if initializer_type not in (INT_TYPE, ERROR_TYPE):
            self.report_error(node.span, f"global initializer must be int: {node.name}")

    def analyze_function(self, node: FunctionDefinition) -> None:
        function_info = self.functions_map[node.name]
        self.current_function = function_info
        self.current_env = FunctionEnv(function_info)

        try:
            if isinstance(node.body, Block):
                self.analyze_block(node.body)
                function_info.local_count = self.current_env.next_local_index
            elif isinstance(node.body, AsmBlock):
                self.analyze_asm_block(node.body)
                function_info.local_count = 0
            else:
                raise SemanticError(
                    f"unsupported function body: {type(node.body).__name__}"
                )
        finally:
            self.current_function = None
            self.current_env = None

    def analyze_asm_block(self, block: AsmBlock) -> None:
        labels: set[str] = set()
        declared_functions: set[str] = set()
        for line in block.lines:
            if line.label is not None:
                if line.label in labels:
                    self.report_error(line.span, f"duplicate asm label: {line.label}")
                labels.add(line.label)
            if isinstance(line.item, AsmDirective):
                if line.item.name == ".globals":
                    self.report_error(
                        line.item.span,
                        ".globals is not allowed in function asm body",
                    )
                elif line.item.name == ".function":
                    name = line.item.operand
                    if name is None:
                        continue
                    if name in declared_functions:
                        self.report_error(
                            line.item.span,
                            f"duplicate .function directive: {name}",
                        )
                    declared_functions.add(name)
                    if name not in self.functions_map:
                        self.report_error(
                            line.item.span,
                            f"undefined function in .function directive: {name}",
                        )
            elif isinstance(line.item, AsmInstruction):
                if line.item.mnemonic == "CALL" and isinstance(line.item.operand, str):
                    target = line.item.operand
                    if target not in labels and target not in declared_functions:
                        self.report_error(
                            line.item.span,
                            "CALL target must be a local label or declared with .function: "
                            f"{target}",
                        )

    def analyze_block(self, block: Block) -> None:
        if self.current_env is None:
            raise SemanticError("block analyzed outside function")

        self.current_env.enter_scope()
        try:
            for item in block.items:
                if isinstance(item, Declaration):
                    self.analyze_declaration(item)
                elif isinstance(item, Statement):
                    self.analyze_statement(item)
                else:
                    raise SemanticError(f"unexpected block item: {type(item).__name__}")
        finally:
            self.current_env.exit_scope()

    def analyze_declaration(self, decl: Declaration) -> None:
        if self.current_env is None:
            raise SemanticError("declaration analyzed outside function")

        current = self.current_env.lookup_current_scope(decl.name)
        if current is not None:
            self.report_error(
                decl.name_span or decl.span,
                f"duplicate local variable in same scope: {decl.name}",
            )
            decl.var_info = current
        else:
            info = self.current_env.add_local(decl.name, INT_TYPE)
            decl.var_info = info

        initializer_type = self.infer_expression_type(decl.initializer)
        symbol_type = decl.var_info.type if decl.var_info is not None else INT_TYPE
        if initializer_type not in (symbol_type, ERROR_TYPE):
            self.report_error(
                decl.span,
                f"type mismatch in declaration of {decl.name}: "
                f"{symbol_type} vs {initializer_type}",
            )

    def analyze_statement(self, stmt: Statement) -> None:
        if isinstance(stmt, Block):
            self.analyze_block(stmt)
            return

        if isinstance(stmt, IfStatement):
            self.infer_condition_type(stmt.condition)
            self.analyze_statement(stmt.then_stmt)
            # TODO: EX2-3 Extending the Semantic Analyzer and Code Generator
            # Analyze the else statement only if it exists.
            assert stmt.else_stmt is not None
            self.analyze_statement(stmt.else_stmt)
            return

        if isinstance(stmt, WhileStatement):
            self.infer_condition_type(stmt.condition)
            self.analyze_statement(stmt.body)
            return

        if isinstance(stmt, DoWhileStatement):
            # TODO: EX2-3 Extending the Semantic Analyzer and Code Generator
            # Analyze the body and condition of the do-while statement.
            return

        if isinstance(stmt, RepeatUntilStatement):
            # TODO: EX2-3 Extending the Semantic Analyzer and Code Generator
            # Analyze the body and condition of the repeat-until statement.
            return

        if isinstance(stmt, ReturnStatement):
            if self.current_function is None:
                raise SemanticError("return outside function")

            if stmt.expr is None:
                return
            expr_type = self.infer_expression_type(stmt.expr)
            if expr_type not in (self.current_function.return_type, ERROR_TYPE):
                self.report_error(
                    stmt.span,
                    f"return type mismatch in {self.current_function.name}",
                )
            return

        if isinstance(stmt, ExpressionStatement):
            self.infer_expression_type(stmt.expr)
            return

        if isinstance(stmt, TailRecursiveCallStatement):
            for arg in stmt.args:
                self.infer_expression_type(arg)
            return

        raise SemanticError(f"unsupported statement: {type(stmt).__name__}")

    def infer_condition_type(self, expr: Expression) -> Type:
        return self.infer_expression_type(expr)

    def infer_expression_type(self, expr: Expression) -> Type:
        if isinstance(expr, Number):
            expr.type = INT_TYPE
            return INT_TYPE

        if isinstance(expr, Identifier):
            info = self.resolve_variable(expr.name, expr.span)
            if info is None:
                expr.type = ERROR_TYPE
                return ERROR_TYPE
            expr.var_info = info
            expr.type = info.type
            return info.type

        if isinstance(expr, UnaryOp):
            operand_type = self.infer_expression_type(expr.expr)
            if operand_type == ERROR_TYPE:
                expr.type = ERROR_TYPE
                return ERROR_TYPE
            if expr.op == TokenKind.MINUS and operand_type == INT_TYPE:
                expr.type = INT_TYPE
                return INT_TYPE

            # TODO: EX2-3 Extending the Semantic Analyzer and Code Generator
            # Analyze the logical NOT operator.

            self.report_error(expr.span, f"unsupported unary operator/type: {expr.op}")
            expr.type = ERROR_TYPE
            return ERROR_TYPE

        if isinstance(expr, BinaryOp):
            left_type = self.infer_expression_type(expr.left)
            right_type = self.infer_expression_type(expr.right)
            if ERROR_TYPE in (left_type, right_type):
                expr.type = ERROR_TYPE
                return ERROR_TYPE
            if left_type != INT_TYPE or right_type != INT_TYPE:
                self.report_error(
                    expr.span,
                    "binary operator currently requires int operands",
                )
                expr.type = ERROR_TYPE
                return ERROR_TYPE
            expr.type = INT_TYPE
            return INT_TYPE

        if isinstance(expr, LogicalAnd) or isinstance(expr, LogicalOr):
            expr.type = INT_TYPE

            # TODO: EX2-3 Extending the Semantic Analyzer and Code Generator
            # Analyze all operands and propagate any semantic error.

            return expr.type

        if isinstance(expr, Assignment):
            if not isinstance(expr.left, Identifier):
                self.report_error(
                    expr.left.span,
                    "left-hand side of assignment must be identifier",
                )
                self.infer_expression_type(expr.right)
                expr.type = ERROR_TYPE
                return ERROR_TYPE

            var_info = self.resolve_variable(expr.left.name, expr.left.span)
            if var_info is None:
                # if var_info is None, resolve_variable already reports an error, so we just need to infer the right-hand side type to avoid cascading errors
                self.infer_expression_type(expr.right)
                expr.type = ERROR_TYPE
                return ERROR_TYPE

            left_type = self.infer_expression_type(expr.left)
            right_type = self.infer_expression_type(expr.right)
            if ERROR_TYPE in (left_type, right_type):
                expr.type = ERROR_TYPE
                return ERROR_TYPE
            if left_type != right_type:
                self.report_error(expr.span, "assignment type mismatch")
                expr.type = ERROR_TYPE
                return ERROR_TYPE
            expr.type = left_type
            return left_type

        if isinstance(expr, Call):
            function_info = self.functions_map.get(expr.func_name)
            if function_info is None:
                self.report_error(
                    expr.func_name_span or expr.span,
                    f"undefined function: {expr.func_name}",
                )
                for arg in expr.args:
                    self.infer_expression_type(arg)
                expr.type = ERROR_TYPE
                return ERROR_TYPE

            expr.function_info = function_info

            if len(expr.args) != len(function_info.params):
                self.report_error(
                    expr.func_name_span or expr.span,
                    f"wrong number of arguments for {expr.func_name}: "
                    f"expected {len(function_info.params)}, got {len(expr.args)}",
                )

            for arg_expr, param_info in zip(expr.args, function_info.params):
                arg_type = self.infer_expression_type(arg_expr)
                if arg_type in (param_info.type, ERROR_TYPE):
                    continue
                self.report_error(
                    arg_expr.span,
                    f"argument type mismatch for {expr.func_name}({param_info.name})",
                )

            expr.type = function_info.return_type
            return function_info.return_type

        raise SemanticError(f"cannot infer expression type: {type(expr).__name__}")

    def resolve_variable(self, name: str, span: SourceSpan) -> VarInfo | None:
        if self.current_env is not None:
            info = self.current_env.lookup(name)
            if info is not None:
                return info

        if name in self.globals_map:
            return self.globals_map[name]

        self.report_error(span, f"undefined variable: {name}")
        return None

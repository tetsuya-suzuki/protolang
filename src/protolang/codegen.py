from .asm_parser import AsmBlock
from .assembler import assemble_block
from .ast import Assignment
from .ast import BinaryOp
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
from .ast import TailRecursiveCallStatement
from .ast import Statement
from .ast import UnaryOp
from .ast import WhileStatement
from .ast import DoWhileStatement
from .ast import RepeatUntilStatement
from .ast import LogicalAnd
from .ast import LogicalOr
from .diagnostics import DiagnosticReporter
from .errors import CodeGenError
from .instruction import Instruction
from .instruction import OpCode
from .semantic import FunctionInfo
from .semantic import ProgramInfo
from .semantic import VarInfo
from .semantic import VarKind
from .token import SourceSpan
from .token import TokenKind


class CodeGenerator:
    def __init__(
        self,
        program_info: ProgramInfo,
        reporter: DiagnosticReporter | None = None,
    ) -> None:
        self.program_info = program_info
        self.reporter = reporter
        self.instructions: list[Instruction] = []
        self.unresolved_calls: list[tuple[int, FunctionInfo]] = []
        self.current_function: FunctionInfo | None = None
        self.current_function_start: int | None = None
        self.current_node_span: SourceSpan | None = None
        self.failed = False

    def report_error(self, span: SourceSpan | None, message: str) -> None:
        self.failed = True
        if self.reporter is None:
            raise CodeGenError(message)
        if span is None:
            span = self.current_node_span
        if span is None:
            span = self.reporter.make_span(1, 1)
        self.reporter.error_at_span(message, span)

    @property
    def globals_map(self) -> dict[str, VarInfo]:
        return self.program_info.globals_map

    @property
    def functions_map(self) -> dict[str, FunctionInfo]:
        return self.program_info.functions_map

    def emit(self, op: OpCode, arg: int | None = None) -> int:
        index = len(self.instructions)
        self.instructions.append(Instruction(op, arg))
        return index

    def patch(self, index: int, arg: int) -> None:
        old_inst = self.instructions[index]
        self.instructions[index] = Instruction(old_inst.op, arg)

    def current_address(self) -> int:
        return len(self.instructions)

    def generate(self, program: Program) -> tuple[list[Instruction] | None, int | None]:
        for item in program.items:
            if isinstance(item, GlobalDeclaration):
                self.emit_expression(item.initializer)
                if self.failed:
                    return None, None
                if item.var_info is None:
                    self.report_error(
                        item.span, f"missing symbol for global: {item.name}"
                    )
                    return None, None
                self.emit_store_by_info(item.var_info)
                if self.failed:
                    return None, None

        main_info = self.functions_map.get("main")
        if main_info is None:
            self.report_error(program.span, "undefined function: main")
            return None, None

        main_call_pos = self.emit(OpCode.CALL, 0)
        self.emit(OpCode.CLEAN, len(main_info.params))
        self.emit(OpCode.HALT)

        for item in program.items:
            if isinstance(item, FunctionDefinition):
                self.emit_function(item)

        self.unresolved_calls.append((main_call_pos, main_info))
        self.patch_unresolved_calls()

        if self.failed:
            return None, None
        return self.instructions, len(self.globals_map)

    def patch_unresolved_calls(self) -> None:
        for index, function_info in self.unresolved_calls:
            if function_info.address is None:
                self.report_error(
                    None, f"undefined function address: {function_info.name}"
                )
                continue
            self.patch(index, function_info.address)

    def emit_function(self, node: FunctionDefinition) -> None:
        self.current_node_span = node.span
        function_info = node.function_info
        if function_info is None:
            self.report_error(node.span, f"missing function info: {node.name}")
            return
        if function_info.address is not None:
            self.report_error(
                node.name_span or node.span,
                f"duplicate function address entry: {function_info.name}",
            )
            return

        function_info.address = self.current_address()
        self.current_function = function_info

        if isinstance(node.body, Block):
            self.emit(OpCode.ALLOC, function_info.local_count)
            self.current_function_start = self.current_address()
            self.emit(OpCode.IPUSH, 0)  # default return value
            self.emit_block(node.body)
        elif isinstance(node.body, AsmBlock):
            self.emit_asm_block(node.body)
        else:
            self.report_error(
                node.span, f"unsupported function body: {type(node.body).__name__}"
            )
        self.current_function = None
        self.current_function_start = None

    def emit_asm_block(self, block: AsmBlock) -> None:
        result = assemble_block(block, reporter=self.reporter)
        base = len(self.instructions)
        for inst in result.code:
            arg = inst.arg
            if inst.op in {OpCode.JMP, OpCode.JPZ, OpCode.CALL} and isinstance(
                arg, int
            ):
                arg = base + arg
            self.instructions.append(
                Instruction(inst.op, arg)
                if inst.op.arity == 1
                else Instruction(inst.op)
            )
        for offset, name in result.unresolved_calls:
            function_info = self.functions_map.get(name)
            if function_info is None:
                self.report_error(
                    result.unresolved_call_spans.get(offset, block.span),
                    f"undefined function address: {name}",
                )
                continue
            self.unresolved_calls.append((base + offset, function_info))

    def emit_block(self, block: Block) -> None:
        for item in block.items:
            if isinstance(item, Declaration):
                self.emit_declaration(item)
            elif isinstance(item, Statement):
                self.emit_statement(item)
            else:
                self.report_error(
                    block.span, f"unexpected block item: {type(item).__name__}"
                )

    def emit_declaration(self, decl: Declaration) -> None:
        self.current_node_span = decl.span
        self.emit_expression(decl.initializer)
        if decl.var_info is None:
            self.report_error(decl.span, f"missing symbol for declaration: {decl.name}")
            return
        self.emit_store_by_info(decl.var_info)

    def emit_statement(self, stmt: Statement) -> None:
        self.current_node_span = stmt.span
        if isinstance(stmt, Block):
            self.emit_block(stmt)
            return

        if isinstance(stmt, IfStatement):
            self.emit_if_statement(stmt)
            return

        if isinstance(stmt, WhileStatement):
            self.emit_while_statement(stmt)
            return

        if isinstance(stmt, DoWhileStatement):
            self.emit_do_while_statement(stmt)
            return

        if isinstance(stmt, RepeatUntilStatement):
            self.emit_repeat_until_statement(stmt)
            return

        if isinstance(stmt, ReturnStatement):
            self.emit_return_statement(stmt)
            return

        if isinstance(stmt, TailRecursiveCallStatement):
            self.emit_tail_recursive_call(stmt)
            return

        if isinstance(stmt, ExpressionStatement):
            self.emit(OpCode.POP)  # discard the latest expression value
            self.emit_expression(stmt.expr)
            return

        self.report_error(stmt.span, f"unsupported statement: {type(stmt).__name__}")

    def emit_if_statement(self, stmt: IfStatement) -> None:
        self.emit_expression(stmt.condition)

        jump_if_zero_pos = self.emit(OpCode.JPZ, 0)
        self.emit_statement(stmt.then_stmt)

        if stmt.else_stmt is None:
            # TODO: EX2-3 Extending the Semantic Analyzer and Code Generator
            # Complete code generation for an if statement without an else statement.
            return

        # This JMP is unreachable for a normalized tail if-statement with an else branch,
        # but it is emitted unconditionally to keep code generation simple.
        jump_end_pos = self.emit(OpCode.JMP, 0)

        else_addr = self.current_address()
        self.patch(jump_if_zero_pos, else_addr)

        self.emit_statement(stmt.else_stmt)
        end_addr = self.current_address()
        self.patch(jump_end_pos, end_addr)

    def emit_while_statement(self, stmt: WhileStatement) -> None:
        begin_addr = self.current_address()
        self.emit_expression(stmt.condition)

        jump_if_zero_pos = self.emit(OpCode.JPZ, 0)
        self.emit_statement(stmt.body)
        self.emit(OpCode.JMP, begin_addr)

        end_addr = self.current_address()
        self.patch(jump_if_zero_pos, end_addr)

    def emit_do_while_statement(self, stmt: DoWhileStatement) -> None:
        begin_addr = self.current_address()
        self.emit_statement(stmt.body)
        self.emit_expression(stmt.condition)

        jump_if_not_zero_pos = self.emit(OpCode.JPZ, 0)
        self.emit(OpCode.JMP, begin_addr)

        end_addr = self.current_address()
        self.patch(jump_if_not_zero_pos, end_addr)

    def emit_repeat_until_statement(self, stmt: RepeatUntilStatement) -> None:
        begin_addr = self.current_address()
        self.emit_statement(stmt.body)
        self.emit_expression(stmt.condition)
        self.emit(OpCode.JPZ, begin_addr)

    def emit_return_statement(self, stmt: ReturnStatement) -> None:
        if self.current_function is None:
            self.report_error(stmt.span, "return outside function")
            return

        if stmt.expr is not None:
            self.emit(OpCode.POP)  # discard the latest expression value
            self.emit_expression(stmt.expr)
        self.emit(OpCode.RET)

    def emit_tail_recursive_call(self, stmt: TailRecursiveCallStatement) -> None:
        if self.current_function is None or self.current_function_start is None:
            self.report_error(stmt.span, "tail-recursive call outside function")
            return
        # TODO: EX2-5 Extending the Optimizer (2)
        # Emit code for the tail-recursive call according to the specification.

    def emit_expression(self, expr: Expression) -> None:
        self.current_node_span = expr.span
        if isinstance(expr, Number):
            self.emit(OpCode.IPUSH, expr.value)
            return

        if isinstance(expr, Identifier):
            if expr.var_info is None:
                self.report_error(
                    expr.span, f"missing symbol for identifier: {expr.name}"
                )
                return
            self.emit_load_by_info(expr.var_info)
            return

        if isinstance(expr, UnaryOp):
            self.emit_expression(expr.expr)
            if expr.op == TokenKind.MINUS:
                self.emit(OpCode.INEG)
                return

            # TODO: EX2-3 Extending the Semantic Analyzer and Code Generator
            # Emit code for the logical NOT operation according to the specification.

            self.report_error(expr.span, f"unsupported unary op: {expr.op}")
            return

        if isinstance(expr, BinaryOp):
            self.emit_expression(expr.left)
            self.emit_expression(expr.right)
            self.emit_binary_op(expr.op)
            return

        if isinstance(expr, Assignment):
            self.emit_assignment_expression(expr)
            return

        if isinstance(expr, LogicalAnd):
            self.emit_logical_and_expression(expr)
            return

        if isinstance(expr, LogicalOr):
            self.emit_logical_or_expression(expr)
            return

        if isinstance(expr, Call):
            self.emit_call_expression(expr)
            return

        self.report_error(expr.span, f"unsupported expression: {type(expr).__name__}")

    def emit_binary_op(self, op: TokenKind) -> None:
        op_map = {
            TokenKind.PLUS: OpCode.IADD,
            TokenKind.MINUS: OpCode.ISUB,
            TokenKind.STAR: OpCode.IMUL,
            TokenKind.SLASH: OpCode.IDIV,
            TokenKind.EQ: OpCode.IEQ,
            TokenKind.NE: OpCode.INE,
            TokenKind.LT: OpCode.ILT,
            TokenKind.LE: OpCode.ILE,
            TokenKind.GT: OpCode.IGT,
            TokenKind.GE: OpCode.IGE,
            # TODO: EX2-3 Extending the Semantic Analyzer and Code Generator
            # Add the modulo operator according to the specification.
        }
        opcode = op_map.get(op)
        if opcode is None:
            self.report_error(None, f"unsupported binary op: {op}")
            return
        self.emit(opcode)

    def emit_assignment_expression(self, expr: Assignment) -> None:
        if not isinstance(expr.left, Identifier):
            self.report_error(
                expr.left.span, "left-hand side of assignment must be identifier"
            )
            return

        self.emit_expression(expr.right)
        self.emit(OpCode.DUP)
        if expr.left.var_info is None:
            self.report_error(
                expr.left.span, f"missing symbol for identifier: {expr.left.name}"
            )
            return
        self.emit_store_by_info(expr.left.var_info)

    def emit_logical_and_expression(self, expr: LogicalAnd) -> None:
        if expr.operands == []:
            self.emit(OpCode.IPUSH, 1)  # empty AND is true
            return

        # TODO: EX2-3 Extending the Semantic Analyzer and Code Generator
        # Emit code for the logical AND expression according to the specification.

    def emit_logical_or_expression(self, expr: LogicalOr) -> None:
        if expr.operands == []:
            self.emit(OpCode.IPUSH, 0)  # empty OR is false
            return

        # TODO: EX2-3 Extending the Semantic Analyzer and Code Generator
        # Emit code for the logical OR expression according to the specification.

    def emit_call_expression(self, expr: Call) -> None:
        for arg in reversed(expr.args):
            self.emit_expression(arg)

        function_info = expr.function_info
        if function_info is None:
            self.report_error(expr.span, f"missing function info: {expr.func_name}")
            return
        call_pos = self.emit(OpCode.CALL, 0)
        self.unresolved_calls.append((call_pos, function_info))
        self.emit(OpCode.CLEAN, len(expr.args))

    def emit_load_by_info(self, info: VarInfo) -> None:
        if info.kind == VarKind.GLOBAL:
            self.emit(OpCode.LOADG, info.index)
            return

        if info.kind == VarKind.ARG:
            self.emit(OpCode.LOADA, info.index)
            return

        if info.kind == VarKind.LOCAL:
            self.emit(OpCode.LOADL, info.index)
            return

        self.report_error(
            self.current_node_span, f"invalid variable kind: {info.kind.value}"
        )

    def emit_store_by_info(self, info: VarInfo) -> None:
        if info.kind == VarKind.GLOBAL:
            self.emit(OpCode.STOREG, info.index)
            return

        if info.kind == VarKind.ARG:
            self.emit(OpCode.STOREA, info.index)
            return

        if info.kind == VarKind.LOCAL:
            self.emit(OpCode.STOREL, info.index)
            return

        self.report_error(
            self.current_node_span, f"invalid variable kind: {info.kind.value}"
        )

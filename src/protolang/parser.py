from .asm_parser import AsmBlock
from .asm_parser import parse_asm_source
from .ast import ASTNode
from .ast import Assignment
from .ast import BinaryOp
from .ast import Statement
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
from .ast import UnaryOp
from .ast import WhileStatement
from .ast import DoWhileStatement
from .ast import RepeatUntilStatement
from .ast import LogicalAnd
from .ast import LogicalOr
from .diagnostics import DiagnosticReporter
from .token import SourceSpan
from .token import Token
from .token import TokenKind
from .lexer import Lexer


class Parser:
    def __init__(
        self, lexer: Lexer, reporter: DiagnosticReporter | None = None
    ) -> None:
        self.lexer = lexer
        self.reporter = (
            reporter if reporter is not None else getattr(lexer, "reporter", None)
        )
        self.next_token = self.lexer.get_next_token()

    def update_next_token(self) -> None:
        self.next_token = self.lexer.get_next_token()

    def current_span(self) -> SourceSpan | None:
        return self.next_token.span

    def report_error(self, message: str) -> None:
        span = self.current_span()
        if self.reporter is not None and span is not None:
            self.reporter.error_at_span(message, span)

    def expect(self, kind: TokenKind) -> Token | None:
        if self.next_token.kind != kind:
            self.report_error(f"expected {kind.name}, got {self.next_token.kind.name}")
            return None

        token = self.next_token
        self.update_next_token()
        return token

    def match(self, kind: TokenKind) -> Token | None:
        if self.next_token.kind == kind:
            token = self.next_token
            self.update_next_token()
            return token
        return None

    @staticmethod
    def token_span(token: Token) -> SourceSpan:
        if token.span is None:
            raise ValueError("token has no source span")
        return token.span

    @staticmethod
    def token_text(token: Token) -> str:
        if not isinstance(token.value, str):
            raise ValueError("token value is not text")
        return token.value

    @staticmethod
    def token_int(token: Token) -> int:
        if not isinstance(token.value, int):
            raise ValueError("token value is not an integer")
        return token.value

    def synchronize(self, stop_kinds: set[TokenKind]) -> None:
        while (
            self.next_token.kind not in stop_kinds
            and self.next_token.kind != TokenKind.EOF
        ):
            self.update_next_token()

    def skip_past(self, kind: TokenKind) -> None:
        if self.next_token.kind == kind:
            self.update_next_token()

    def parse_program(self) -> Program:
        items: list[ASTNode] = []
        start_span = self.token_span(self.next_token)

        while self.next_token.kind != TokenKind.EOF:
            if self.next_token.kind == TokenKind.VAR:
                global_decl = self.parse_global_declaration()
                if global_decl is not None:
                    items.append(global_decl)
                else:
                    self.synchronize(
                        {
                            TokenKind.SEMICOLON,
                            TokenKind.FUNCTION,
                            TokenKind.VAR,
                            TokenKind.EOF,
                        }
                    )
                    self.skip_past(TokenKind.SEMICOLON)
            elif self.next_token.kind == TokenKind.FUNCTION:
                function_def = self.parse_function_definition()
                if function_def is not None:
                    items.append(function_def)
                else:
                    self.synchronize({TokenKind.FUNCTION, TokenKind.VAR, TokenKind.EOF})
            else:
                self.report_error(
                    "expected global declaration or function definition, "
                    f"got {self.next_token.kind.name}"
                )
                self.update_next_token()

        eof_span = self.token_span(self.next_token)
        if items:
            span = SourceSpan.combine(items[0].span, items[-1].span)
        else:
            span = start_span
        return Program(span, items)

    def parse_global_declaration(self) -> GlobalDeclaration | None:
        var_token = self.expect(TokenKind.VAR)
        name_token = self.expect(TokenKind.IDENT)
        self.expect(TokenKind.ASSIGN)
        initializer = self.parse_expression()
        semicolon_token = self.expect(TokenKind.SEMICOLON)

        if (
            var_token is None
            or name_token is None
            or initializer is None
            or semicolon_token is None
        ):
            return None

        span = SourceSpan.combine(
            self.token_span(var_token), self.token_span(semicolon_token)
        )
        return GlobalDeclaration(
            span,
            self.token_text(name_token),
            initializer,
            name_span=self.token_span(name_token),
        )

    def parse_function_definition(self) -> FunctionDefinition | None:
        function_token = self.expect(TokenKind.FUNCTION)
        name_token = self.expect(TokenKind.IDENT)
        self.expect(TokenKind.LPAREN)

        params: list[str] = []
        param_spans: list[SourceSpan] = []
        if self.next_token.kind != TokenKind.RPAREN:
            result = self.parse_parameter_list()
            if result is None:
                return None
            params, param_spans = result

        if self.expect(TokenKind.RPAREN) is None:
            return None
        if self.next_token.kind == TokenKind.ASM:
            body: Block | AsmBlock | None = self.parse_asm_block()
        else:
            body = self.parse_block()

        if function_token is None or name_token is None or body is None:
            return None
        span = SourceSpan.combine(self.token_span(function_token), body.span)

        return FunctionDefinition(
            span,
            self.token_text(name_token),
            params,
            body,
            name_span=self.token_span(name_token),
            param_spans=param_spans,
        )

    def parse_asm_block(self) -> AsmBlock | None:
        if self.expect(TokenKind.ASM) is None:
            return None
        if self.next_token.kind != TokenKind.LBRACE:
            self.report_error(f"expected LBRACE, got {self.next_token.kind.name}")
            return None
        lbrace_token = self.next_token
        asm_source, _rbrace_span = self.lexer.capture_until_matching_rbrace()
        self.next_token = self.lexer.get_next_token()
        return parse_asm_source(
            asm_source,
            line_offset=self.token_span(lbrace_token).end.line - 1,
            col_offset=self.token_span(lbrace_token).end.column - 1,
            reporter=self.reporter,
        )

    def parse_parameter_list(self) -> tuple[list[str], list[SourceSpan]] | None:
        first = self.expect(TokenKind.IDENT)
        if first is None:
            return None

        params: list[str] = [self.token_text(first)]
        param_spans: list[SourceSpan] = [self.token_span(first)]

        while self.match(TokenKind.COMMA):
            ident = self.expect(TokenKind.IDENT)
            if ident is None:
                return None
            params.append(self.token_text(ident))
            param_spans.append(self.token_span(ident))

        return params, param_spans

    def parse_block(self) -> Block | None:
        lbrace_token = self.expect(TokenKind.LBRACE)
        if lbrace_token is None:
            return None

        items: list[Declaration | Statement] = []

        while self.next_token.kind != TokenKind.RBRACE:
            if self.next_token.kind == TokenKind.EOF:
                self.report_error("expected RBRACE, got EOF")
                return None

            if self.next_token.kind == TokenKind.VAR:
                declaration = self.parse_declaration()
                if declaration is not None:
                    items.append(declaration)
                else:
                    self.synchronize(
                        {TokenKind.SEMICOLON, TokenKind.RBRACE, TokenKind.EOF}
                    )
                    self.skip_past(TokenKind.SEMICOLON)
            else:
                statement = self.parse_statement()
                if statement is not None:
                    items.append(statement)
                else:
                    self.synchronize(
                        {TokenKind.SEMICOLON, TokenKind.RBRACE, TokenKind.EOF}
                    )
                    self.skip_past(TokenKind.SEMICOLON)

        rbrace_token = self.expect(TokenKind.RBRACE)
        if rbrace_token is None:
            return None
        span = SourceSpan.combine(
            self.token_span(lbrace_token), self.token_span(rbrace_token)
        )
        return Block(span, items)

    def parse_declaration(self) -> Declaration | None:
        var_token = self.expect(TokenKind.VAR)
        name_token = self.expect(TokenKind.IDENT)
        self.expect(TokenKind.ASSIGN)
        initializer = self.parse_expression()
        semicolon_token = self.expect(TokenKind.SEMICOLON)
        if (
            var_token is None
            or name_token is None
            or initializer is None
            or semicolon_token is None
        ):
            return None
        span = SourceSpan.combine(
            self.token_span(var_token), self.token_span(semicolon_token)
        )

        return Declaration(
            span,
            self.token_text(name_token),
            initializer,
            name_span=self.token_span(name_token),
        )

    def parse_statement(self) -> Statement | None:
        if self.next_token.kind == TokenKind.LBRACE:
            return self.parse_block()

        if self.next_token.kind == TokenKind.IF:
            return self.parse_if_statement()

        if self.next_token.kind == TokenKind.WHILE:
            return self.parse_while_statement()

        if self.next_token.kind == TokenKind.DO:
            return self.parse_do_while_statement()

        if self.next_token.kind == TokenKind.REPEAT:
            return self.parse_repeat_until_statement()

        if self.next_token.kind == TokenKind.RETURN:
            return self.parse_return_statement()

        return self.parse_expression_statement()

    def parse_if_statement(self) -> IfStatement | None:
        if_token = self.expect(TokenKind.IF)
        self.expect(TokenKind.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenKind.RPAREN)
        then_block = self.parse_block()

        # TODO: EX2-2 Extending the Parser (1)
        # Handle the optional ELSE part, which may be a block or another if statement.
        self.expect(TokenKind.ELSE)

        else_part: Statement | None = None
        if self.next_token.kind == TokenKind.LBRACE:
            else_part = self.parse_block()
        elif self.next_token.kind == TokenKind.IF:
            else_part = self.parse_if_statement()
        else:
            self.report_error(
                f"expected IF or LBRACE after ELSE, got {self.next_token.kind.name}"
            )
            return None

        if (
            if_token is None
            or condition is None
            or then_block is None
            or else_part is None
        ):
            return None
        span = SourceSpan.combine(self.token_span(if_token), else_part.span)
        return IfStatement(span, condition, then_block, else_part)

    def parse_while_statement(self) -> WhileStatement | None:
        while_token = self.expect(TokenKind.WHILE)
        self.expect(TokenKind.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenKind.RPAREN)
        body = self.parse_block()
        if while_token is None or condition is None or body is None:
            return None
        span = SourceSpan.combine(self.token_span(while_token), body.span)
        return WhileStatement(span, condition, body)

    def parse_do_while_statement(self) -> DoWhileStatement | None:
        # TODO: EX2-2 Extending the Parser (1)
        # Parse a do-while statement according to the specification.
        return None

    def parse_repeat_until_statement(self) -> RepeatUntilStatement | None:
        # TODO: EX2-2 Extending the Parser (1)
        # Parse a repeat-until statement according to the specification.
        return None

    def parse_return_statement(self) -> ReturnStatement | None:
        return_token = self.expect(TokenKind.RETURN)
        expr = self.parse_expression()
        semicolon_token = self.expect(TokenKind.SEMICOLON)
        if return_token is None or expr is None or semicolon_token is None:
            return None
        span = SourceSpan.combine(self.token_span(return_token), expr.span)
        return ReturnStatement(span, expr)

    def parse_expression_statement(self) -> ExpressionStatement | None:
        expr = self.parse_expression()
        semicolon_token = self.expect(TokenKind.SEMICOLON)
        if expr is None or semicolon_token is None:
            return None
        span = SourceSpan.combine(expr.span, self.token_span(semicolon_token))
        return ExpressionStatement(span, expr)

    def parse_expression(self) -> Expression | None:
        return self.parse_assignment()

    def parse_assignment(self) -> Expression | None:
        # TODO: EX2-2 Extending the Parser (1)
        # Parse an assignment expression according to the specification
        # to accept logical OR expressions on the left-hand side.
        left = self.parse_equality()
        if left is None:
            return None
        if self.match(TokenKind.ASSIGN):
            right = self.parse_assignment()
            if right is None:
                return None
            return Assignment(SourceSpan.combine(left.span, right.span), left, right)
        return left

    def parse_logical_or(self) -> Expression | None:
        # TODO: EX2-2 Extending the Parser (1)
        # Parse a logical OR expression according to the specification.
        return None

    def parse_logical_and(self) -> Expression | None:
        # TODO: EX2-2 Extending the Parser (1)
        # Parse a logical AND expression according to the specification.
        return None

    def parse_equality(self) -> Expression | None:
        node = self.parse_relational()
        if node is None:
            return None
        while self.next_token.kind in (TokenKind.EQ, TokenKind.NE):
            op = self.next_token.kind
            self.update_next_token()
            right = self.parse_relational()
            if right is None:
                return None
            node = BinaryOp(SourceSpan.combine(node.span, right.span), op, node, right)
        return node

    def parse_relational(self) -> Expression | None:
        node = self.parse_additive()
        if node is None:
            return None
        while self.next_token.kind in (
            TokenKind.LT,
            TokenKind.LE,
            TokenKind.GT,
            TokenKind.GE,
        ):
            op = self.next_token.kind
            self.update_next_token()
            right = self.parse_additive()
            if right is None:
                return None
            node = BinaryOp(SourceSpan.combine(node.span, right.span), op, node, right)
        return node

    def parse_additive(self) -> Expression | None:
        node = self.parse_term()
        if node is None:
            return None

        while self.next_token.kind in (TokenKind.PLUS, TokenKind.MINUS):
            op = self.next_token.kind
            self.update_next_token()
            right = self.parse_term()
            if right is None:
                return None
            node = BinaryOp(SourceSpan.combine(node.span, right.span), op, node, right)

        return node

    def parse_term(self) -> Expression | None:
        node = self.parse_unary()
        if node is None:
            return None

        # TODO: EX2-2 Extending the Parser (1)
        # Add parsing for modulus operator (%) at the term level of the expression grammar.
        while self.next_token.kind in (TokenKind.STAR, TokenKind.SLASH):
            op = self.next_token.kind
            self.update_next_token()
            right = self.parse_unary()
            if right is None:
                return None
            node = BinaryOp(SourceSpan.combine(node.span, right.span), op, node, right)

        return node

    def parse_unary(self) -> Expression | None:
        # TODO: EX2-2 Extending the Parser (1)
        # Add parsing for logical NOT (!) operators at the unary level of the expression grammar.
        if self.next_token.kind == TokenKind.MINUS:
            op_token = self.next_token
            self.update_next_token()
            operand = self.parse_unary()
            if operand is None:
                return None
            return UnaryOp(
                SourceSpan.combine(self.token_span(op_token), operand.span),
                op_token.kind,
                operand,
            )
        return self.parse_primary()

    def parse_primary(self) -> Expression | None:
        if self.next_token.kind == TokenKind.NUMBER:
            token = self.next_token
            self.update_next_token()
            return Number(self.token_span(token), self.token_int(token))

        if self.next_token.kind == TokenKind.IDENT:
            name_token = self.next_token
            self.update_next_token()

            if self.match(TokenKind.LPAREN):
                args: list[Expression] = []
                if self.next_token.kind != TokenKind.RPAREN:
                    parsed_args = self.parse_argument_list()
                    if parsed_args is None:
                        return None
                    args = parsed_args

                rparen_token = self.expect(TokenKind.RPAREN)
                if rparen_token is None:
                    return None
                span = SourceSpan.combine(
                    self.token_span(name_token), self.token_span(rparen_token)
                )
                return Call(
                    span,
                    self.token_text(name_token),
                    args,
                    func_name_span=self.token_span(name_token),
                )

            return Identifier(self.token_span(name_token), self.token_text(name_token))

        lparen_token = self.match(TokenKind.LPAREN)
        if lparen_token is not None:
            expr = self.parse_expression()
            rparen_token = self.expect(TokenKind.RPAREN)
            if expr is None or rparen_token is None:
                return None
            expr.span = SourceSpan.combine(
                self.token_span(lparen_token), self.token_span(rparen_token)
            )
            return expr

        self.report_error(f"unexpected token in primary: {self.next_token.kind.name}")
        return None

    def parse_argument_list(self) -> list[Expression] | None:
        first = self.parse_expression()
        if first is None:
            return None
        args = [first]

        while self.match(TokenKind.COMMA):
            expr = self.parse_expression()
            if expr is None:
                return None
            args.append(expr)

        return args

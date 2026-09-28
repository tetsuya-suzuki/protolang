class ProtoLangError(Exception):
    def __init__(
        self,
        message: str,
        line: int | None = None,
        column: int | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column


class LexerError(ProtoLangError):
    pass


class ParserError(ProtoLangError):
    pass


class SemanticError(ProtoLangError):
    pass


class CodeGenError(ProtoLangError):
    pass


class VMError(ProtoLangError):
    pass


class AssemblerError(ProtoLangError):
    pass

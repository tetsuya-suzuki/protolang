import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from .assembler import assemble_source
from .assembly_formatter import AssemblyFormatter
from .ast import Program
from .ast_printer import format_ast_as_mermaid
from .codegen import CodeGenerator
from .diagnostics import DiagnosticReporter
from .lexer import Lexer
from .normalizer import ASTNormalizer
from .optimizer import Optimizer
from .parser import Parser
from .semantic import ProgramInfo
from .semantic import SemanticAnalyzer
from .token import Token
from .token import TokenKind
from .vm import Instruction
from .vm import VirtualMachine


@dataclass
class CompilationResult:
    ast: Program | None
    code: list[Instruction] | None
    global_count: int | None
    program_info: ProgramInfo | None
    reporter: DiagnosticReporter


def parse_source(
    source: str,
    filename: str | None = None,
) -> tuple[Program, DiagnosticReporter]:
    """Parse a ProtoLang program and return the AST produced by the parser."""
    reporter = DiagnosticReporter(source, filename=filename)
    lexer = Lexer(source, reporter=reporter)
    parser = Parser(lexer, reporter=reporter)
    ast = parser.parse_program()
    return ast, reporter


def build_ast(
    source: str,
    filename: str | None = None,
    optimization_level: int = 0,
) -> tuple[Program, ProgramInfo | None, DiagnosticReporter]:
    """Parse, normalize, analyze, and optionally optimize a ProtoLang program.

    AST normalization makes implicit returns explicit before semantic analysis.
    Semantic analysis is performed before optimization so that an optimization
    cannot hide an error in the original source program.  -O1 only performs
    local expression transformations, so its result does not need another
    semantic-analysis pass.  -O2 may transform control structures and introduce
    or remove declarations, so semantic analysis is performed again afterward.
    """
    ast, reporter = parse_source(source, filename=filename)
    if reporter.has_errors():
        return ast, None, reporter

    ast = ASTNormalizer().normalize(ast)

    analyzer = SemanticAnalyzer(reporter)
    program_info = analyzer.analyze(ast)
    if reporter.has_errors():
        return ast, program_info, reporter

    optimized_ast = Optimizer(level=optimization_level).optimize(ast)

    if not isinstance(optimized_ast, Program):
        raise ValueError("Expected Program node after optimization")

    ast = optimized_ast

    if optimization_level >= 2:
        analyzer = SemanticAnalyzer(reporter)
        program_info = analyzer.analyze(ast)
        if reporter.has_errors():
            return ast, program_info, reporter

    return ast, program_info, reporter


def compile_source(
    source: str,
    filename: str | None = None,
    optimization_level: int = 0,
) -> CompilationResult:
    ast, program_info, reporter = build_ast(
        source,
        filename=filename,
        optimization_level=optimization_level,
    )
    if ast is None or program_info is None or reporter.has_errors():
        return CompilationResult(ast, None, None, program_info, reporter)

    generator = CodeGenerator(program_info, reporter=reporter)
    code, global_count = generator.generate(ast)
    return CompilationResult(ast, code, global_count, program_info, reporter)


def run_source(
    source: str,
    filename: str | None = None,
    optimization_level: int = 0,
) -> VirtualMachine | None:
    result = compile_source(
        source,
        filename=filename,
        optimization_level=optimization_level,
    )
    if (
        result.reporter.has_errors()
        or result.code is None
        or result.global_count is None
    ):
        return None

    vm = VirtualMachine(result.code, global_count=result.global_count)
    vm.run()
    return vm


def run_file(path: str, optimization_level: int = 0) -> VirtualMachine | None:
    source = Path(path).read_text(encoding="utf-8")
    return run_source(
        source,
        filename=path,
        optimization_level=optimization_level,
    )


def print_assembly(result: CompilationResult) -> None:
    if (
        result.code is None
        or result.program_info is None
        or result.global_count is None
    ):
        return

    formatter = AssemblyFormatter(result.program_info, result.global_count)
    print(formatter.format_program(result.code))


def format_token(token: Token) -> str:
    if token.value is None:
        return token.kind.name
    return f"{token.kind.name}({token.value})"


def print_tokens(source: str, filename: str | None = None) -> bool:
    reporter = DiagnosticReporter(source, filename=filename)
    lexer = Lexer(source, reporter=reporter)

    while True:
        token = lexer.get_next_token()
        print(format_token(token))
        if token.kind == TokenKind.EOF:
            break

    reporter.print(stream=sys.stderr)
    return not reporter.has_errors()


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ProtoLang Compiler")
    parser.add_argument("input", help="input source file")
    parser.add_argument(
        "-O",
        dest="optimization_level",
        type=int,
        choices=(0, 1, 2),
        default=0,
        metavar="LEVEL",
        help=(
            "optimization level: 0=none, "
            "1=local expression optimizations, "
            "2=optimizations including control structures"
        ),
    )
    parser.add_argument(
        "--dump-tokens",
        action="store_true",
        help="print the token sequence and exit",
    )
    parser.add_argument(
        "--dump-ast",
        action="store_true",
        help="print the AST immediately after parsing as Mermaid and exit",
    )
    parser.add_argument(
        "--dump-transformed-ast",
        action="store_true",
        help=(
            "print the AST before code generation as Mermaid and exit "
            "(normalized and, if requested, optimized)"
        ),
    )
    parser.add_argument(
        "--dump-asm",
        action="store_true",
        help="print assembly listing and exit",
    )
    parser.add_argument(
        "--trace-vm",
        action="store_true",
        help="trace VM execution (pc, sp, fp, stack, globals)",
    )
    parser.add_argument(
        "--run-asm",
        action="store_true",
        help="assemble input file and run it on the VM",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    try:
        source = Path(args.input).read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"error: file not found: {args.input}", file=sys.stderr)
        return 2
    except IsADirectoryError:
        print(f"error: is a directory: {args.input}", file=sys.stderr)
        return 2
    except PermissionError:
        print(f"error: permission denied: {args.input}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"error: failed to read input file: {e}", file=sys.stderr)
        return 2

    if args.run_asm:
        if args.dump_tokens or args.dump_ast or args.dump_transformed_ast:
            print(
                "error: token and AST dump options cannot be used with --run-asm",
                file=sys.stderr,
            )
            return 2
        if args.optimization_level != 0:
            print(
                "error: optimization options cannot be used with --run-asm",
                file=sys.stderr,
            )
            return 2

        reporter = DiagnosticReporter(source, filename=args.input)
        assembly_result = assemble_source(source, reporter=reporter)
        for pc, name in assembly_result.unresolved_calls:
            span = assembly_result.unresolved_call_spans.get(pc)
            if span is not None:
                reporter.error_at_span(f"unresolved function call: {name}", span)
            else:
                reporter.error(f"unresolved function call: {name}", 1, 1)

        reporter.print(stream=sys.stderr)
        if reporter.has_errors():
            return 1

        vm = VirtualMachine(
            assembly_result.code,
            global_count=assembly_result.global_count,
        )
        vm.run(trace=args.trace_vm)
        if vm.sp > 0:
            print(f"result = {vm.stack[vm.sp - 1]}")
        print(f"max_stack_size = {vm.max_sp - 1}")
        return 0

    if args.dump_tokens:
        if print_tokens(source, filename=args.input):
            return 0
        return 1

    if args.dump_ast:
        ast, reporter = parse_source(source, filename=args.input)
        if reporter.has_errors():
            reporter.print(stream=sys.stderr)
            return 1

        print(format_ast_as_mermaid(ast))
        return 0

    if args.dump_transformed_ast:
        ast, _, reporter = build_ast(
            source,
            filename=args.input,
            optimization_level=args.optimization_level,
        )
        if reporter.has_errors():
            reporter.print(stream=sys.stderr)
            return 1

        print(format_ast_as_mermaid(ast))
        return 0

    result = compile_source(
        source,
        filename=args.input,
        optimization_level=args.optimization_level,
    )
    result.reporter.print()

    if (
        result.reporter.has_errors()
        or result.code is None
        or result.global_count is None
    ):
        return 1

    if args.dump_asm:
        print_assembly(result)
        return 0

    vm = VirtualMachine(result.code, global_count=result.global_count)
    vm.run(trace=args.trace_vm)

    if vm.sp > 0:
        print(f"result = {vm.stack[vm.sp - 1]}")
    print(f"max_stack_size = {vm.max_sp - 1}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

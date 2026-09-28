# Using the Proto Language Processing System

[Japanese](how_to_use_compiler.md)

## 1 Computing Environment

- OS
  - Windows, macOS, Linux
- Shell
  - bash on Linux and macOS
  - Command Prompt on Windows
- Python
  - Version 3.10 or later

```console
$ python --version
Python 3.10.14
```

## 2 Installing and Using the Proto Language Processing System

### 2.1 Installation

Install the Python libraries required to run the Proto language processing system `ptlc`.
The libraries are installed in a Python virtual environment created with `venv`.

On Linux or macOS, perform the following operation in a shell.

```console
$ bash ./setup
```

On Windows, perform the following operation in Command Prompt.

```console
> setup
```

### 2.2 Running a Proto Program

When a program written in Proto is specified as a command-line argument, the system compiles and executes the program.

```console
$ ./ptlc examples/01_return_expression_value.ptl 
result = 3
max_stack_size = 3
```

The second-to-last line, `result = 3`, indicates that the return value of the `main` function is 3. The last line, `max_stack_size = 3`, indicates that the maximum stack size used by the virtual machine during program execution is 3.

### 2.3 Optimization Levels

Specify the optimization level with the `-O0`, `-O1`, or `-O2` option. The default is `-O0`.

- `-O0`: Perform no optimization.
- `-O1`: Perform local expression-level optimizations such as constant folding and algebraic simplification.
- `-O2`: In addition to `-O1`, perform optimizations involving control structures.

```console
$ ./ptlc -O2 examples/12_tail_recursive_call.ptl
```

The optimization features used by `-O1` and `-O2` must be implemented in the exercises.
In the `-O2` exercise, tail-recursion optimization is implemented as an optimization involving control structures.

### 2.4 Displaying the Token Sequence

The `--dump-tokens` option outputs the token sequence produced by lexical analysis. The program is neither parsed nor executed.

```console
$ ./ptlc --dump-tokens examples/01_return_expression_value.ptl
FUNCTION
IDENT(main)
LPAREN
RPAREN
LBRACE
RETURN
LPAREN
NUMBER(3)
STAR
NUMBER(4)
PLUS
NUMBER(2)
MINUS
NUMBER(3)
RPAREN
SLASH
NUMBER(3)
SEMICOLON
RBRACE
EOF
```

### 2.5 Displaying the Abstract Syntax Tree

- The `--dump-ast` option outputs the abstract syntax tree constructed by the parser in Mermaid format. The program is not executed.
- The `--dump-transformed-ast` option outputs the abstract syntax tree after normalization and the specified optimizations have been applied, in Mermaid format. The program is not executed.

```console
$ ./ptlc --dump-ast examples/01_return_expression_value.ptl
graph TD

n0["Program"]
n1["FunctionDefinition<br/>name=main"]
n2["Block"]
n3["ReturnStatement"]
n4["BinaryOp<br/>op=SLASH"]
n5["BinaryOp<br/>op=MINUS"]
n6["BinaryOp<br/>op=PLUS"]
n7["BinaryOp<br/>op=STAR"]
n8["Number<br/>value=3"]
n9["Number<br/>value=4"]
n10["Number<br/>value=2"]
n11["Number<br/>value=3"]
n12["Number<br/>value=3"]

n7 -->|left| n8
n7 -->|right| n9
n6 -->|left| n7
n6 -->|right| n10
n5 -->|left| n6
n5 -->|right| n11
n4 -->|left| n5
n4 -->|right| n12
n3 -->|expr| n4
n2 -->|items.0| n3
n1 -->|body| n2
n0 -->|items.0| n1
```

### 2.6 Displaying the Compilation Result

The `--dump-asm` option displays the compiled assembly language and exits. The program is not executed.

```console
$ ./ptlc --dump-asm examples/01_return_expression_value.ptl
.globals 0
L00: CALL L03 ; main
L01: CLEAN 0
L02: HALT
L03: ALLOC 0 ; main
L04: IPUSH 0
L05: POP
L06: IPUSH 3
L07: IPUSH 4
L08: IMUL
L09: IPUSH 2
L10: IADD
L11: IPUSH 3
L12: ISUB
L13: IPUSH 3
L14: IDIV
L15: RET
```

### 2.7 Displaying the Execution Trace

The `--trace-vm` option executes the compiled result on the virtual machine and displays the execution trace, including changes in the registers, stack, and global variables.

```console
$ ./ptlc --trace-vm examples/01_return_expression_value.ptl
--------------------------------------------------
NEXT : CALL 3
pc=0  sp=0  fp=0
stack  : []
globals: []
--------------------------------------------------
NEXT : ALLOC 0
pc=3  sp=2  fp=1
stack  : [1, 0]
globals: []
--------------------------------------------------
NEXT : IPUSH 0
pc=4  sp=2  fp=1
stack  : [1, 0]
globals: []
--------------------------------------------------
NEXT : POP
pc=5  sp=3  fp=1
stack  : [1, 0, 0]
globals: []
--------------------------------------------------
NEXT : IPUSH 3
pc=6  sp=2  fp=1
stack  : [1, 0]
globals: []
--------------------------------------------------
NEXT : IPUSH 4
pc=7  sp=3  fp=1
stack  : [1, 0, 3]
globals: []
--------------------------------------------------
NEXT : IMUL
pc=8  sp=4  fp=1
stack  : [1, 0, 3, 4]
globals: []
--------------------------------------------------
NEXT : IPUSH 2
pc=9  sp=3  fp=1
stack  : [1, 0, 12]
globals: []
--------------------------------------------------
NEXT : IADD
pc=10  sp=4  fp=1
stack  : [1, 0, 12, 2]
globals: []
--------------------------------------------------
NEXT : IPUSH 3
pc=11  sp=3  fp=1
stack  : [1, 0, 14]
globals: []
--------------------------------------------------
NEXT : ISUB
pc=12  sp=4  fp=1
stack  : [1, 0, 14, 3]
globals: []
--------------------------------------------------
NEXT : IPUSH 3
pc=13  sp=3  fp=1
stack  : [1, 0, 11]
globals: []
--------------------------------------------------
NEXT : IDIV
pc=14  sp=4  fp=1
stack  : [1, 0, 11, 3]
globals: []
--------------------------------------------------
NEXT : RET
pc=15  sp=3  fp=1
stack  : [1, 0, 3]
globals: []
--------------------------------------------------
NEXT : CLEAN 0
pc=1  sp=1  fp=0
stack  : [3]
globals: []
--------------------------------------------------
NEXT : HALT
pc=2  sp=1  fp=0
stack  : [3]
globals: []
==================================================
HALT
result = 3
pc=2  sp=1  fp=0
stack  : [3]
globals: []
==================================================
result = 3
```

### 2.8 Running an Assembly Language Program

The `--run-asm` option executes a program written in assembly language.

```console
$ ./ptlc --run-asm exercises/1/print_star.pta
*
```

An assembly language program produced with the `--dump-asm` option can also be executed.
In the following example, the compiled assembly language is first saved to a file and then executed with the `--run-asm` option.

```console
$ ./ptlc --dump-asm examples/01_return_expression_value.ptl > examples/01_return_expression_value.pta
$ ./ptlc --run-asm examples/01_return_expression_value.pta
```

### 2.9 Displaying Help

Use the `-h` option to display help.

```console
$ ./ptlc -h
usage: main.py [-h] [-O LEVEL] [--dump-tokens] [--dump-ast]
               [--dump-transformed-ast] [--dump-asm] [--trace-vm] [--run-asm]
               input

ProtoLang Compiler

positional arguments:
  input                 input source file

options:
  -h, --help            show this help message and exit
  -O LEVEL              optimization level: 0=none, 1=local expression optimizations,
                        2=optimizations including control structures
  --dump-tokens         print the token sequence and exit
  --dump-ast            print the AST immediately after parsing as Mermaid and exit
  --dump-transformed-ast
                        print the AST before code generation as Mermaid and exit
                        (normalized and, if requested, optimized)
  --dump-asm            print assembly listing and exit
  --trace-vm            trace VM execution (pc, sp, fp, stack, globals)
  --run-asm             assemble input file and run it on the VM
```

With `-O2`, semantic analysis is run again after optimizations involving control structures.

## 3 Installing and Using Development Support Tools for the Proto Language Processing System

### 3.1 Installation

Install Python libraries useful for developing the Proto language processing system `ptlc`.
The libraries are installed in a Python virtual environment created with `venv`.

On Linux or macOS, perform the following operation in a shell.

```console
$ bash ./setup-dev
```

On Windows, perform the following operation in Command Prompt.

```console
> setup-dev
```

### 3.2 Regression Tests

Run the regression tests for the completed ProtoLang compiler. These tests are mainly used during compiler development and maintenance to verify that changes have not broken existing functionality.

The test code is located in the `tests` directory.

```console
$ ./test
```

To display detailed information for failed tests, specify the `--details` option.

```console
$ ./test --details
```

### 3.3 Static Type Checking

Perform static type checking with [mypy](https://mypy-lang.org/).

```console
$ ./typecheck
```

### 3.4 Formatting

Format the source code with [Ruff](https://docs.astral.sh/ruff/).

```console
$ ./format
```

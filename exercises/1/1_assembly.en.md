# Exercise 1-1:Assembly Language Programming

[Japanese](1_assembly.md)

The purpose of this document is to confirm that assembly language programs consist of lower-level instructions than programs written in high-level languages.

Read the following explanation while referring to the [Proto Virtual Machine Specification](../../docs/vm_spec.en.md), and then work on the task at the end of this document.

## Global Variables

When using global variables, specify the number of global variables with the `.globals` directive.
The following example declares that three global variables are used.

```text
.globals 3
```

Global variables are specified by number (0, 1, 2, ...).

Use the `STOREG` instruction to assign a value to a global variable.
The following example assigns the value 2 on the stack to global variable 0.

```text
IPUSH 2
STOREG 0
```

Use the `LOADG` instruction to read the value of a global variable.
The following example pushes the value of global variable 0 onto the stack.

```text
LOADG 0
```

Run the following program, `globals.pta`.

```text
.globals 1
IPUSH 2
STOREG 0
LOADG 0
HALT
```

The command and its output are shown below. The `--trace-vm` option lets you observe changes in the stack and global variables step by step.

```console
$ ./ptlc --trace-vm --run-asm exercises/1/globals.pta
--------------------------------------------------
NEXT : IPUSH 2
pc=0  sp=0  fp=0
stack  : []
globals: [0]
--------------------------------------------------
NEXT : STOREG 0
pc=1  sp=1  fp=0
stack  : [2]
globals: [0]
--------------------------------------------------
NEXT : LOADG 0
pc=2  sp=0  fp=0
stack  : []
globals: [2]
--------------------------------------------------
NEXT : HALT
pc=3  sp=1  fp=0
stack  : [2]
globals: [2]
==================================================
HALT
result = 2
pc=3  sp=1  fp=0
stack  : [2]
globals: [2]
==================================================
result = 2
```

## Character Output

The Proto virtual machine has the `CPRINT` instruction, which outputs the character corresponding to a specified ASCII code.
This corresponds to a system call in a conventional operating system.

Some examples of ASCII codes are shown below.

- Character `' '` (space)
  - ASCII code 32 in decimal
- Character `'*'`
  - ASCII code 42 in decimal
- Character `'-'`
  - ASCII code 45 in decimal
- Character `'0'`
  - ASCII code 48 in decimal
- Character `'1'`
  - ASCII code 49 in decimal

The following example (`print_star.pta`) outputs one `'*'` character.

```text
.globals 0
IPUSH 42
CPRINT
HALT
```

Running the program produces the following output. Because no newline is printed, the shell prompt will appear next to the `'*'`.

```console
$ ./ptlc --run-asm exercises/1/print_star.pta
*
```

## Arithmetic Operations

The `IADD`, `ISUB`, `IMUL`, and `IDIV` instructions perform integer arithmetic (corresponding to +, -, *, and /, respectively).

The following code fragment pushes the value of global variable 0 plus 1 onto the stack.

```text
LOADG 0
IPUSH 1
IADD
```

## Comparison Operations

The `IEQ`, `INE`, `ILT`, `ILE`, `IGT`, and `IGE` instructions perform comparisons (corresponding to =, !=, <, <=, >, and >=, respectively).

The following code fragment pushes 1 (true) if the condition (value of global variable 0) > 1 is true, and 0 (false) otherwise.

```text
LOADG 0
IPUSH 1
IGT
```

## Conditional Branches

The `JPZ` instruction performs a conditional branch. It jumps to the specified address if the value popped from the stack is 0. The value 0 represents false.

In the following code fragment, if the condition (value of global variable 0) > 1 is false, `JPZ` jumps to `ELSE`, where 0 is pushed onto the stack.
If the condition is true, 1 is pushed and `JMP` jumps to `ENDIF`.

```text
      LOADG 0
      IPUSH 1
      IGT
      JPZ ELSE
      IPUSH 1
      JMP ENDIF
ELSE:
      IPUSH 0
ENDIF:
```

## Exercise

Write an assembly language program, `print_line.pta`, that prints `-` as many times as specified by global variable 0.

Hint: Fill in the part between `STOREG` and `HALT` below.

```text
.globals 1
IPUSH 10
STOREG 0

HALT
```

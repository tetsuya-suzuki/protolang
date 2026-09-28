# Proto Virtual Machine Specification

[Japanese](vm_spec.md)

A simple stack machine that handles integer values.

## 1 Architecture

### 1.1 Registers

- Program counter `pc`
  - Initial value: 0
- Stack pointer `sp`
  - The stack address at which the next value will be pushed.
  - Initial value: 0
- Frame pointer `fp`
  - Initial value: 0

### 1.2 Memory

- Memory for the program
  - A program can neither refer to nor modify its own code. One instruction is stored at each address.
- Stack `stack`
  - A stack for computation.
  - Actual arguments to functions and local variables are also stored on the stack.
- Memory for global variables `global_mem`
  - The value of one variable is stored at each address.

## 2 Input and Output

The `CPRINT` instruction outputs the character corresponding to a specified ASCII code.

## 3 Instruction Set

### 3.1 Data Manipulation

- `IPUSH` *n*

  Pushes integer *n* onto the stack.

  ```text
  stack[sp] ← n
  sp ← sp+1
  pc ← pc+1
  ```

- `POP`

  Discards the value at the top of the stack.

  ```text
  sp ← sp-1
  pc ← pc+1
  ```
  
- `DUP`

  Duplicates the value at the top of the stack.

  ```text
  stack[sp] ← stack[sp-1]
  sp ← sp+1
  pc ← pc+1
  ```

### 3.2 Variable Access

- `LOADG` *i*

  Pushes the value of global variable *i* (*i* = 0, 1, 2, ...) onto the stack.

  ```text
  stack[sp] ← global_mem[i]
  sp ← sp+1
  pc ← pc+1
  ```

- `STOREG` *i*

  Stores the value popped from the stack in global variable *i* (*i* = 0, 1, 2, ...).

  ```text
  sp ← sp-1
  global_mem[i] ← stack[sp]
  pc ← pc+1
  ```

- `LOADA` *i*

  Pushes the value of argument *i* (*i* = 0, 1, 2, ...) onto the stack. Used within a function.

  ```text
  stack[sp] ← stack[fp-2-i]
  sp ← sp+1
  pc ← pc+1
  ```

- `STOREA` *i*

  Stores the value popped from the stack in argument *i* (*i* = 0, 1, 2, ...). Used within a function.

  ```text
  sp ← sp-1
  stack[fp-2-i] ← stack[sp]
  pc ← pc+1
  ```

- `LOADL` *i*

  Pushes the value of local variable *i* (*i* = 0, 1, 2, ...) onto the stack. Used within a function.

  ```text
  stack[sp] ← stack[fp+1+i]
  sp ← sp+1
  pc ← pc+1
  ```

- `STOREL` *i*

  Stores the value popped from the stack in local variable *i* (*i* = 0, 1, 2, ...). Used within a function.

  ```text
  sp ← sp-1
  stack[fp+1+i] ← stack[sp]
  pc ← pc+1
  ```

### 3.3 Arithmetic Operations

- `IADD`

  Pops two integer values from the stack, adds them, and pushes the result onto the stack.

  ```text
  sp ← sp-1
  b ← stack[sp]
  sp ← sp-1
  a ← stack[sp]
  stack[sp] ← a+b
  sp ← sp+1
  pc ← pc+1
  ```

- `ISUB`

  Pops two integer values from the stack, subtracts the value pushed later from the value pushed earlier, and pushes the result onto the stack.

  ```text
  sp ← sp-1
  b ← stack[sp]
  sp ← sp-1
  a ← stack[sp]
  stack[sp] ← a-b
  sp ← sp+1
  pc ← pc+1
  ```

- `IMUL`

  Pops two integer values from the stack, multiplies them, and pushes the result onto the stack.

  ```text
  sp ← sp-1
  b ← stack[sp]
  sp ← sp-1
  a ← stack[sp]
  stack[sp] ← a*b
  sp ← sp+1
  pc ← pc+1
  ```

- `IDIV`
  
  Pops two integer values from the stack, divides the value pushed earlier by the value pushed later, and pushes the result onto the stack. Division follows the semantics of Python's integer division operator (`//`).

  ```text
  sp ← sp-1
  b ← stack[sp]
  sp ← sp-1
  a ← stack[sp]
  stack[sp] ← a//b
  sp ← sp+1
  pc ← pc+1
  ```

- `INEG`

  Pops an integer value from the stack, negates it, and pushes the result onto the stack.

  ```text
  sp ← sp-1
  a ← stack[sp]
  stack[sp] ← -a
  sp ← sp+1
  pc ← pc+1
  ```

### 3.4 Comparison Operations

A comparison result is represented by 0 (false) or 1 (true).

- `IEQ`

  Pops two integer values from the stack, compares them for equality, and pushes the result onto the stack.

  ```text
  sp ← sp-1
  b ← stack[sp]
  sp ← sp-1
  a ← stack[sp]
  stack[sp] ← 1 if a == b, 0 otherwise
  sp ← sp+1
  pc ← pc+1
  ```

- `INE`

  Pops two integer values from the stack, compares them for inequality, and pushes the result onto the stack.

  ```text
  sp ← sp-1
  b ← stack[sp]
  sp ← sp-1
  a ← stack[sp]
  stack[sp] ← 1 if a != b, 0 otherwise
  sp ← sp+1
  pc ← pc+1
  ```

- `ILT`

  Pops two integer values from the stack, checks whether the value pushed earlier is less than the value pushed later, and pushes the result onto the stack.

  ```text
  sp ← sp-1
  b ← stack[sp]
  sp ← sp-1
  a ← stack[sp]
  stack[sp] ← 1 if a < b, 0 otherwise
  sp ← sp+1
  pc ← pc+1
  ```

- `ILE`

  Pops two integer values from the stack, checks whether the value pushed earlier is less than or equal to the value pushed later, and pushes the result onto the stack.

  ```text
  sp ← sp-1
  b ← stack[sp]
  sp ← sp-1
  a ← stack[sp]
  stack[sp] ← 1 if a <= b, 0 otherwise
  sp ← sp+1
  pc ← pc+1
  ```

- `IGT`

  Pops two integer values from the stack, checks whether the value pushed earlier is greater than the value pushed later, and pushes the result onto the stack.

  ```text
  sp ← sp-1
  b ← stack[sp]
  sp ← sp-1
  a ← stack[sp]
  stack[sp] ← 1 if a > b, 0 otherwise
  sp ← sp+1
  pc ← pc+1
  ```

- `IGE`

  Pops two integer values from the stack, checks whether the value pushed earlier is greater than or equal to the value pushed later, and pushes the result onto the stack.

  ```text
  sp ← sp-1
  b ← stack[sp]
  sp ← sp-1
  a ← stack[sp]
  stack[sp] ← 1 if a >= b, 0 otherwise
  sp ← sp+1
  pc ← pc+1
  ```

### 3.5 Control Flow

- `JMP` *addr*

  Jumps to address *addr*.

  ```text
  pc ← addr
  ```

- `JPZ` *addr*
  
  Pops a value from the stack. If the value is 0, jumps to address *addr*; otherwise, proceeds to the next instruction.

  ```text
  sp ← sp-1
  a ← stack[sp]
  pc ← addr if a == 0, pc+1 otherwise
  ```

### 3.6 Functions

- `CALL` *addr*

  Calls the function beginning at address *addr*. Pushes the return address and the current frame pointer onto the stack, and updates the frame pointer.

  ```text
  stack[sp] ← pc+1
  sp ← sp+1
  stack[sp] ← fp
  sp ← sp+1
  fp ← sp-1
  pc ← addr
  ```

  - Note
    - Before calling function `f(`*a_1* `,` *a_2* `,` ...`,` *a_n*`)`, push the actual arguments onto the stack in the order *a_n* through *a_1*.

- `ALLOC` *n*

  Allocates space for *n* local variables on the stack and initializes each local variable to 0.

  ```text
  repeat n times:
    stack[sp] ← 0
    sp ← sp+1
  pc ← pc+1
  ```
  
  - Note
    - Used at function entry.

- `RET`

  Returns from the function. Leaves the value at the top of the stack as the return value, releases the storage for local variables, and restores the frame pointer to its state before the function call. Sets the program counter to the return address.

  ```text
  sp ← sp-1
  ret_val ← stack[sp]
  old_fp ← stack[fp]
  ret_addr ← stack[fp-1]
  sp ← fp-1
  fp ← old_fp
  stack[sp] ← ret_val
  sp ← sp+1
  pc ← ret_addr
  ```

  - Note
    - The value at the top of the stack at this point becomes the return value of the function.

- `CLEAN` *n*

  Releases the stack space for the *n* actual arguments remaining on the stack and leaves the return value at the top of the stack.

  ```text
  sp ← sp-1
  ret_val ← stack[sp]
  sp ← sp-n
  stack[sp] ← ret_val
  sp ← sp+1
  pc ← pc+1
  ```

  - Note
    - Used immediately after returning from a function.

### 3.7 Other Instructions

- `CPRINT`
  Treats the value popped from the stack as an ASCII code and outputs the corresponding character to standard output.

  ```text
  sp ← sp-1
  a ← stack[sp]
  Output ASCII(a)
  pc ← pc+1
  ```

- `HALT`
  Stops the virtual machine.

### 3.8 Assembler Directives and Syntax

- `.globals` *n*
  - Written at the beginning of an assembly language program to specify the number of global variables used.

- `:`
  - The text from the beginning of the line to immediately before `:` is treated as a label. It can be used as the address operand of `JMP`, `JPZ`, or `CALL`.

- `;`
  - Text from a semicolon to the end of the line is treated as a comment.

## 4 Stack Frame

The conceptual layout of a stack frame during a function call is shown below.

```text
(low address)
+----------------+
|    arg_n-1     |
+----------------+
|       .        |
|       .        |
|       .        |
+----------------+
|    arg_2       |
+----------------+
|    arg_1       |
+----------------+
|    arg_0       |
+----------------+
| return address |
+----------------+
|    old fp      | <- fp
+----------------+
|    local_0     |
+----------------+
|    local_1     |
+----------------+
|       .        |
|       .        |
|       .        |
+----------------+
|    local_n-1   |
+----------------+
(high address)
```

- `fp` holds the stack address where the old `fp` is stored and serves as the base for accessing actual arguments and local variables.
- `arg_0` is the first actual argument.
- `local_0` is the first local variable.
- Space for local variables is allocated by executing `ALLOC` *n* at the beginning of the function.
- `LOADA` *i* and `STOREA` *i* access `arg_`*i*.
- `LOADL` *i* and `STOREL` *i* access `local_`*i*.

## 5 Sample Program

- The assembly language program below computes 2 + 3.
- The code beginning at label `ADD` is a function that takes two arguments and computes their sum.
- At the beginning of the program, the actual arguments (2 and 3) to function `ADD` are pushed onto the stack, and function `ADD` is called.

```text
     .globals 0 ; no global variables
     IPUSH 3    ; 2nd argument
     IPUSH 2    ; 1st argument
     CALL ADD
     CLEAN 2    ; remove the two arguments from the stack
     HALT
ADD: ALLOC 0    ; no local variables
     LOADA 0    ; 1st argument
     LOADA 1    ; 2nd argument
     IADD
     RET
```

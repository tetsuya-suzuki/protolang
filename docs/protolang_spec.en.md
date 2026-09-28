# Proto Language Specification

[Japanese](protolang_spec.md)

## 1 Language Overview

Proto is an educational language with the following features for learning the complete flow of lexical analysis, parsing, optimization, code generation, and virtual machine execution.

- It is a procedural language.
- Values are integers only.
- Control structures are `if`, `while`, and `return`.
- The language has block scope.
- Execution starts with the `main` function.
- A function body can also be written in assembly language for the Proto virtual machine.

## 2 Grammar

### 2.1 Syntax Rules

- Regular expressions are used on the right-hand side of lexical rules. Here, `::=` is also used for lexical rules, as it is for syntax rules.
- The syntax diagrams are available [here](railroad_diagram.md) (generated using the [Railroad Diagram Generator](https://www.bottlecaps.de/rr/ui)). Please view them with a light background.

```bnf
/* Lexical rules */

ASM_COMMENT ::= ";" [^\r\n]*
IDENT  ::= [_A-Za-z][_A-Za-z0-9]*
NUMBER ::= [0-9]+

/* Syntax rules for ProtoLang */
Program ::= ( GlobalDeclaration | FunctionDefinition )*

GlobalDeclaration ::= "var" IDENT "=" Expression ";"

FunctionDefinition ::= "function" IDENT "(" ParameterList? ")" ( Block | AsmBlock )

ParameterList ::= IDENT ( "," IDENT )*

Block ::= "{" (Declaration | Statement)* "}"

AsmBlock ::= "asm" "{" AsmLine* "}"

AsmLine ::= AsmDirective | AsmCodeLine

AsmDirective ::= ".function" IDENT

AsmCodeLine ::= (IDENT ":")? Instruction?  ASM_COMMENT?

Instruction ::= "IPUSH"  "-"? NUMBER
              | "POP"
              | "DUP"
              | "LOADG" NUMBER
              | "STOREG" NUMBER
              | "LOADA" NUMBER
              | "STOREA" NUMBER
              | "LOADL" NUMBER
              | "STOREL" NUMBER
              | "IADD"
              | "ISUB"
              | "IMUL"
              | "IDIV"
              | "INEG"
              | "IMOD"
              | "IEQ"
              | "INE"
              | "ILT"
              | "ILE"
              | "IGT"
              | "IGE"
              | "JMP" (NUMBER | IDENT)
              | "JPZ" (NUMBER | IDENT)
              | "CALL" (NUMBER | IDENT)
              | "ALLOC" NUMBER
              | "RET"
              | "CLEAN" NUMBER
              | "CPRINT"
              | "HALT"

Declaration ::= "var" IDENT "=" Expression ";"

Statement ::= Block
            | IfStatement
            | WhileStatement
            | ReturnStatement
            | ExpressionStatement

IfStatement ::= "if" "(" Expression ")" Block "else" (Block | IfStatement)

WhileStatement ::= "while" "(" Expression ")" Block

ReturnStatement ::= "return" Expression ";"

ExpressionStatement ::= Expression ";"

Expression ::= Assignment

Assignment ::= Equality ( "=" Assignment )?

Equality ::= Relational ( ("==" | "!=") Relational )*

Relational ::= Additive ( ("<" | "<=" | ">" | ">=") Additive )*

Additive ::= Term ( ("+" | "-") Term )*

Term ::= Unary ( ("*" | "/") Unary )*

Unary ::= "-" Unary
        | Primary

Primary ::= NUMBER
          | IDENT ( "(" ArgumentList? ")" )?
          | "(" Expression ")"

ArgumentList ::= Expression ( "," Expression )*
```

### 2.2 Function Bodies Written in Assembly

When a function body is written as an `asm` block, use the `.function` directive to declare the name of a Proto function called by a `CALL` instruction within that block.

For example, to call a function named `helper` defined in Proto, write:

```text
.function helper
CALL helper
```

## 3 Semantic Rules

### 3.1 Values and Types

- All values are integers.

### 3.2 Boolean Values

- There is no dedicated Boolean type.
- 0 is treated as false, and any nonzero value as true.

### 3.3 Scope

- Each block has a local scope.
- A variable cannot be redeclared with the same name in the same block.
- An inner block may declare a variable with the same name as one in an outer block.
  - The variable declared in the inner block shadows the variable declared in the outer block.

### 3.4 Functions

- In a function call, actual arguments are evaluated from right to left.
- The number of actual arguments must match the number of formal parameters.
- Forward references in function calls are allowed.

  The following function `foo` calls function `bar`, which is defined later in the source code.

  ```text
  function foo() {
    return bar();
  }

  function bar() {
    return 1;
  }
  ```

- The return value is determined in the following order.
  1. The value of the expression specified by a `return` statement

     The return value of the following function `foo` is 9, the value of the expression `4+5` specified by the `return` statement.

     ```text
     function foo() {
       var x = 1+2;
       x+3;
       return 4+5;
     }
     ```

  2. The value of the last evaluated expression statement

     The return value of the following function `foo` is 6, the value of the expression statement `x+3`, which is evaluated last.

     ```text
     function foo() {
       var x = 1+2;
       x+3;
     }
     ```

  3. 0

     The following function `foo` has neither a `return` statement nor an expression statement, so its return value is 0.
     In Proto, `x = 1+2;` is an expression statement, and its value is 3, the value assigned to variable `x`. However, `var x = 1+2;` is a variable declaration, not an expression statement.

     ```text
     function foo() {
       var x = 1+2;
     }
     ```

### 3.5 Assignment

- Assignment is an expression, not a statement.
  - The expression `y = 7` assigns the integer value 7 to variable `y`.
  - Just as the expression `y + 7` has a value, the expression `y = 7` evaluates to the value assigned to the variable (7 in this example).
- The left-hand side of an assignment must be an identifier.
- Right-associative assignment expressions such as `x = y = 7` can be written.
  - The value 7, which is the value of the expression `y = 7`, is assigned to variable `x`. Therefore, the value of the expression `x = y = 7` is also 7.

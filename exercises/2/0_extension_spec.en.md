# Proto Language Extension Specification

[Japanese](0_extension_spec.md)

## Notation for Abstract Syntax Trees

- *E*, *E_1*, ..., *E_n* are AST subtrees of type `Expression`.
- *B*, *B_1*, ..., *B_n* are AST subtrees of type `Block`.
- *a* and *b* are integer values, and the AST nodes representing them are written as `Number(`*a*`)` and `Number(`*b*`)`, respectively.

## Adding the Remainder Operation

- Lexical analysis
  - Recognize the string `%` as the constant `TokenKind.PERCENT`.
- Grammar

  Before

  ```bnf
  Term ::= Unary ( ("*" | "/") Unary )*
  ```

  After

  ```bnf
  Term ::= Unary ( ("*" | "/" | "%") Unary )*
  ```

- Semantic analysis of the AST node `BinaryOp(op=PERCENT, left=`*E_1*`, right=`*E_2*`)`
  - If *E_1* is of integer type and *E_2* is of integer type, the expression is of integer type.
  - Otherwise, report a type error.

- Virtual machine instruction to add
  - `IMOD`
    1. Let *b* be the integer value popped from the stack.
    2. Let *a* be the integer value popped from the stack.
    3. Push the integer value *a* % *b* onto the stack.

- Target code for the AST node `BinaryOp(op=PERCENT, left=`*E_1*`, right=`*E_2*`)`

```text
   target code for E_1
   target code for E_2
   IMOD
```

## Adding the do-while Statement

- Lexical analysis
  - Recognize the string `do` as the constant `TokenKind.DO`.
- Grammar

  Before

  ```bnf
  Statement ::= Block
            | IfStatement
            | WhileStatement
            | ReturnStatement
            | ExpressionStatement
  ```

  After

  ```bnf
  Statement ::= Block
            | IfStatement
            | WhileStatement
            | DoWhileStatement
            | ReturnStatement
            | ExpressionStatement

  DoWhileStatement ::= "do" Block "while" "(" Expression ")" ";"
  ```

- Semantic analysis of the AST node `DoWhileStatement(body=`*B*`, condition=`*E*`)`
  - Perform semantic analysis on *B*.
  - Perform semantic analysis on *E*.
  - If *E* is not of integer type, report a type error.

- Target code for the AST node `DoWhileStatement(body=`*B*`, condition=`*E*`)`

  ```text
  L1:
      target code for B
      target code for E
      JPZ L2
      JMP L1
  L2:
  ```

## Adding the repeat-until Statement

- Lexical analysis
  - Recognize the string `repeat` as the constant `TokenKind.REPEAT`.
  - Recognize the string `until` as the constant `TokenKind.UNTIL`.
- Grammar

  Before

  ```bnf
  Statement ::= Block
            | IfStatement
            | WhileStatement
            | ReturnStatement
            | ExpressionStatement
  ```

  After

  ```bnf
  Statement ::= Block
            | IfStatement
            | WhileStatement
            | RepeatUntilStatement
            | ReturnStatement
            | ExpressionStatement

  RepeatUntilStatement ::= "repeat" Block "until" "(" Expression ")" ";"
  ```

- Semantic analysis of the AST node `RepeatUntilStatement(body=`*B*`, condition=`*E*`)`
  - Perform semantic analysis on *B*.
  - Perform semantic analysis on *E*.
  - If *E* is not of integer type, report a type error.

- Target code for the AST node `RepeatUntilStatement(body=`*B*`, condition=`*E*`)`

  ```text
  L1:
      target code for B
      target code for E
      JPZ L1
  ```

## Omitting `else`

- Grammar

  Before

  ```bnf
  IfStatement ::= "if" "(" Expression ")" Block "else" (Block | IfStatement)
  ```

  After

  ```bnf
  IfStatement ::= "if" "(" Expression ")" Block ("else" (Block | IfStatement))?
  ```

- Semantic analysis of the AST node `IfStatement(condition=`*E*`, then_stmt=`*B1*`, else_stmt=`*B2*`)`
  - Perform semantic analysis on *E*.
  - If *E* is not of integer type, report a type error.
  - Perform semantic analysis on *B1*.
  - If *B2* is not `None`, perform semantic analysis on *B2*.

- Target code for the AST node `IfStatement(condition=`*E*`, then_stmt=`*B1*`, else_stmt=None)`

  ```text
      target code for E
      JPZ L1
      target code for B1
  L1:
  ```

- Target code for the AST node `IfStatement(condition=`*E*`, then_stmt=`*B1*`, else_stmt=`*B2*`)`. Here, *B2* is not `None`. *B2* may be an `IfStatement` rather than a `Block`, but it is denoted as *B2* for convenience.

  ```text
      target code for E
      JPZ L1
      target code for B1
      JMP L2
  L1:
      target code for B2
  L2:
  ```

## Logical Operators

- Lexical elements to add
  - Recognize the string `&&` as the constant `TokenKind.LAND`.
  - Recognize the string `||` as the constant `TokenKind.LOR`.
  - Recognize the string `!` as the constant `TokenKind.LNOT`.

- Grammar

  Before

  ```bnf
  Assignment ::= Equality ( "=" Assignment )?

  Unary ::= "-" Unary
          | Primary
  ```

  After

  ```bnf
  Assignment ::= LogicalOr ( "=" Assignment )?
  LogicalOr ::= LogicalAnd ( "||" LogicalAnd )*
  LogicalAnd ::= Equality ( "&&" Equality )*

  Unary ::= ( "-" | "!" ) Unary
          | Primary
  ```

- Semantic analysis of the AST node `UnaryOp(op=LNOT, expr=`*E*`)`
  - If *E* is of integer type, the expression is of integer type.
  - Otherwise, report a type error

- Virtual machine instruction to add
  - `INOT`
    1. Let *a* be the integer value popped from the stack.
    2. If *a* is 0, push 1 onto the stack. If *a* is nonzero, push 0 onto the stack.

- Target code for the AST node `UnaryOp(op=LNOT, expr=`*E*`)`

  ```text
      target code for E
      INOT
  ```

- Semantic analysis of the AST node `LogicalAnd([`*E_1*`,` ... `,` *E_n*`])`
  - If *E_1*, ..., *E_n* are all of integer type, the entire expression is of integer type.
  - Otherwise, report a type error.

- Target code for the AST node `LogicalAnd([`*E_1*`,` ...`,` *E_n*`])`

  ```text
      target code for E_1
      JPZ L1
      target code for E_2
      JPZ L1
      ...
      target code for E_n
      JPZ L1
      IPUSH 1
      JMP L2
  L1: IPUSH 0
  L2:
  ```

- Semantic analysis of the AST node `LogicalOr([`*E_1*`,` ...`,` *E_n*`])`
  - If *E_1*, ..., *E_n* are all of integer type, the entire expression is of integer type.
  - Otherwise, report a type error.

- Target code for the AST node `LogicalOr([`*E_1*`,` ...`,` *E_n*`])`

  ```text
      target code for E_1
      JPZ L1
      IPUSH 1
      JMP L_end
  L1:
      target code for E_2
      JPZ L2
      IPUSH 1
      JMP L_end
  L2:
      ...
  Ln-1:
      target code for E_n
      JPZ Ln
      IPUSH 1
      JMP L_end
  Ln:
      IPUSH 0
  L_end:
  ```

## Optimization

- Notation and meaning of AST transformation rules
  - "AST subtree -> AST subtree" means that the AST subtree on the left-hand side is replaced with the AST subtree on the right-hand side.

- AST transformation rules for algebraic simplification
  - Binary operators
    - `BinaryOp(op=PLUS, left=Number(0), right=`*E*`)` -> *E*
    - `BinaryOp(op=PLUS, left=`*E*`, right=Number(0))` -> *E*
    - `BinaryOp(op=MINUS, left=Number(0), right=`*E*`)` -> `UnaryOp(op=MINUS, expr=`*E*`)`
    - `BinaryOp(op=MINUS, left=`*E*`, right=Number(0))` -> *E*
    - `BinaryOp(op=STAR, left=Number(1), right=`*E*`)` -> *E*
    - `BinaryOp(op=STAR, left=`*E*`, right=Number(1))` -> *E*
    - `BinaryOp(op=SLASH, left=`*E*`, right=Number(1))` -> *E*
  - Logical operators
    - `LogicalOr([`*E_1*`,` ...`, Number(0),` ...`, `*E_n*`])` -> `LogicalOr([`*E_1*`, `...`, `*E_n*`])`
      - Remove `Number(0)`.
    - `LogicalOr([])` -> `Number(0)`
    - `LogicalAnd([`*E_1*`, `...`, Number(`*a*`), `...`, `*E_n*`])` → `LogicalAnd([`*E_1*`, `...`, `*E_n*`])`    (*a* ≠ 0)
      - If *a* ≠ 0, remove `Number(`*a*`)`.
    - `LogicalAnd([])` -> `Number(1)`

- AST transformation rules for constant folding

  - `BinaryOp(op=PLUS, left=Number(`*a*`), right=Number(`*b*`))` -> `Number(`*a* + *b*`)`
  - `BinaryOp(op=MINUS, left=Number(`*a*`), right=Number(`*b*`))` -> `Number(`*a* - *b*`)`
  - `BinaryOp(op=STAR, left=Number(`*a*`), right=Number(`*b*`))` -> `Number(`*a* * *b*`)`
  - `BinaryOp(op=SLASH, left=Number(`*a*`), right=Number(`*b*`))` -> `Number(`*a* // *b*`)`    (*b* ≠ 0)
  - `BinaryOp(op=PERCENT, left=Number(`*a*`), right=Number(`*b*`))` -> `Number(`*a* % *b*`)`    (*b* ≠ 0)
  - `UnaryOp(op=MINUS, expr=Number(`*a*`))` -> `Number(-`*a*`)`
  - `UnaryOp(op=LNOT, expr=Number(0))` -> `Number(1)`
  - `UnaryOp(op=LNOT, expr=Number(`*a*`))` -> `Number(0)`    (*a* ≠ 0)

- AST transformation rules for simplification using short-circuit evaluation

  - `LogicalOr([`*E_1*`, `...`, Number(`*a*`), `...`, `*E_n*`])` -> `LogicalOr([`*E_1*`, `...`, Number(`*a*`)])`    (*a* ≠ 0)
    - If *a* ≠ 0, remove the operands after `Number(`*a*`)`.
  - `LogicalAnd([`*E_1*`, `...`, Number(0), `...`, `*E_n*`])` -> `LogicalAnd([`*E_1*`, `...`, Number(0)])`
    - Remove the operands after `Number(0)`.

- AST transformation rule for tail-recursion optimization

  - `ReturnStatement( Call(func_name=f, args=[`*E_1*`, `*E_2*`, ..., `*E_n*`]) )` -> `TailRecursiveCallStatement(args=[`*E_1*`, `*E_2*`, ..., `*E_n*`])` (`f` is the function currently being transformed)
    - `TailRecursiveCallStatement` is an internal node that does not exist in Proto and appears only in the optimized AST.

- Code generation for tail-recursion optimization

  Generate the following code for the AST subtree `TailRecursiveCallStatement(args=[`*E_1*`, `*E_2*`, `...`, `*E_n*`])` in function `f`.
  Here, `func_start` is a label that refers to the instruction immediately after the `ALLOC` instruction that allocates space for the local variables of function `f`.

  ```text
             ALLOC m       ; allocate space for local variables
  func_start:
             ....
             POP           ; discard the result of the preceding expression statement
             target code for E_n
             ....
             target code for E_2
             target code for E_1
             STOREA 0
             STOREA 1
             ....
             STOREA n-1
             JMP func_start
  ```

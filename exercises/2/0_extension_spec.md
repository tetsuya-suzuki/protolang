# Proto言語の拡張仕様

[English](0_extension_spec.en.md)

## 抽象構文木での記法

- *E*, *E_1*, ..., *E_n* は `Expression` 型のAST部分木
- *B*, *B_1*, ..., *B_n* は `Block` 型のAST部分木
- *a*, *b* は整数値とし、それらを表すASTノードをそれぞれ `Number(`*a*`)`, `Number(`*b*`)` と記す。

## 剰余演算の導入

- 字句
  - 文字列 `%` を 定数`TokenKind.PERCENT` として認識する。
- 文法

  変更前

  ```bnf
  Term ::= Unary ( ("*" | "/") Unary )*
  ```

  変更後

  ```bnf
  Term ::= Unary ( ("*" | "/" | "%") Unary )*
  ```

- ASTノード `BinaryOp(op=PERCENT, left=`*E_1*`, right=`*E_2*`)` の意味解析
  - *E_1*が整数型、かつ *E_2*が整数型, 式全体は整数型。
  - それ以外なら、型エラー。

- 追加する仮想マシン命令
  - `IMOD`
    1. スタックからpopした整数値を*b*とする。
    2. スタックからpopした整数値を*a*とする。
    3. *a* % *b*の値（整数）をスタックにpushする。

- ASTノード `BinaryOp(op=PERCENT, left=`*E_1*`, right=`*E_2*`)` の目的コード

```text
   E_1の目的コード
   E_2の目的コード
   IMOD
```

## do-while文の導入

- 字句
  - 文字列 `do` を 定数`TokenKind.DO` として認識する。
- 文法

  変更前

  ```bnf
  Statement ::= Block
            | IfStatement
            | WhileStatement
            | ReturnStatement
            | ExpressionStatement
  ```

  変更後

  ```bnf
  Statement ::= Block
            | IfStatement
            | WhileStatement
            | DoWhileStatement
            | ReturnStatement
            | ExpressionStatement

  DoWhileStatement ::= "do" Block "while" "(" Expression ")" ";"
  ```

- ASTノード `DoWhileStatement(body=`*B*`, condition=`*E*`)`の意味解析
  - *B* を意味解析する。
  - *E* を意味解析する。
  - *E* が整数型でなければ型エラー。

- ASTノード `DoWhileStatement(body=`*B*`, condition=`*E*`)`の目的コード

  ```text
  L1:
      Bの目的コード
      Eの目的コード
      JPZ L2
      JMP L1
  L2:
  ```

## repeat-until文の導入

- 字句
  - 文字列 `repeat` を 定数`TokenKind.REPEAT` として認識する。
  - 文字列 `until` を 定数`TokenKind.UNTIL` として認識する。
- 文法

  変更前

  ```bnf
  Statement ::= Block
            | IfStatement
            | WhileStatement
            | ReturnStatement
            | ExpressionStatement
  ```

  変更後

  ```bnf
  Statement ::= Block
            | IfStatement
            | WhileStatement
            | RepeatUntilStatement
            | ReturnStatement
            | ExpressionStatement

  RepeatUntilStatement ::= "repeat" Block "until" "(" Expression ")" ";"
  ```

- ASTノード `RepeatUntilStatement(body=`*B*`, condition=`*E*`)`の意味解析
  - *B* を意味解析する。
  - *E* を意味解析する。
  - *E* が整数型でなければ型エラー。

- ASTノード `RepeatUntilStatement(body=`*B*`, condition=`*E*`)`の目的コード

  ```text
  L1:
      Bの目的コード
      Eの目的コード
      JPZ L1
  ```

## elseの省略

- 文法

  変更前

  ```bnf
  IfStatement ::= "if" "(" Expression ")" Block "else" (Block | IfStatement)
  ```

  変更後

  ```bnf
  IfStatement ::= "if" "(" Expression ")" Block ("else" (Block | IfStatement))?
  ```

- ASTノード`IfStatement(condition=`*E*`, then_stmt=`*B1*`, else_stmt=`*B2*`)`の意味解析
  - *E*を意味解析する。
  - *E*が整数型でなければ型エラー。
  - *B1*を意味解析する。
  - *B2*が`None`でなければ、*B2*を意味解析する。

- ASTノード`IfStatement(condition=`*E*`, then_stmt=`*B1*`, else_stmt=None)`の目的コード

  ```text
      Eの目的コード
      JPZ L1
      B1の目的コード
  L1:
  ```

- ASTノード `IfStatement(condition=`*E*`, then_stmt=`*B1*`, else_stmt=`*B2*`)`の目的コード。ただし*B2*は`None`ではない。*B2*は`Block`ではなく`IfStatement`の場合もあるが、便宜上*B2*と表記する。

  ```text
      Eの目的コード
      JPZ L1
      B1の目的コード
      JMP L2
  L1:
      B2の目的コード
  L2:
  ```

## 論理演算子

- 追加する字句
  - 文字列 `&&` を 定数`TokenKind.LAND` として認識する。
  - 文字列 `||` を 定数`TokenKind.LOR` として認識する。
  - 文字列 `!` を 定数`TokenKind.LNOT` として認識する。

- 文法

  変更前

  ```bnf
  Assignment ::= Equality ( "=" Assignment )?

  Unary ::= "-" Unary
          | Primary
  ```

  変更後

  ```bnf
  Assignment ::= LogicalOr ( "=" Assignment )?
  LogicalOr ::= LogicalAnd ( "||" LogicalAnd )*
  LogicalAnd ::= Equality ( "&&" Equality )*

  Unary ::= ( "-" | "!" ) Unary
          | Primary
  ```

- ASTノード `UnaryOp(op=LNOT, expr=`*E*`)`の意味解析
  - *E*が整数型なら、式全体は整数型。
  - それ以外なら、型エラー。

- 追加する仮想マシン命令
  - `INOT`
    1. スタックからpopした整数値を*a*とする。
    2. *a*が0なら1をスタックにpushする。*a*が0以外なら0をpushする。

- ASTノード `UnaryOp(op=LNOT, expr=`*E*`)`の目的コード

  ```text
      Eの目的コード
      INOT
  ```

- ASTノード `LogicalAnd([`*E_1*`,` ... `,` *E_n*`])` の意味解析
  - *E_1*, ..., *E_n* がすべて整数型なら、式全体は整数型。
  - それ以外なら、型エラー。

- ASTノード `LogicalAnd([`*E_1*`,` ...`,` *E_n*`])`の目的コード

  ```text
      E_1の目的コード
      JPZ L1
      E_2の目的コード
      JPZ L1
      ...
      E_nの目的コード
      JPZ L1
      IPUSH 1
      JMP L2
  L1: IPUSH 0
  L2:
  ```

- ASTノード `LogicalOr([`*E_1*`,` ...`,` *E_n*`])` の意味解析
  - *E_1*, ..., *E_n* がすべて整数型なら、式全体は整数型。
  - それ以外なら、型エラー。

- ASTノード `LogicalOr([`*E_1*`,` ...`,` *E_n*`])`の目的コード

  ```text
      E_1の目的コード
      JPZ L1
      IPUSH 1
      JMP L_end
  L1:
      E_2の目的コード
      JPZ L2
      IPUSH 1
      JMP L_end
  L2:
      ...
  Ln-1:
      E_nの目的コード
      JPZ Ln
      IPUSH 1
      JMP L_end
  Ln:
      IPUSH 0
  L_end:
  ```

## 最適化

- AST変換規則の記法と意味
  - 「AST部分木 → AST部分木」は、左辺のAST部分木を右辺のAST部分木へ置き換えることを表す。

- 代数的簡約のAST変換規則
  - 二項演算子
    - `BinaryOp(op=PLUS, left=Number(0), right=`*E*`)` → *E*
    - `BinaryOp(op=PLUS, left=`*E*`, right=Number(0))` → *E*
    - `BinaryOp(op=MINUS, left=Number(0), right=`*E*`)` → `UnaryOp(op=MINUS, expr=`*E*`)`
    - `BinaryOp(op=MINUS, left=`*E*`, right=Number(0))` → *E*
    - `BinaryOp(op=STAR, left=Number(1), right=`*E*`)` → *E*
    - `BinaryOp(op=STAR, left=`*E*`, right=Number(1))` → *E*
    - `BinaryOp(op=SLASH, left=`*E*`, right=Number(1))` → *E*
  - 論理演算子
    - `LogicalOr([`*E_1*`,` ...`, Number(0),` ...`, `*E_n*`])` → `LogicalOr([`*E_1*`, `...`, `*E_n*`])`
      - `Number(0)`を削除する。
    - `LogicalOr([])` → `Number(0)`
    - `LogicalAnd([`*E_1*`, `...`, Number(`*a*`), `...`, `*E_n*`])` → `LogicalAnd([`*E_1*`, `...`, `*E_n*`])`    (*a* ≠ 0)
      - *a* ≠ 0のとき、`Number(`*a*`)`を削除する。
    - `LogicalAnd([])` → `Number(1)`

- 定数畳み込みのAST変換規則

  - `BinaryOp(op=PLUS, left=Number(`*a*`), right=Number(`*b*`))` → `Number(`*a* + *b*`)`
  - `BinaryOp(op=MINUS, left=Number(`*a*`), right=Number(`*b*`))` → `Number(`*a* - *b*`)`
  - `BinaryOp(op=STAR, left=Number(`*a*`), right=Number(`*b*`))` → `Number(`*a* * *b*`)`
  - `BinaryOp(op=SLASH, left=Number(`*a*`), right=Number(`*b*`))` → `Number(`*a* // *b*`)`    (*b* ≠ 0)
  - `BinaryOp(op=PERCENT, left=Number(`*a*`), right=Number(`*b*`))` → `Number(`*a* % *b*`)`    (*b* ≠ 0)
  - `UnaryOp(op=MINUS, expr=Number(`*a*`))` → `Number(-`*a*`)`
  - `UnaryOp(op=LNOT, expr=Number(0))` → `Number(1)`
  - `UnaryOp(op=LNOT, expr=Number(`*a*`))` → `Number(0)`    (*a* ≠ 0)

- 短絡評価を利用した簡約のAST変換規則

  - `LogicalOr([`*E_1*`, `...`, Number(`*a*`), `...`, `*E_n*`])` → `LogicalOr([`*E_1*`, `...`, Number(`*a*`)])`    (*a* ≠ 0)
    - *a* ≠ 0のとき、`Number(`*a*`)` より後ろのオペランドを削除する。
  - `LogicalAnd([`*E_1*`, `...`, Number(0), `...`, `*E_n*`])` → `LogicalAnd([`*E_1*`, `...`, Number(0)])`
    - `Number(0)` より後ろのオペランドを削除する。

- 末尾再帰最適化のAST変換規則

  - `ReturnStatement( Call(func_name=f, args=[`*E_1*`, `*E_2*`, ..., `*E_n*`]) )` → `TailRecursiveCallStatement(args=[`*E_1*`, `*E_2*`, ..., `*E_n*`])` (`f` は現在変換中の関数)
    - `TailRecursiveCallStatement` はProto言語には存在しない、最適化後のASTにのみ現れる内部ノードである。

- 末尾再帰最適化のコード生成

  関数`f`のAST部分木`TailRecursiveCallStatement(args=[`*E_1*`, `*E_2*`, `...`, `*E_n*`])`に対して、次のようなコードを生成する。
  ただし`func_start`は、関数`f`の局所変数領域を確保する`ALLOC`命令の直後を指すラベルとする。

  ```text
             ALLOC m       ; 局所変数の領域を確保する
  func_start:
             ....
             POP           ; 直前の式文の評価結果を捨てる
             E_nの目的コード
             ....
             E_2の目的コード
             E_1の目的コード
             STOREA 0
             STOREA 1
             ....
             STOREA n-1
             JMP func_start
  ```

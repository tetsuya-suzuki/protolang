# Proto言語仕様

[English](protolang_spec.en.md)

## 1 言語の概要

Proto言語は、次のような特徴を持つ、字句解析・構文解析・最適化・コード生成・仮想機械実行を一通り学ぶための教育用言語である。

- 手続き型言語。
- 値は整数のみ。
- 制御構文は `if`, `while`, `return` の3つ。
- ブロックスコープを持つ。
- `main`関数から実行を開始する。
- 関数本体を（Proto仮想マシンの）アセンブリ言語で記述することもできる。

## 2 文法

### 2.1 構文規則

- 字句規則(lexical rules)の右辺には正規表現を用いる。ここでは構文規則と同じ ::= を用いて表記する。
- 構文図式は[こちら](railroad_diagram.md)（[Railroad Diagram Generator](https://www.bottlecaps.de/rr/ui)で作成）。画面の背景を明るくして閲覧してください。

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

### 2.2 アセンブリによる関数本体

関数本体を `asm` ブロックで記述する場合、`.function` ディレクティブを用いて、そのブロック内の `CALL` 命令から呼び出すProto言語の関数名を宣言する。

例えば、Proto言語で定義された関数 `helper` を呼び出す場合は、次のように記述する。

```text
.function helper
CALL helper
```

`.function` は呼び出し先のProto言語関数を宣言するためのディレクティブであり、関数そのものを定義するものではない。

## 3. 意味規則

### 3.1 値と型

- 値はすべて整数である。

### 3.2 真偽値

- 真偽値専用型は持たない。
- 0 を偽、0 以外を真として扱う。

### 3.3 スコープ

- ブロックごとに局所スコープを持つ。
- 同一ブロック内で同名変数を再宣言することはできない。
- 内側ブロックで外側と同名変数を宣言することはできる。
  - 内側で宣言された変数が、外側で宣言された変数を隠す。

### 3.4 関数

- 関数呼び出しでは、実引数を右から左の順に評価する。
- 関数の実引数個数は仮引数個数と一致しなければならない。
- 前方参照の関数呼び出しは許す。

  次の関数`foo`は、ソースコード上でその先に定義されている関数`bar`を呼び出している。

   ```text
   function foo() {
     return bar();
   }
   
   function bar() {
     return 1;
   }
   ```

- 戻り値は次の順で決定される。
  1. return文で指定された式の値

     次の関数`foo`の戻り値は、`return`文で指定された式`4+5`の評価値9である。

     ```text
     function foo() {
       var x = 1+2;
       x+3;
       return 4+5;
     }
     ```

  2. 最後に評価した式文の値

     次の関数`foo`の戻り値は、最後に評価される式文`x+3`の評価値6である。

     ```text
     function foo() {
       var x = 1+2;
       x+3;
     }
     ```

  3. 0

     次の関数`foo`には`return`文も式文もないので、その戻り値は0である。
     Proto言語では、`x = 1+2;`は式文でありその評価値は変数`x`に代入される3である。
     しかし`var x = 1+2;`は変数宣言であり、式文ではない。

     ```text
     function foo() {
       var x = 1+2;
     }
     ```

### 3.5 代入

- 代入は文ではなく式である。
  - 式`y = 7`によって変数yに整数値7が代入される。
  - 式`y + 7`が評価値を持つように、式`y = 7`は変数に代入した値(この例では7)を評価値とする。
- 代入の左辺は識別子でなければならない。
- `x = y = 7` のような右結合の代入式を書ける。
  - 式`y = 7`の評価値である7が、変数`x`にその7が代入される。したがって、式 `x = y = 7` の評価値も7となる。

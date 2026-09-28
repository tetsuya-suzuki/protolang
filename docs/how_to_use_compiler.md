# Proto言語処理系の使い方

[English](how_to_use_compiler.en.md)

## 1 計算機環境

- OS
  - Windows、macOS、Linux
- シェル
  - Linux、macOSの場合はbash
  - Windowsの場合はコマンドプロンプト
- Python処理系
  - バージョン3.10以上

```console
$ python --version
Python 3.10.14
```

## 2 Proto言語処理系のインストールと使い方

### 2.1 インストール

Proto言語処理系 `ptlc` の実行に必要なPythonライブラリをインストールする。
ライブラリは`venv`で作成したPython仮想環境にインストールされる。

Linux、macOSの場合、シェル上で次の操作をする。

```console
$ bash ./setup
```

Windowsの場合、コマンドプロンプトで次の操作をする。

```console
> setup
```

### 2.2 Proto言語プログラムの実行

コマンドライン引数にProto言語で記述されたプログラムを指定すると、そのプログラムをコンパイルして実行する。

```console
$ ./ptlc examples/01_return_expression_value.ptl 
result = 3
max_stack_size = 3
```

最後から２番目の行`result = 3`は`main`関数の戻り値が3であることを示している。また、最後の行`max_stack_size = 3`は、プログラムの実行中に仮想マシンが使用したスタックの最大長が3であることを示している。

### 2.3 最適化レベル

`-O0`、`-O1`、`-O2`オプションで最適化レベルを指定する。省略時は`-O0`である。

- `-O0`: 最適化しない
- `-O1`: 定数畳み込みと代数的簡約など、式レベルの局所最適化を行う。
- `-O2`: `-O1`に加えて、制御構造を含む最適化を行う。

```console
$ ./ptlc -O2 examples/12_tail_recursive_call.ptl
```

`-O1`および`-O2`で使用する最適化機能は、演習課題で実装する。
`-O2`の演習課題では、制御構造を含む最適化として末尾再帰最適化を実装する。

### 2.4 トークン列の表示

`--dump-tokens`オプションは、字句解析によって得られたトークン列を出力する。プログラムの構文解析や実行は行わない。

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

### 2.5 抽象構文木の表示

- `--dump-ast`オプションは、構文解析器で構築された抽象構文木をMermaid形式で出力する。プログラムは実行しない。
- `--dump-transformed-ast`オプションは、正規化や指定された最適化を施した後の抽象構文木をMermaid形式で出力する。プログラムは実行しない。

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

### 2.6 コンパイル結果の表示

`--dump-asm`オプションはコンパイル結果のアセンブリ言語を表示して終了する。プログラムは実行しない。

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

### 2.7 実行過程の表示

`--trace-vm`オプションは、コンパイル結果を仮想マシンで実行し、その実行過程（レジスタ、スタック、大域変数の変化）を出力する。

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

### 2.8 アセンブリ言語プログラムの実行

`--run-asm`オプションは、アセンブリ言語で書かれたプログラムを実行する。

```console
$ ./ptlc --run-asm exercises/1/print_star.pta
*
```

`--dump-asm`オプションで出力したアセンブリ言語プログラムを実行することもできる。
下記の例では、コンパイル結果のアセンブリ言語をファイルに保存し、そのファイルを`--run-asm`オプションで実行している。

```console
$ ./ptlc --dump-asm examples/01_return_expression_value.ptl > examples/01_return_expression_value.pta
$ ./ptlc --run-asm examples/01_return_expression_value.pta
```

### 2.9 ヘルプの表示

`-h`オプションでヘルプを表示する。

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

`-O2`では、制御構造を含む最適化の後に意味解析を再実行する。

## 3 Proto言語処理系開発支援ツールのインストールと使い方

### 3.1 インストール

Proto言語処理系`ptlc`の開発に便利なPythonライブラリをインストールする。
ライブラリは`venv`で作成したPython仮想環境にインストールされる。

Linux、macOSの場合、シェル上で次の操作をする。

```console
$ bash ./setup-dev
```

Windowsの場合、コマンドプロンプトで次の操作をする。

```console
> setup-dev
```

### 3.2 回帰テスト

完成したProto言語処理系に対する回帰テストを実行する。主に処理系の開発・保守時に、変更によって既存の機能が損なわれていないことを確認するために使用する。

テストコードは`tests`ディレクトリ内に配置されている。

```console
$ ./test
```

失敗したテストの詳細を表示する場合は、`--details`オプションを指定する。

```console
$ ./test --details
```

### 3.3 静的型検査

[mypy](https://mypy-lang.org/)による静的型検査を行う。

```console
$ ./typecheck
```

### 3.4 フォーマット

[Ruff](https://docs.astral.sh/ruff/)によってソースコードを整形する。

```console
$ ./format
```

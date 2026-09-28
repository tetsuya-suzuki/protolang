# Proto仮想マシン仕様

[English](vm_spec.en.md)

整数型を扱える簡単なスタックマシン。

## 1 構成

### 1.1 レジスタ

- プログラムカウンタ `pc`
  - 初期値0
- スタックポインタ `sp`
  - 次に値をpushするスタック上の番地
  - 初期値0
- フレームポインタ `fp`
  - 初期値0

### 1.2 メモリ

- プログラムを配置するメモリ
  - プログラムが自分自身のコードを参照することも書き換えることもできない。1つの番地に1つの命令が記録される。
- スタック `stack`
  - 計算用のスタック
  - 関数への実引数や関数の局所変数もスタック上に配置する。
- グローバル変数用メモリ `global_mem`
  - 1つの番地に1つの変数の値を記録する。

## 2 入出力

`CPRINT`命令によって、指定したASCIIコードに対応する文字を出力できる。

## 3 命令一覧

### 3.1 データ操作

- `IPUSH` *n*
  
  整数*n*をスタックにpushする。

  ```text
  stack[sp] ← n
  sp ← sp+1
  pc ← pc+1
  ```

- `POP`

  スタックトップの値を捨てる。

  ```text
  sp ← sp-1
  pc ← pc+1
  ```

- `DUP`

  スタックトップの値を複製する。

  ```text
  stack[sp] ← stack[sp-1]
  sp ← sp+1
  pc ← pc+1
  ```

### 3.2 変数アクセス

- `LOADG` *i*

  *i* (=0, 1, 2, ...)番目の大域変数の値をスタックにpushする。

  ```text
  stack[sp] ← global_mem[i]
  sp ← sp+1
  pc ← pc+1
  ```

- `STOREG` *i*

  スタックからpopした値を、*i* (=0, 1, 2, ...)番目の大域変数に保存する。

  ```text
  sp ← sp-1
  global_mem[i] ← stack[sp]
  pc ← pc+1
  ```

- `LOADA` *i*

  *i* (=0, 1, 2, ...)番目の引数の値をスタックにpushする。関数内で使用する。

  ```text
  stack[sp] ← stack[fp-2-i]
  sp ← sp+1
  pc ← pc+1
  ```

- `STOREA` *i*

  スタックからpopした値を、*i* (=0, 1, 2, ...)番目の引数に保存する。関数内で使用する。

  ```text
  sp ← sp-1
  stack[fp-2-i] ← stack[sp]
  pc ← pc+1
  ```

- `LOADL` *i*

  *i* (=0, 1, 2, ...)番目の局所変数の値をスタックにpushする。関数内で使用する。

  ```text
  stack[sp] ← stack[fp+1+i]
  sp ← sp+1
  pc ← pc+1
  ```

- `STOREL` *i*

  スタックからpopした値を、*i* (=0, 1, 2, ...)番目の局所変数に保存する。関数内で使用する。

  ```text
  sp ← sp-1
  stack[fp+1+i] ← stack[sp]
  pc ← pc+1
  ```

### 3.3 算術演算

- `IADD`

  スタックからpopした2つの整数値を加算し、結果をスタックにpushする。

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

  スタックからpopした2つの整数値について、先にpushされていた値から後にpushされた値を減算し、結果をスタックにpushする。

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

  スタックからpopした2つの整数値を乗算し、結果をスタックにpushする。

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

  スタックからpopした2つの整数値について、先にpushされていた値を後にpushされた値で除算し、結果をスタックにpushする。
  除算はPythonの整数除算（`//`）の仕様に従う。

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

  スタックからpopした整数値の符号を反転し、結果をスタックにpushする。

  ```text
  sp ← sp-1
  a ← stack[sp]
  stack[sp] ← -a
  sp ← sp+1
  pc ← pc+1
  ```

### 3.4 比較演算

比較結果は0(false)または1(true)で表す。

- `IEQ`

  スタックからpopした2つの整数値が等しいかを判定し、その結果をスタックにpushする。

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

  スタックからpopした2つの整数値が等しくないかを判定し、その結果をスタックにpushする。

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

  スタックからpopした2つの整数値について、先にpushされていた値が後にpushされた値より小さいかを判定し、その結果をスタックにpushする。

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

  スタックからpopした2つの整数値について、先にpushされていた値が後にpushされた値以下であるかを判定し、その結果をスタックにpushする。

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

  スタックからpopした2つの整数値について、先にpushされていた値が後にpushされた値より大きいかを判定し、その結果をスタックにpushする。

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

  スタックからpopした2つの整数値について、先にpushされていた値が後にpushされた値以上であるかを判定し、その結果をスタックにpushする。

  ```text
  sp ← sp-1
  b ← stack[sp]
  sp ← sp-1
  a ← stack[sp]
  stack[sp] ← 1 if a >= b, 0 otherwise
  sp ← sp+1
  pc ← pc+1
  ```

### 3.5 制御

- `JMP` *addr*

  *addr*番地へジャンプする。

  ```text
  pc ← addr
  ```

- `JPZ` *addr*

  スタックからpopした値が0ならば*addr*番地へジャンプする。0でなければ次の命令へ進む。

  ```text
  sp ← sp-1
  a ← stack[sp]
  pc ← addr if a == 0, pc+1 otherwise
  ```

### 3.6 関数

- `CALL` *addr*

  *addr*番地から始まる関数を呼び出す。戻り番地と現在のフレームポインタをスタックにpushし、フレームポインタを更新する。

  ```text
  stack[sp] ← pc+1
  sp ← sp+1
  stack[sp] ← fp
  sp ← sp+1
  fp ← sp-1
  pc ← addr
  ```

  - 補足
    - 関数`f(`*a_1* `,` *a_2* `,` ...`,` *a_n*`)`を呼び出す前に、実引数を*a_n*から*a_1*の順にスタックにpushしておく。

- `ALLOC` *n*

  局所変数 *n* 個分のメモリ領域をスタック上に確保し、各局所変数を0で初期化する。

  ```text
  repeat n times:
    stack[sp] ← 0
    sp ← sp+1
  pc ← pc+1
  ```

  - 補足
    - 関数の入り口で使用する。

- `RET`

  関数から戻る。スタックトップの値を戻り値として残し、局所変数の領域を解放して、フレームポインタを呼び出し前の状態に戻す。プログラムカウンタに戻り番地を設定する。

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

  - 補足
    - 関数から戻る直前にスタックトップにある値が、この関数の戻り値となる。

- `CLEAN` *n*

  スタック上に残っている*n*個の実引数を取り除き、戻り値をスタックトップに残す。

  ```text
  sp ← sp-1
  ret_val ← stack[sp]
  sp ← sp-n
  stack[sp] ← ret_val
  sp ← sp+1
  pc ← pc+1
  ```

  - 補足
    - 関数から戻った直後に使用する。

### 3.7 その他の命令

- `CPRINT`

  スタックからpopした値をASCIIコードとして、標準出力にその文字を出力する。

  ```text
  sp ← sp-1
  a ← stack[sp]
  Output ASCII(a)
  pc ← pc+1
  ```

- `HALT`

  仮想マシンを停止する。

### 3.8 アセンブラ指示と構文

- `.globals` *n*
  - アセンブリ言語プログラムの先頭に記述し、使用する大域変数の個数を指定する。

- `:`
  - 行頭から`:`の直前まではラベルとして扱われる。`JMP`, `JPZ`, `CALL`のアドレス部として利用できる。

- `;`
  - セミコロンから行末まではコメントとして扱われる。

## 4 スタックフレーム

関数呼び出し時のスタックフレームの概念図は次のとおり。

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

- `fp` は、旧`fp` が格納されているスタック上の番地を記録しており、実引数や局所変数へアクセスするときの起点となる。
- `arg_0` は最初の実引数である。
- `local_0` は最初の局所変数である。
- 局所変数のメモリ領域は関数の先頭で `ALLOC` *n* を実行して確保する。
- `LOADA` *i* と `STOREA` *i* は `arg_`*i* にアクセスする。
- `LOADL` *i* と `STOREL` *i* は `local_`*i* にアクセスする。

## 5 サンプルプログラム

- 下記のアセンブリ言語プログラムは2+3を計算するプログラムである。
- ラベル`ADD`以降が、２つの引数を取り、それらの和を計算する関数である。
- プログラムの先頭で関数`ADD`への実引数（2と3）をスタックにpushし、関数`ADD`を呼び出す。

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

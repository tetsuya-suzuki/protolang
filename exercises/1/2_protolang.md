# 演習1-2 Proto言語プログラミング

[English](2_protolang.en.md)

この文書の目的は、Proto言語の文法とProto言語プログラムの動作を理解することである。

[Proto言語の仕様書](../../docs/protolang_spec.md)も参照しながら、下記の説明を読んだ上で、この文書の最後にある課題に取り組む。

[ディレクトリ`examples`](../../examples/README.md)にあるサンプルプログラムも参考にするとよい。

## main関数

Proto言語プログラムはmain関数から実行が開始される。

## if文

Proto言語のif文の使用例である。if文はelseを省略できない。

```text
function main() {
    if (3 < 5) {
        return 1;
    } else {
        return 0;
    }
}
```

## 入出力

Proto言語自体に入出力の機能はない。
しかしProto仮想マシンには、指定したASCIIコードの文字を出力するCPRINT命令がある。

したがってProto言語プログラムから文字を出力するには、アセンブリ言語で実装したProto言語の関数を実装する必要がある。

次の関数`print_ch`は引数にASCIIコードをとり、その文字を出力する。

```text
function print_ch(x) asm {
  LOADA 0
  CPRINT
  IPUSH 0
  RET
}
```

## 演習問題

[下記のプログラム(print_int.ptl)](print_int.ptl)の関数`print_int`を編集して、整数値を出力できるようにしてください。

```text
function print_ch(x) asm {
  LOADA 0
  CPRINT
  IPUSH 0
  RET
}

function print_eol() {
  print_ch(10);
}

function print_sp() {
  print_ch(32);
}

function print_minus() {
  print_ch(45);
}

function print_digit(d) {
  if (d < 0) {
    return 0;
  } else {
  }
  if (d > 9) {
    return 0;
  } else {
  }
  print_ch(48+d);
}

function print_int(x) {
  print_minus();
}

function main() {
  print_int(-265);
  print_sp();
  print_int(0);
  print_sp();
  print_int(48);
  print_eol();
}
```

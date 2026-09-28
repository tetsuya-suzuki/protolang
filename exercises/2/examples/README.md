# 参考資料

[English](README.en.md)

演習課題に関連するサンプルプログラムと、それに対応する抽象構文木を示す。

抽象構文木はMermaid形式（`.mmd`）で記述されている。
[Mermaid Live Editor](https://mermaid.live/)などを使用して図を表示できる。

## 制御構造

- do-while文の使用例
  - [プログラム do_while.ptl](do_while.ptl), [抽象構文木](do_while_ast.mmd)
- if文の使用例
  - [プログラム if.ptl](if.ptl), [抽象構文木](if_ast.mmd)
- repeat-until文の使用例
  - [プログラム repeat_until.ptl](repeat_until.ptl), [抽象構文木](repeat_until_ast.mmd)

## 演算子と式

- 論理否定演算子`!`の使用例
  - [プログラム lnot.ptl](lnot.ptl), [抽象構文木](lnot_ast.mmd)
- 論理積演算子`&&`の使用例
  - [プログラム land.ptl](land.ptl), [抽象構文木](land_ast.mmd)
- 論理和演算子`||`の使用例
  - [プログラム lor.ptl](lor.ptl), [抽象構文木](lor_ast.mmd)
- 論理演算子を組み合わせた例
  - [プログラム logical_operators.ptl](logical_operators.ptl), [抽象構文木](logical_operators_ast.mmd)
- 剰余演算子`%`の使用例
  - [プログラム mod.ptl](mod.ptl), [抽象構文木](mod_ast.mmd)
- 代入できない式への代入の例
  - [プログラム left-hand_side_error.ptl](left-hand_side_error.ptl), [抽象構文木](left-hand_side_error_ast.mmd)

## 最適化レベル1
- [プログラム opt1/expressions.ptl](opt1/expressions.ptl)
- 最適化レベル0 (`-O0`) [抽象構文木](opt1/expressions_O0.ast.mmd), [コンパイル結果 opt1/expressions_O0.pta](opt1/expressions_O0.pta), [仮想マシンの実行過程 opt1/expressions_O0.trace](opt1/expressions_O0.trace)
- 最適化レベル1 (`-O1`) [抽象構文木](opt1/expressions_O1.ast.mmd), [コンパイル結果 opt1/expressions_O1.pta](opt1/expressions_O1.pta), [仮想マシンの実行過程 opt1/expressions_O1.trace](opt1/expressions_O1.trace)

## 最適化レベル2
- [プログラム opt2/tail_recursion.ptl](opt2/tail_recursion.ptl)
- 最適化レベル0 (`-O0`) [抽象構文木](opt2/tail_recursion_O0.ast.mmd), [コンパイル結果 opt2/tail_recursion_O0.pta](opt2/tail_recursion_O0.pta), [仮想マシンの実行過程 opt2/tail_recursion_O0.trace](opt2/tail_recursion_O0.trace)
- 最適化レベル2 (`-O2`) [抽象構文木](opt2/tail_recursion_O2.ast.mmd), [コンパイル結果 opt2/tail_recursion_O2.pta](opt2/tail_recursion_O2.pta), [仮想マシンの実行過程 opt2/tail_recursion_O2.trace](opt2/tail_recursion_O2.trace)


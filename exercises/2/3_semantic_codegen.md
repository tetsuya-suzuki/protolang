# 演習2-3 意味解析器とコード生成器の拡張

[English](3_semantic_codegen.en.md)

## 問題

### 意味解析

[Proto言語の拡張仕様](0_extension_spec.md)で定義されている次の機能について、意味解析処理を実装しなさい。

- do-while文
- repeat-until文
- elseの省略
- 論理演算子

### 仮想マシン命令の追加

[Proto言語の拡張仕様](0_extension_spec.md)で定義されている新しい仮想マシン命令を実装しなさい。

- `IMOD`
- `INOT`

### コード生成

[Proto言語の拡張仕様](0_extension_spec.md)で定義されている次の機能について、コード生成処理を実装しなさい。

- 剰余演算
- do-while文
- repeat-until文
- elseの省略
- 論理演算子

具体的な目的コードの生成規則は、上記仕様書に従うこと。

## テストコードの実行方法

```console
$ ./test 3
```

失敗したテストの詳細を表示する場合は、`--details`オプションを指定する。

```console
$ ./test 3 --details
```

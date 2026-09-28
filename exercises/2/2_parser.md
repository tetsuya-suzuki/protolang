# 演習2-2 構文解析器の拡張

[English](2_parser.en.md)

## 問題

[Proto言語の拡張仕様](0_extension_spec.md)で定義されている次の構文を構文解析器に実装しなさい。

- 剰余演算
- do-while文
- repeat-until文
- elseの省略
- 論理演算子

生成規則の変更については、上記仕様書にしたがうこと。

## テストコードの実行方法

```console
$ ./test 2
```

失敗したテストの詳細を表示する場合は、`--details`オプションを指定する。

```console
$ ./test 2 --details
```

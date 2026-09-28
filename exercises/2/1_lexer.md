# 演習2-1 字句解析器の拡張

[English](1_lexer.en.md)

## 問題

[Proto言語の拡張仕様](0_extension_spec.md)で定義されている拡張のうち、
字句解析に関する機能を実装しなさい。

実装対象は次のとおりである。

- 剰余演算
- do-while文
- repeat-until文
- 論理演算子

それぞれで追加する字句については、上記仕様書を参照すること。

## テストコードの実行方法

```console
$ ./test 1
```

失敗したテストの詳細を表示する場合は、`--details`オプションを指定する。

```console
$ ./test 1 --details
```

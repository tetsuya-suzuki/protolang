# Exercise 2-4: Extending the Optimizer (1)

[Japanese](4_optimizer_1.md)

## Task

Implement the AST transformations defined in the [Optimization section of the Proto Language Extension Specification](0_extension_spec.en.md#optimization).

Implement the following:

- Algebraic simplification
- Constant folding
- Simplification using short-circuit evaluation

Refer to the specification above for the AST transformation rules.

## Running the Tests

```console
./test 4
```

To display detailed information for failed tests, specify the `--details` option.

```console
$ ./test 4 --details
```

# Exercise 2-5: Extending the Optimizer (2)

[日本語](5_optimizer_2.md)

## Problem

Implement the AST transformation defined in the ["Optimization" section of the Proto language extension specification](0_extension_spec.en.md#optimization).

The following optimization must be implemented:

- Tail recursion optimization

Refer to the specification above for the AST transformation rules and code generation rules for tail recursion.

## Running the Test Code

```console
$ ./test 5
```

To display detailed information for failed tests, specify the `--details` option.

```console
$ ./test 5 --details
```

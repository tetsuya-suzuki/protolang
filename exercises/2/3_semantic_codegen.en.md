# Exercise 2-3: Extending the Semantic Analyzer and Code Generator

[Japanese](3_semantic_codegen.md)

## Task

### Semantic Analysis

Implement semantic analysis for the following features defined in the [Proto Language Extension Specification](0_extension_spec.en.md).

- do-while statement
- repeat-until statement
- Omission of `else`
- Logical operators

### Adding Virtual Machine Instructions

Implement the new virtual machine instructions defined in the [Proto Language Extension Specification](0_extension_spec.en.md).

- `IMOD`
- `INOT`

### Code Generation

Implement code generation for the following features defined in the [Proto Language Extension Specification](0_extension_spec.en.md).

- Remainder operation
- do-while statement
- repeat-until statement
- Omission of `else`
- Logical operators

Follow the target-code generation rules in the specification above.

## Running the Tests

```console
$ ./test 3
```

To display detailed information for failed tests, specify the `--details` option.

```console
$ ./test 3 --details
```

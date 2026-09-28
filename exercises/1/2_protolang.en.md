# Exercise 1-2: Proto Programming

[Japanese](2_protolang.md)

The purpose of this document is to understand the syntax of Proto and the behavior of Proto programs.

Read the following explanation while referring to the [Proto Language Specification](../../docs/protolang_spec.en.md), and then work on the task at the end of this document.

The sample programs in the [`examples` directory](../../examples/README.en.md) may also be helpful.

## The `main` Function

Execution of a Proto program starts with the `main` function.

## The `if` Statement

The following is an example of an `if` statement in Proto. The `else` part cannot be omitted.

```text
function main() {
    if (3 < 5) {
        return 1;
    } else {
        return 0;
    }
}
```

## Input and Output

Proto itself has no input/output facilities.
However, the Proto virtual machine has the `CPRINT` instruction, which outputs the character corresponding to a specified ASCII code.

Therefore, to output characters from a Proto program, a Proto function implemented in assembly language is required.

The following function, `print_ch`, takes an ASCII code as an argument and outputs the corresponding character.

```text
function print_ch(x) asm {
  LOADA 0
  CPRINT
  IPUSH 0
  RET
}
```

## Exercise

Edit the `print_int` function in [the following program (`print_int.ptl`)](print_int.ptl) so that it can output integer values.

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

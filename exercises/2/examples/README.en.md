# Reference Materials

[Japanese](README.md)

This directory contains sample programs related to the exercises and their corresponding abstract syntax trees.

The abstract syntax trees are written in Mermaid format (`.mmd`).
You can display the diagrams using tools such as [Mermaid Live Editor](https://mermaid.live/).

## Control Structures

- Example of a do-while statement
  - [Program do_while.ptl](do_while.ptl), [abstract syntax tree](do_while_ast.mmd)
- Example of an if statement
  - [Program if.ptl](if.ptl), [abstract syntax tree](if_ast.mmd)
- Example of a repeat-until statement
  - [Program repeat_until.ptl](repeat_until.ptl), [abstract syntax tree](repeat_until_ast.mmd)

## Operators and Expressions

- Example of the logical NOT operator `!`
  - [Program lnot.ptl](lnot.ptl), [abstract syntax tree](lnot_ast.mmd)
- Example of the logical AND operator `&&`
  - [Program land.ptl](land.ptl), [abstract syntax tree](land_ast.mmd)
- Example of the logical OR operator `||`
  - [Program lor.ptl](lor.ptl), [abstract syntax tree](lor_ast.mmd)
- Example combining logical operators
  - [Program logical_operators.ptl](logical_operators.ptl), [abstract syntax tree](logical_operators_ast.mmd)
- Example of the remainder operator `%`
  - [Program mod.ptl](mod.ptl), [abstract syntax tree](mod_ast.mmd)
- Example of assignment to a non-assignable expression
  - [Program left-hand_side_error.ptl](left-hand_side_error.ptl), [abstract syntax tree](left-hand_side_error_ast.mmd)

## Optimization Level 1
- [Program opt1/expressions.ptl](opt1/expressions.ptl)
- Optimization level 0 (`-O0`): [abstract syntax tree](opt1/expressions_O0.ast.mmd), [compiled result opt1/expressions_O0.pta](opt1/expressions_O0.pta), [virtual machine execution trace opt1/expressions_O0.trace](opt1/expressions_O0.trace)
- Optimization level 1 (`-O1`): [abstract syntax tree](opt1/expressions_O1.ast.mmd), [compiled result opt1/expressions_O1.pta](opt1/expressions_O1.pta), [virtual machine execution trace opt1/expressions_O1.trace](opt1/expressions_O1.trace)

## Optimization Level 2
- [Program opt2/tail_recursion.ptl](opt2/tail_recursion.ptl)
- Optimization level 0 (`-O0`): [abstract syntax tree](opt2/tail_recursion_O0.ast.mmd), [compiled result opt2/tail_recursion_O0.pta](opt2/tail_recursion_O0.pta), [virtual machine execution trace opt2/tail_recursion_O0.trace](opt2/tail_recursion_O0.trace)
- Optimization level 2 (`-O2`): [abstract syntax tree](opt2/tail_recursion_O2.ast.mmd), [compiled result opt2/tail_recursion_O2.pta](opt2/tail_recursion_O2.pta), [virtual machine execution trace opt2/tail_recursion_O2.trace](opt2/tail_recursion_O2.trace)

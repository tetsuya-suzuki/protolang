**ASM_COMMENT:**

![ASM_COMMENT](diagram/ASM_COMMENT.svg)

```
ASM_COMMENT
         ::= ';' [^\r\n]*
```

referenced by:

* AsmCodeLine

**IDENT:**

![IDENT](diagram/IDENT.svg)

```
IDENT    ::= [_A-Za-z] [_A-Za-z0-9]*
```

referenced by:

* AsmCodeLine
* AsmDirective
* Declaration
* FunctionDefinition
* GlobalDeclaration
* Instruction
* ParameterList
* Primary

**NUMBER:**

![NUMBER](diagram/NUMBER.svg)

```
NUMBER   ::= [0-9]+
```

referenced by:

* Instruction
* Primary

**Program:**

![Program](diagram/Program.svg)

```
Program  ::= ( GlobalDeclaration | FunctionDefinition )*
```

**GlobalDeclaration:**

![GlobalDeclaration](diagram/GlobalDeclaration.svg)

```
GlobalDeclaration
         ::= 'var' IDENT '=' Expression ';'
```

referenced by:

* Program

**FunctionDefinition:**

![FunctionDefinition](diagram/FunctionDefinition.svg)

```
FunctionDefinition
         ::= 'function' IDENT '(' ParameterList? ')' ( Block | AsmBlock )
```

referenced by:

* Program

**ParameterList:**

![ParameterList](diagram/ParameterList.svg)

```
ParameterList
         ::= IDENT ( ',' IDENT )*
```

referenced by:

* FunctionDefinition

**Block:**

![Block](diagram/Block.svg)

```
Block    ::= '{' ( Declaration | Statement )* '}'
```

referenced by:

* FunctionDefinition
* IfStatement
* Statement
* WhileStatement

**AsmBlock:**

![AsmBlock](diagram/AsmBlock.svg)

```
AsmBlock ::= 'asm' '{' AsmLine* '}'
```

referenced by:

* FunctionDefinition

**AsmLine:**

![AsmLine](diagram/AsmLine.svg)

```
AsmLine  ::= AsmDirective
           | AsmCodeLine
```

referenced by:

* AsmBlock

**AsmDirective:**

![AsmDirective](diagram/AsmDirective.svg)

```
AsmDirective
         ::= '.function' IDENT
```

referenced by:

* AsmLine

**AsmCodeLine:**

![AsmCodeLine](diagram/AsmCodeLine.svg)

```
AsmCodeLine
         ::= ( IDENT ':' )? Instruction? ASM_COMMENT?
```

referenced by:

* AsmLine

**Instruction:**

![Instruction](diagram/Instruction.svg)

```
Instruction
         ::= 'IPUSH' '-'? NUMBER
           | 'POP'
           | 'DUP'
           | 'LOADG' NUMBER
           | 'STOREG' NUMBER
           | 'LOADA' NUMBER
           | 'STOREA' NUMBER
           | 'LOADL' NUMBER
           | 'STOREL' NUMBER
           | 'IADD'
           | 'ISUB'
           | 'IMUL'
           | 'IDIV'
           | 'INEG'
           | 'IMOD'
           | 'IEQ'
           | 'INE'
           | 'ILT'
           | 'ILE'
           | 'IGT'
           | 'IGE'
           | 'JMP' ( NUMBER | IDENT )
           | 'JPZ' ( NUMBER | IDENT )
           | 'CALL' ( NUMBER | IDENT )
           | 'ALLOC' NUMBER
           | 'RET'
           | 'CLEAN' NUMBER
           | 'CPRINT'
           | 'HALT'
```

referenced by:

* AsmCodeLine

**Declaration:**

![Declaration](diagram/Declaration.svg)

```
Declaration
         ::= 'var' IDENT '=' Expression ';'
```

referenced by:

* Block

**Statement:**

![Statement](diagram/Statement.svg)

```
Statement
         ::= Block
           | IfStatement
           | WhileStatement
           | ReturnStatement
           | ExpressionStatement
```

referenced by:

* Block

**IfStatement:**

![IfStatement](diagram/IfStatement.svg)

```
IfStatement
         ::= 'if' '(' Expression ')' Block 'else' ( Block | IfStatement )
```

referenced by:

* IfStatement
* Statement

**WhileStatement:**

![WhileStatement](diagram/WhileStatement.svg)

```
WhileStatement
         ::= 'while' '(' Expression ')' Block
```

referenced by:

* Statement

**ReturnStatement:**

![ReturnStatement](diagram/ReturnStatement.svg)

```
ReturnStatement
         ::= 'return' Expression ';'
```

referenced by:

* Statement

**ExpressionStatement:**

![ExpressionStatement](diagram/ExpressionStatement.svg)

```
ExpressionStatement
         ::= Expression ';'
```

referenced by:

* Statement

**Expression:**

![Expression](diagram/Expression.svg)

```
Expression
         ::= Assignment
```

referenced by:

* ArgumentList
* Declaration
* ExpressionStatement
* GlobalDeclaration
* IfStatement
* Primary
* ReturnStatement
* WhileStatement

**Assignment:**

![Assignment](diagram/Assignment.svg)

```
Assignment
         ::= Equality ( '=' Assignment )?
```

referenced by:

* Assignment
* Expression

**Equality:**

![Equality](diagram/Equality.svg)

```
Equality ::= Relational ( ( '==' | '!=' ) Relational )*
```

referenced by:

* Assignment

**Relational:**

![Relational](diagram/Relational.svg)

```
Relational
         ::= Additive ( ( '<' | '<=' | '>' | '>=' ) Additive )*
```

referenced by:

* Equality

**Additive:**

![Additive](diagram/Additive.svg)

```
Additive ::= Term ( ( '+' | '-' ) Term )*
```

referenced by:

* Relational

**Term:**

![Term](diagram/Term.svg)

```
Term     ::= Unary ( ( '*' | '/' ) Unary )*
```

referenced by:

* Additive

**Unary:**

![Unary](diagram/Unary.svg)

```
Unary    ::= '-' Unary
           | Primary
```

referenced by:

* Term
* Unary

**Primary:**

![Primary](diagram/Primary.svg)

```
Primary  ::= NUMBER
           | IDENT ( '(' ArgumentList? ')' )?
           | '(' Expression ')'
```

referenced by:

* Unary

**ArgumentList:**

![ArgumentList](diagram/ArgumentList.svg)

```
ArgumentList
         ::= Expression ( ',' Expression )*
```

referenced by:

* Primary

## 
![rr-2.6](diagram/rr-2.6.svg) <sup>generated by [RR - Railroad Diagram Generator][RR]</sup>

[RR]: https://www.bottlecaps.de/rr/ui
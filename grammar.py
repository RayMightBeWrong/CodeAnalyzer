grammar = """
start: code+
code: decl 
    | instr

code2: declvar ";"
     | instr

decl: declvar ";"
    | declfun

declvar: tipo? VAR "=" express
       | tipo VAR

declfun: "def" VAR "(" argsdef? ")" "{" content  "}"

argsdef: argdef ("," argdef)*
argdef: tipo? VAR

instr: if
     | whileloop
     | dowhile
     | forloop
     | switch
     | func ";"

express: func
    | string
    | array
    | list
    | tuple
    | elem
    | expnum
    | BOOL
    | condition
    | VAR

func: funcname "(" args? ")"

funcname: READ
        | WRITE
        | CONS
        | SNOC
        | HEAD
        | IN
        | TAIL
        | WORD



args: arg ("," arg)*
arg: express

return: "return" express ";"

if: "if" condition content elif* else?
elif: "elif" condition content 
else: "else" content 

whileloop: "while" condition content

dowhile: "do" content "while" condition

forloop: "for" VAR "in" range content

content: "{" (code2|return)* "}"

range: iterable
     | func
     | range_explicit 

range_explicit: "[" NUMBER ".." NUMBER "]"


switch: "switch" VAR case+ default*
case: "case" express content 
default: "default" content 

expnum: expnum LPOP term
    | term

term: term HPOP factor
    | factor

factor: NUMBER
    | VAR
    | "(" expnum ")"
    | expnum "^" expnum
    | func
    | elem

condition: "("? cond ")"?

cond: cond "or" cond2
    | cond2

cond2: cond2 "and" cond3
    | cond3

cond3: "not" cond4
    | cond4

cond4: "(" cond ")"
    | comp
    | BOOL

comp: express COP express


tipo: INT | BOOL | STRING | darray | LIST | TUPLE
darray: tipo "[" NUMBER? "]"


INT: "int"
BOOL: "true" | "false"
STRING: "string"
LIST: "list"
TUPLE: "tuple"

READ: "read"
WRITE: "write"
CONS: "cons"
SNOC: "snoc"
HEAD: "head"
IN: "in"
TAIL: "tail"

iterable: string
        | array
        | list
        | tuple

string: ESCAPED_STRING
array: "[" elems? "]"
list: "{" elems? "}"
tuple: "(" elems?")"

elems: express ("," express)*

elem: VAR "[" NUMBER "]"

VAR: WORD

WORD: (LETTER | "_") (LETTER | "_" | NUMBER)*

LPOP: "+"
    | "-"

HPOP: "*"
    | "/"
    | "%"

COP: ">"
    | "<"
    | "<="
    | ">="
    | "=="
    | "!="


%import common.ESCAPED_STRING
%import common.LETTER
%import common.NUMBER
%import common.WS
%ignore WS
"""

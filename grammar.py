grammar = """
start: code+
code: decl 
    | instr

decl: declvar ";"
    | declfun

declvar: tipo? VAR "=" express
       | tipo VAR

declfun: "def" VAR "(" argsdef? ")" "{" (code|return)+  "}"
       | tipo  VAR "(" argsdef? ")" "{" (code|return)+  "}"

argsdef: argdef ("," argdef)*
argdef: tipo? VAR

instr: if
     | while
     | dowhile
     | for
     | switch
     | func ";"

express: VAR
    | func
    | string
    | array
    | list
    | tuple
    | elem
    | expnum
    | BOOL
    | condition

func: funcname "(" args? ")"

funcname: "read"
        | "write"
        | "cons"
        | "snoc"
        | "head"
        | "in" 
        | "tail"
        | VAR

args: arg ("," arg)*
arg: express

return: "return" express ";"

if: "if" condition content elif* else?
elif: "elif" condition content 
else: "else" content 

while: "while" condition content

dowhile: "do" content "while" condition

for: "for" VAR "in" range content

content: "{" (code|return)* "}"

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

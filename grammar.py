grammar = """
start: componente+
componente: decl ";" 
    | instr

decl: tipo? VAR "=" express

instr: if
     | while
     | dowhile
     | for
     | switch
     | dfunc
     | func ";"
  
express: VAR
    | func
    | string
    | array
    | list
    | tuple
    | elem
    | expnum
    | bool


dfunc: "def" VAR "(" argsdef? ")" "{" componente+ return? "}"
    | "def" VAR "(" argsdef? ")" "{" componente* return "}"
func: funcname "(" args? ")"

funcname: "read"
        | "write"
        | "cons"
        | "snoc"
        | "head"
        | "in" 
        | "tail"
        | VAR

argsdef: argdef ("," argdef)*
argdef: VAR

args: arg ("," arg)*
arg: express

return: "return" express ";"

if: "if" condition content elif* else?
elif: "elif" condition content 
else: "else" content 

while: "while" condition content

dowhile: "do" content "while" condition

for: "for" VAR "in" range content

content: "{" componente* "}"

range: array
    | list
    | func
    | range_explicit 

range_explicit: "[" NUMBER ".." NUMBER "]"


switch: "switch" VAR case+ default*
case: "case" express content 
default: "default" content 

elems: express ("," express)*


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

cond3: "not" comp
    | comp
    | bool

comp: express COP express


tipo: "int" | "bool" | "string" | darray | "list" | "tuple"
darray: tipo "[" NUMBER "]"

LIST: "list"
TUPLO: "tuple"
string: ESCAPED_STRING
bool: "true" | "false"
array: "[" elems? "]"
list: "{" elems? "}"
tuple: "(" elems?")"

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
    | "=<"
    | ">="
    | "=="
    | "!="


%import common.ESCAPED_STRING
%import common.LETTER
%import common.NUMBER
%import common.WS
%ignore WS
"""

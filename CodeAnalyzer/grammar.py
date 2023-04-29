grammar = """
start: code+
code: decl 
    | instr

code2: declvar ";"
     | instr

decl: declvar ";"
    | declfun

declvar: tipo? VAR "=" express
       | elemdec "=" express
       | tipo VAR

declfun: "def" VAR "(" argsdef? ")" content

argsdef: argdef ("," argdef)*
argdef: tipo? VAR

instr: ifcond
     | whileloop
     | dowhile
     | forloop
     | switch
     | func ";"

express : bool
        | func
        | string
        | array
        | list
        | tuple
        | elem
        | express2
        | expnum
        | condition

express2.8: VAR

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

returnval: "return" express ";"

ifcond: "if" condition content elifcond* elsecond?
elifcond: "elif" condition content 
elsecond: "else" content 

whileloop: "while" condition content

dowhile: "do" content "while" condition

forloop: "for" VAR "in" range content

content: "{" (code2|returnval)* "}"

range: iterable
     | func
     | range_explicit
     | VAR

range_explicit: "[" SIGNED_NUMBER ".." SIGNED_NUMBER "]"

switch: "switch" VAR case+ default?
case: "case" express content
default: "default" content

expnum.4: expnum LPOP term
    | term

term: term HPOP factor
    | factor

factor: SIGNED_NUMBER
    | VAR
    | "(" expnum ")"
    | expnum "^" expnum
    | func
    | elem

condition.6: "("? cond ")"?

cond: cond OR cond2
    | cond2

cond2: cond2 AND cond3
    | cond3

cond3: NOT cond4
    | cond4

cond4: "(" cond ")"
    | bool
    | comp
    | VAR

bool.10: TRUE | FALSE


comp: express COP express


tipo: tipo "[" NUMBER "]" | tipo2
tipo2: INT | BOOL | STRING | LIST | TUPLE


BOOL: "bool"
INT: "int"
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
tuple: "(" express "," elems?")"


TRUE.10: "true"
FALSE.10: "false"
NOT.10: "not"
OR.10: "or"
AND.10: "and"

elems: express ("," express)*

elem: VAR "[" NUMBER "]"
elemdec: VAR "[" NUMBER "]"

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
%import common.SIGNED_NUMBER
%import common.NUMBER
%import common.WS
%ignore WS
"""

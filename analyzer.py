#!/usr/bin/python3

from lark import Lark,Token,Tree
from lark import Discard
from lark.visitors import Interpreter

from grammar import grammar
from html_creator import html_builder

"""
Table structure:

{
    declVar: {
        "a":{
            type: "string",
            value: "",
            context:""
        },
        ...
    }
    declFun: {
        "fib":{
            args:
            retType:
        }
    }
}
"""



class analyzer(Interpreter):
    def __init__(self) :
        self.declVar = {}
        self.declFun = {}
        pass
    def start(self,tree):
        self.visit_children(tree)
        
        
    def declvar(self,tree):
        index = 0
        # If the first children is a Tree, it means it is a "tipo"
        if isinstance(tree.children[index],Tree):
            tipo = self.visit(tree.children[index])[index]
            index+=1
        name = tree.children[index]
        index+=1
        value = self.visit_children(tree.children[index])
        value=value[0]
        print(value)
        self.declVar[name]={
            "tipo":tipo,
            "value":value
        }

    def express(self,tree):
        c = self.visit_children(tree)
        if len(c) == 1:
            return c[0]
        else:
            return c

    def expnum(self,tree):
        c = self.visit_children(tree)

        # If it is a term
        if len(c) == 1:
            return c[0]
        else:
            if c[1] == "+":
                if isinstance(c[0],int) and isinstance(c[2],int):
                    return c[0] + c[2]
            elif c[1] == "-":
                if isinstance(c[0],int) and isinstance(c[2],int):
                    return c[0] - c[2]
            return c

    def term(self,tree):
        c = self.visit_children(tree)
        # If it is a factor
        if len(c) == 1:
            return c[0]
        else:
            if c[1] == "*":
                if isinstance(c[0],int) and isinstance(c[2],int):
                    return c[0] * c[2]
            elif c[1] == "/":
                if isinstance(c[0],int) and isinstance(c[2],int):
                    return c[0] / c[2]

            elif c[1] == "%":
                if isinstance(c[0],int) and isinstance(c[2],int):
                    return c[0] % c[2]
            return c
    
    def factor(self,tree):
        c = self.visit_children(tree)
        if len(c) == 1:
            if isinstance(c[0],Token) and c[0].type=="NUMBER":
                return int(c[0].value)
            elif  isinstance(c[0],Token) and c[0].type=="VAR":
                return self.declVar[c[0].value]["value"]
            else:
                return c[0]
        else:
            if isinstance(c[0],int) and isinstance(c[1],int):
                return c[0] ** c[1]
            else:
                return c

                
        

    def condition(self,tree):
        c = self.visit_children(tree)
        return c[0]
    
    def cond(self,tree):
        c = self.visit_children(tree)
        if len(c)==1:
            return c[0]
        else:
            if isinstance(c[0],bool) and isinstance(c[1],bool):
                return c[0] or c[1]
            else: 
                return c

    def cond2(self,tree):
        c = self.visit_children(tree)
        if len(c)==1:
            return c[0]
        else:
            if isinstance(c[0],bool) and isinstance(c[1],bool):
                return c[0] and c[1]
            else: 
                return c


    def cond3(self,tree):
        c = self.visit_children(tree)
        if len(c)==1:
            return c[0]
        else:
            if isinstance(c[0],bool):
                return not c[1]
            else: 
                return c


    def cond4(self,tree):
        c = self.visit_children(tree)
        if isinstance(c[0],Token) and c[0].type=="BOOL": 
            return c[0].value=="True"
        else:
            return c[0]

            
    
    def comp(self,tree):
        c = self.visit_children(tree)
        if c[1] == ">":
            if isinstance(c[0],int) and isinstance(c[2],int):
                return c[0] > c[2]
        elif c[1] == "<":
            if isinstance(c[0],int) and isinstance(c[2],int):
                return c[0] < c[2]
        elif c[1] == "<=":
            if isinstance(c[0],int) and isinstance(c[2],int):    
                return c[0] <= c[2]
        elif c[1] == ">=":
            if isinstance(c[0],int) and isinstance(c[2],int):    
                return c[0] >= c[2]
        elif c[1] == "==":
            if isinstance(c[0],int) and isinstance(c[2],int):    
                return c[0] == c[2]
        elif c[1] == "!=":
            if isinstance(c[0],int) and isinstance(c[2],int):    
                return c[0] != c[2]
        return c
    

           

        
    
    def tipo(self,tree):
        x=self.visit_children(tree)
        return x


        


#Add argparser and flit maybe?
file = "int a = 3;int i =8 == a;"

p = Lark(grammar)
parse_tree = p.parse(file)
data = analyzer().visit(parse_tree)

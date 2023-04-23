#!/usr/bin/python3

from lark import Lark,Token,Tree
from lark import Discard
from lark.visitors import Interpreter

from grammar import grammar
from html_creator import html_builder


class analyzer(Interpreter):
    def __init__(self) :
        self.typeCount={"attr":0,"read":0,"write":0,"cond":0,"cycle":0}
        self.declVar = {"global":{}}
        self.declFun = {}
        self.unused  = {}
        self.redecl  = {}
        self.undecl  = {}
        self.warnings= {}
        self.errors  = {}
        self.context = "global"


    def start(self,tree):
        self.visit_children(tree)
        print(self.declVar)
        
    def declvar(self,tree):
        index = 0
        tipo=""
        
        # If the first children is a Tree, it means it is a "tipo"
        if isinstance(tree.children[index],Tree):
            tipo = self.visit(tree.children[index])
            index+=1

        name = tree.children[index].value
        index+=1
        value = self.visit(tree.children[index])
        
        #TODO: Check for redeclaration
        self.declVar[self.context][name]={
            "tipo":tipo,
            "value":value
        }
        self.unused[name]={
          "meta": vars(tree.meta)
        }

    def declfun(self,tree):
        name =tree.children[0].value
        args =tree.children[1]
        
        args= self.visit_children(args)
        
        self.declFun[name]={
            "args":args
        }
        self.context=name
        self.declVar[self.context]={}
        
        self.visit(tree.children[2])
        
        self.context="global"
        return tree

    def argsdef(self,tree):
        c = self.visit_children(tree)
        return c

    def argdef(self,tree):
        if isinstance(tree.children[0],Tree):
            return (self.visit(tree.children[0]),tree.children[1].value)
        else:
            return ("",tree.children[0].value)
            
    def tipo(self,tree):
        x=self.visit_children(tree)
        return x[0].value
        

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
    

  


#Add argparser and flit maybe?
file = "def ola(int i, string s, coisas){int i =0;}"

p = Lark(grammar,propagate_positions=True)
parse_tree = p.parse(file)
data = analyzer().visit(parse_tree)

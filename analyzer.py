#!/usr/bin/python3

from lark import Lark,Token,Tree
from lark import Discard
from lark.visitors import Interpreter

from grammar import grammar
from html_creator import html_builder


#TODO: Hierarqy of contexts
#DONE: TypeCount


class analyzer(Interpreter):
    def __init__(self) :
        self.typeCount={"attr":0,"read":0,"write":0,"cond":0,"cycle":0}
        self.declVar = {"global":{}}
        self.declFun = {}
        self.unused  = {}
        self.redecl  = {}
        self.undecl  = {}
        self.warnings= []
        self.errors  = []
        self.context = "global"


    def start(self,tree):
        self.visit_children(tree)
        print(vars(self))
        
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
        #TODO: Check for attr
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
        
        #Verify if it is a redeclaration of a fun, with same len of args
        if name in self.declFun:
          if len(self.declFun[name]["args"]) ==  len(args):
            self.errors.append({
              "errorMsg": "Redeclaration of function",
              "meta": vars(tree.meta) 
            })
          else:      
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
        if len(x)==1:
          return x[0].value
        else:
          return x
        
    def func(self,tree):
        #TODO: Verify args types
        c = self.visit_children(tree)
        return {"func":{"name":c[0].value,"args":c[1]}}

    def args(self,tree):
        c = self.visit_children(tree)
        return c
    
    def arg(self,tree):
        c = self.visit_children(tree)
        return c[0] if not isinstance(c[0],Token) else c[0].value
    
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
        self.typeCount["cond"]+=1
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
            return c[0].value=="true"
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
    
    def whileloop(self,tree):
      self.typeCount["cycle"]+=1
      c = self.visit_children(tree)
      return c
      
    def forloop(self,tree):
      #TODO: Change the scope of the for loop variable
      self.typeCount["cycle"]+=1
      c = self.visit_children(tree)
      return c

    def dowhile(self,tree):
      self.typeCount["cycle"]+=1
      c = self.visit_children(tree)
      return c
    
    def funcname(self,tree):
      c = self.visit_children(tree)
      if c[0].value == "write":
        self.typeCount["write"]+=1
      elif c[0].value == "read":
        self.typeCount["read"]+=1

      return c[0]

    def range_explicit(self,tree):
      if tree.children[0] > tree.children[1]:
        self.errors.append({
            "errorMsg": "Invalid range",
            "meta": vars(tree.meta)
        })

    #These dont work for some reason
    def BOOL(self,bool):
      return bool.value=="true"

    def NUMBER(self,number):
      return int(number.value)
    
    def VAR(sel,var):
      print(var)
      return var


#Add argparser and flit maybe?

p = Lark(grammar,propagate_positions=True)
while(True):
  file = input()
  try:
    parse_tree = p.parse(file)
    data = analyzer().visit(parse_tree)
  except:
    print("error in grammar")
  print("\n\n")

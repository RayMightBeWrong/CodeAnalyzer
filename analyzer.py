#!/usr/bin/python3

from lark import Lark,Token,Tree
from lark import Discard
from lark.visitors import Interpreter
from lark.exceptions import UnexpectedCharacters,UnexpectedEOF,UnexpectedInput,UnexpectedToken

from grammar import grammar
from html_creator import html_builder


#TODO: Hierarqy of contexts
#DONE: TypeCount


class analyzer(Interpreter):
    def __init__(self) :
        self.typeCount  = {"attr":0,"read":0,"write":0,"cond":0,"cycle":0}
        self.instrCount = 0

        self.contextTree= {"global":{}}    # Tree Structure for context evaluation
        self.declVar    = {"global":{}}    # Dictionary of variables based on context
        self.declFun    = {}               # Defined functions
        self.unused     = {}               # List of unused variable/function warnings
        self.undecl     = []               # List of undeclared variable/function
        self.warnings   = []               # General warnings list
        self.errors     = []               # List of errors
        self.contextStk    = ["global"]    # Current stack context


    def start(self,tree):
        self.visit_children(tree)
        print(vars(self))
        
    def declvar(self,tree):
        tipo=""
        ## 1. Recognize if it is a declaration, an assingment or booth
        decl=False
        assignment=False
        #If the first children is a Tree, it means it is a declaration
        if isinstance(tree.children[0],Tree):
            tipo = self.visit(tree.children[0])
            decl = True

        #If the last children is a tree then it is an assingment
        if isinstance(tree.children[-1],Tree):
            value = self.visit(tree.children[-1])
            assignment=True
        
        ##2. Check for context errors
        if not decl:
          name = tree.children[0].value
          search = False
          definedIn = ""
          for context in self.contextStk:
              if name in self.declFun[context]:
                definedIn = context
                search=True

          if not search:
            #If it wasnt found, declare it as undefined
            self.undecl[self.context[-1]+ name] = vars(tree.meta)
          else:
            # If it was, add its new value to the stack
            # TODO: If it as a type, we could check if is a valid assignment
            self.declVar[definedIn][name]["value"].append(value)
        
        else:
          name = tree.children[1].value
          if name in self.declVar[self.contextStk[-1]]:
              #Already defined
              self.errors.append({"errorMsg":"Already defined it current context", "meta":vars(tree.meta)})
          else:
              # Not defined nor used
              # TODO: If it as a type, we could check if is a valid assignment
              if assignment: self.declVar[self.contextStk[-1]] = {"type":tipo,"value":[value]}
              else: self.declVar[self.contextStk[-1]][name] = {"type":tipo,"value":[]}

              self.unused[self.contextStk[-1]+ name] = vars(tree.meta)

        return tree

    def declfun(self,tree):
        name =tree.children[0].value
        args =tree.children[1]
        args= self.visit_children(args)
        
        if name in self.declFun:
            self.errors.append({
                  "errorMsg": "Redeclaration of function",
                  "meta": vars(tree.meta) 
            })
            return tree
        else:     
            # Create contexts and func
            self.contextStk.append(name)
            self.contextTree["global"][name]={}
            
            self.declFun[name]={
                "args":args
            }
            #Visit code
            self.visit(tree.children[2])
            # Return to previous context
            self.contextStk.pop(-1)
          
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
        print(tree)
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

        return c
         
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

    def bool(self,tree):
      c = self.visit_children(tree)
      return c[0]=="true"

    # These dont work for some reason
    def NUMBER(self,number):
      print("OIII")
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
  except [UnexpectedToken,UnexpectedInput,UnexpectedEOF,UnexpectedCharacters] :
    print("error in grammar")
  print("\n\n")

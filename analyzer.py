#!/usr/bin/python3

from lark import Lark,Token,Tree
from lark import Discard
from lark.visitors import Interpreter
from lark.exceptions import UnexpectedCharacters,UnexpectedEOF,UnexpectedInput,UnexpectedToken

from grammar import grammar

#TODO: Marcação de utilização de variaveis
#TODO: Marcação de erros nas operações de calculo de expressoes
#TODO: Testes


def get_type(elem):
    res = ''
    for key in elem:
        res = key
    return res

def make_comparison(val1, cop, val2):
    if cop == '<':
        return val1 < val2
    elif cop == '>':
        return val1 > val2
    elif cop == '<=':
        return val1 <= val2
    elif cop == '>=':
        return val1 >= val2
    elif cop == '==':
        return val1 == val2
    elif cop == '!=':
        return val1 != val2


class analyzer(Interpreter):
    
    def __init__(self) :
        self.typeCount  = {"attr":0,"read":0,"write":0,"cond":0,"cycle":0}
        self.instrCount = 0
        self.contextTree= {"global":{}}    # Tree Structure for context evaluation
        self.declVar    = {"global":{}}    # Dictionary of variables based on context
        self.declFun    = {}               # Defined functions
        self.unused     = {}               # List of unused variable/function warnings
        self.undecl     = []               # List of undeclared variable/function
        self.notInit    = []               # List of not initialized variable/function
        self.warnings   = []               # General warnings list
        self.errors     = []               # List of errors
        self.contextStk = ["global"]       # Current stack context
    
    ## Auxiliary functions
    def vstContentAux(self,tree,contextN):
      node=self.contextTree
      for contxt in self.contextStk:
        node= node[contxt]
      node[contextN]={}
      self.contextStk.append(contextN)
      content =  self.visit(tree)
      self.contextStk.pop(-1)
      return content

    def useVariableAux(self,tree,var):
      definedIn = ""
      search=False
      for context in self.contextStk:
          if context in self.declVar and var in self.declVar[context]:
            definedIn = context
            search=True
      if not search:
          self.undecl.append(vars(tree.meta))
          return None,None
      else:
          value= self.declVar[definedIn][var]["value"][-1] if len(self.declVar[definedIn][var]["value"])>0 else None
          type= self.declVar[definedIn][var]["type"]
          if definedIn+var in self.unused: self.unused.pop(definedIn+var)
          if value==None:
             self.notInit.append(vars(tree.meta))
          return type,value
      
    ## RULES
    def start(self,tree):
        code =self.visit_children(tree)
       
        return{
           "code":code,
           "type_counter":self.typeCount, 
           "instr_counter":self.instrCount,
           "contextTree":self.contextTree,
           "vars" :self.declVar,
           "functions":self.declFun,
           "notInit":self.notInit,
           "unused": self.unused,
           "undecl":self.undecl,
           "warnings":self.warnings,
           "errors":self.errors,
           "nested":code
        }

    def code(self,tree):
       self.instrCount+=1
       c = self.visit_children(tree)[0]
       return c[0]
    
    def code2(self,tree):
       self.instrCount+=1
       c = self.visit_children(tree)
       return c[0]
       
    def instr(self,tree):
       c = self.visit_children(tree)
       return c[0]

    def declvar(self,tree):
        tipo=""
        value=''
        ## 1. Recognize if it is a declaration, an assingment or booth
        decl=False
        value=[]
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
              if name in self.declVar[context]:
                definedIn = context
                search=True

          if not search:
            #If it wasnt found, declare it as undefined
            self.undecl.append(vars(tree.meta))
          else:
            # If it was, add its new value to the stack
            # TODO: If it as a type, we could check if is a valid assignment
            self.declVar[definedIn][name]["value"].append(value)
            if assignment: self.typeCount["attr"]+=1
        
        else:
          name = tree.children[1].value

          if self.contextStk[-1] in self.declVar and  name in self.declVar[self.contextStk[-1]]:
              #Already defined
              self.errors.append({"errorMsg":"Already defined it current context", "meta":vars(tree.meta)})
          else:
              # Not defined nor used
              # TODO: If it as a type, we could check if is a valid assignment
              if not self.contextStk[-1] in self.declVar: self.declVar[self.contextStk[-1]]={}
              
              if assignment: self.declVar[self.contextStk[-1]][name] = {"type":tipo,"value":[value]}
              else: self.declVar[self.contextStk[-1]][name] = {"type":tipo,"value":value}
            
              if assignment: self.typeCount["attr"]+=1

              self.unused[self.contextStk[-1]+ name] = vars(tree.meta)

        return {"dclVar":{"decl":decl,"assign":assignment,"type":tipo,"value":value}}

    def declfun(self,tree):
        name =tree.children[0].value
        args =tree.children[1]
        args= self.visit(args)
        
        if name in self.declFun:
            self.errors.append({
                  "errorMsg": "Redeclaration of function",
                  "meta": vars(tree.meta)
            })
        else:     
            for arg in args:
               self.declVar[name]={}
               self.declVar[name][arg[1]]= {"type":arg[0],"value":[]}

            
            self.declFun[name]={
                "args":args
            }

            content = self.vstContentAux(tree.children[2],name)
          
        return {"dclFun":{"name":name,"args":args,"content":content}}
       
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
        if len(x)==1 and isinstance(x[0],Token) :
          return x[0].value
        else:
          return x[0]
        
    def func(self,tree):
        #TODO: Verify args types
        func= self.visit(tree.children[0])
        if func.type=="WORD":
           if not func.value in self.declFun:
              self.warnings.append({"errorMsg":"Function not defined!","meta":vars(tree.meta)})
              return None
        elif func.type=="READ":self.typeCount["read"]+=1
        elif func.type=="WRITE":self.typeCount["write"]+=1
        
        c = self.visit(tree.children[1])
        return {"func":{"name":func.value,"args":c[0]}}

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
                type,value=self.useVariableAux(tree,c[0].value)
                if value== None:
                   return c[0]
                else: return self.declVar[value]["value"]
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
                return {"or":(c[0],c[1])}

    def cond2(self,tree):
        
        c = self.visit_children(tree)
        if len(c)==1:
            return c[0]
        else:
            if isinstance(c[0],bool) and isinstance(c[1],bool):
                return c[0] and c[1]
            else: 
                return {"and":(c[0],c[1])}

    def cond3(self,tree):
        
        c = self.visit_children(tree)
        if len(c)==1:
            return c[0]
        else:
            if c[0].value == 'not' and isinstance(c[1],bool):
                return not c[1]
            else: 
                return {"not":c[0]}

    def cond4(self,tree):
        
        c = self.visit_children(tree)
        return c[0]
         

    def comp(self,tree):
        
        c = self.visit_children(tree)

        if len(c) == 3:
            type1 = type(c[0])
            type2 = type(c[2])
            if type1 == type({}) and type2 == type({}):
                type1 = get_type(c[0])
                type2 = get_type(c[2])
                if type1 == type2:
                    return make_comparison(c[0][type1], c[1], c[2][type2])
                else:
                    self.errors.append({"errorMsg":"Comparing values of different types", "meta":vars(tree.meta)})
            elif type1 == type2:
                return make_comparison(c[0], c[1], c[2])
            else:
                self.errors.append({"errorMsg":"Comparing values of different types", "meta":vars(tree.meta)})
        else:
            return c
    

    def whileloop(self,tree):
      self.typeCount["cycle"]+=1
      condition = self.visit(tree.children[0])
      content = self.vstContentAux(tree.children[1], "wloop"+str(self.typeCount["cycle"]))
      return {"wloop"+str(self.typeCount["cycle"]):{"cond":condition, "content":content}}
      
    def forloop(self,tree):
      self.typeCount["cycle"]+=1
      iterator = self.visit(tree.children[0])

      #TODO: range treatment
      range = self.visit(tree.children[1])

      self.declVar["floop"+str(self.typeCount["cycle"])]={}
      self.declVar["floop"+str(self.typeCount["cycle"])][iterator]= {"type":"iterator","value":range}

      content = self.vstContentAux(tree.children[2],"floop"+str(self.typeCount["cycle"]))
      
      return {"floop"+str(self.typeCount["cycle"]):{"range":range, "content":content}}
    
    def range(self,tree):
      #Its a var and it needs to be type checked
      if isinstance(tree.children[0],Token):
         iterable = tree.children[0].value
         type,value=self.useVariableAux(tree,iterable)
        #TODO: typecheck
      else:
         return self.visit(tree.children[0])[0]
      
    def range_explicit(self,tree):
      if tree.children[0].value > tree.children[1].value:
        self.errors.append({
            "errorMsg": "Invalid range",
            "meta": vars(tree.meta)
        })
      return {"range_explicit":{"min":tree.children[0].value,"max":tree.children[1].value,}}
     
    def iterable(self,tree):
      c = self.visit(tree.children[0])
      return {"iterableObj":{"value" :c[0]}}

    def string(self,tree):
      return {"string":tree.children[0].value}

    def array(self,tree):
      c = self.visit(tree.children[0])
      return {"array":c}
      
    def list(self,tree):
      c = self.visit(tree.children[0])
      return {"list":c}

    def tuple(self,tree):
      c = self.visit(tree.children[0])
      return {"tuple":c}
    
    def elems(self,tree):
        exps=[]
        for i in range(len(tree.children)):
          exps.append(self.visit(tree.children[i]))
        return exps
  
    def darray(self,tree):
       c = self.visit_children(tree)
       return c
           
    def dowhile(self,tree):
      self.typeCount["cycle"]+=1
      condition = self.visit(tree.children[1])
      content = self.vstContentAux(tree.children[0],"dwloop"+str(self.typeCount["cycle"]))

      return {"dwloop"+str(self.typeCount["cycle"]):{"cond":condition, "content":content}}
    
    def ifcond(self,tree):
      condition = self.visit(tree.children[0])
      content = self.vstContentAux(tree.children[1],"if"+str(self.typeCount["cond"]))
      elses=[]
      for i in range(2,len(tree.children)):
           elses.append(self.visit(tree.children[i]))
      
      return {"if":{"cond":condition, "content":content, "elses":elses}}
    
    def elifcond(self,tree):
      condition = self.visit(tree.children[0])
      content = self.vstContentAux(tree.children[1],"elif"+str(self.typeCount["cond"]))
      return {"elif":{"cond":condition, "content":content}}

    def elsecond(self,tree):
      content = self.vstContentAux(tree.children[0],"else"+str(self.typeCount["cond"]))
      return {"else":{"content":content}}
    
    def funcname(self,tree):

      return tree.children[0]

    
    def switch(self,tree):
      var = tree.children[0].value
      type,value = self.useVariableAux(tree,tree.children[0].value)

      cases=[]
      for i in range(1,len(tree.children)-1):
        cases.append(self.visit(tree.children[i]))

      default={}
      if (tree.children[-1].data == "case"):
         
         cases.append(self.visit(tree.children[-1]))
      else:
         default=self.visit(tree.children[-1])
      
      return {"switch":{"var":var,"cases":cases,"default":default}}       

    def case(self,tree):
      expression = self.visit(tree.children[0])
      content= self.vstContentAux(tree.children[1],"casecond"+str(self.typeCount["cond"]))
      return {"case":{"expression":expression, "content":content}}
    
    def default(self,tree):
      content= self.vstContentAux(tree.children[0],"defcond"+str(self.typeCount["cond"]))
      return {"default":{"content":content}}
    
    def bool(self,tree):
      c = self.visit_children(tree)
      return c[0]=="true"

    def returnval(self,tree):
       
       if self.contextStk[-1]== "global":
          self.errors.append({"errorMsg":"Return in the global context", "meta":vars(tree.meta)})
       else:
          self.instrCount+=1 
          c = self.visit(tree.children[0])
          return {"return": c}

#Add argparser and flit maybe?

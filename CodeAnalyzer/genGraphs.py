import graphviz

contexts = {}

def genCFGAux(code,begin,end,dot):
    previous= [begin]
    next = begin
    edges = 0
    for statement in code:
        if "dclVar" in statement:
            next+=1
            id = next
            if statement["dclVar"]["decl"]:
                text = "decl: "
            else:
                text = "assign: "
            dot.node(str(id),text+statement["dclVar"]["name"])
            for i in previous:
                dot.edge(str(i),str(id))
                edges+=1
            previous=[id]
        elif list(statement.keys())[0] in ["floop","wloop","dwloop"]:
            name = list(statement.keys())[0]
            next+=1
            id = next
            dot.node(str(id),name)
            for i in previous:
                dot.edge(str(i),str(id))
                edges+=1
            previous=[id]
            next,addedEdges,_ = genCFGAux(statement[name]["content"],id,id,dot)
            edges+=addedEdges
        elif "if" in statement:
            next+=1
            id = next
            dot.node(str(id),"if",shape="diamond")
            for i in previous:
                dot.edge(str(i),str(id))
                edges+=1
            next,addedEdges,previous3 = genCFGAux(statement["if"]["content"],id,-1,dot)
            edges+=addedEdges
            previous=[]
            previous2=id
            if len(statement["if"]["elses"]) == 0:
                previous.append(id)
            for elseSt in statement["if"]["elses"]:
                if "elif" in elseSt:
                    next+=1
                    id = next
                    dot.node(str(id),"elif",shape="diamond")
                    dot.edge(str(previous2),str(id))
                    edges+=1
                    next,addedEdges,previous = genCFGAux(elseSt["elif"]["content"],id,-1,dot)
                    edges+=addedEdges
                    previous.append(id)
                    previous2=next
                elif "else" in elseSt:
                    next+=1
                    id = next
                    dot.node(str(id),"else",shape="diamond")
                    dot.edge(str(previous2),str(id))
                    edges+=1
                    next,addedEdges,previous = genCFGAux(elseSt["else"]["content"],id,-1,dot)
                    edges+=addedEdges
            previous.extend(previous3)
        elif "func" in statement:
            next+=1
            id = next
            dot.node(str(id),"func:"+statement["func"]["name"])
            for i in previous:
                dot.edge(str(i),str(id))
                edges+=1
            previous=[id]
        elif "return" in statement:
            next+=1
            id = next
            dot.node(str(id),"return")
            for i in previous:
                dot.edge(str(i),str(id))
                edges+=1
            previous=[id]
        elif "dclFun" in statement:
           genCFG(statement["dclFun"]["content"],statement["dclFun"]["name"])

            

    if end!=-1:
        for i in previous:
            dot.edge(str(i),str(end))
            edges+=1
        previous=[]
    
    return next,edges,previous

                    

def genCFG(code,output):
    dot = graphviz.Digraph()
    dot.node(str(0),"begin",)
    dot.node(str(-2),"end")
    nodes,edges,_ = genCFGAux(code,0,-2,dot)
    dot.render('CFGraphs/'+output, format="png")

    contexts[output]={"nodes":nodes+2,"edges":edges}

def genCFGs(code):
    global contexts
    genCFG(code,"global")
    return contexts



def genSDGAux(code,begin,end,dot):
    next = begin
    edges = 0

    for statement in code:
        if "dclVar" in statement:
            next+=1
            id = next
            dot.node(str(id),"declVar")
            dot.edge(str(begin),str(id))
        elif list(statement.keys())[0] in ["floop","wloop","dwloop"]:
            name = list(statement.keys())[0]
            next+=1
            id = next
            dot.node(str(id), name, shape="diamond")
            dot.edge(str(begin),str(id))
            dot.edge(str(id),str(id))
            genSDGAux(statement[name]['content'],id,end,dot)
        elif "if" in statement:
            name = list(statement.keys())[0]
            next+=1
            id_if = next
            id = next
            dot.node(str(id_if), name, shape="diamond")
            dot.edge(str(begin),str(id))
            next+=1
            id = next
            dot.node(str(id),'then', shape="diamond")
            dot.edge(str(id_if),str(id))
            next, addedEdges = genSDGAux(statement[name]['content'], id, end, dot)
            for elseSt in statement["if"]["elses"]:
                if 'else' in elseSt:
                    next+=1
                    id = next
                    dot.node(str(id),'else', shape="diamond")
                    dot.edge(str(id_if),str(id))
                    next, addedEdges = genSDGAux(elseSt["else"]["content"], id, -1, dot)
                elif 'elif' in elseSt:
                    next+=1
                    id = next
                    dot.node(str(id),'elif', shape="diamond")
                    dot.edge(str(id_if),str(id))
                    next, addedEdges = genSDGAux(elseSt["elif"]["content"], id, -1, dot)
        elif "func" in statement:
            next+=1
            id = next
            dot.node(str(id),"func:"+statement["func"]["name"])
            dot.edge(str(begin),str(id))
        elif "dclFun" in statement:
           genSDG(statement["dclFun"]["content"], statement["dclFun"]["name"], True)
        elif "return" in statement:
            next+=1
            id = next
            dot.node(str(id),"return")
            dot.edge(str(begin),str(id))

    return next,edges

def genSDG(code, output, func):
    dot = graphviz.Digraph()
    if func:
        dot.node(str(0),"entry " + output, shape="trapezium")
    else:
        dot.node(str(0),"entry begin" , shape="trapezium")
    nodes,edges = genSDGAux(code,0,-2,dot)
    dot.render('SDGraphs/'+output, format="png")
    contexts[output]={"nodes":0,"edges":0}

def genSDGs(code):
    global contexts
    contexts = {}
    for val in code:
        print('=============================')
        print(val, end='\n\n')
    genSDG(code, "global", True)
    return contexts

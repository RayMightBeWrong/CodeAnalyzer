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
            dot.node(str(id),"declVar")
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
            next,addedEdges = genCFGAux(statement[name]["content"],id,id,dot)
            edges+=addedEdges
        elif "if" in statement:
            next+=1
            id = next
            dot.node(str(id),"if",shape="diamond")
            for i in previous:
                dot.edge(str(i),str(id))
                edges+=1
            next,addedEdges = genCFGAux(statement["if"]["content"],id,-1,dot)
            edges+=addedEdges
            previous=[next]
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
                    next,addedEdges = genCFGAux(elseSt["elif"]["content"],id,-1,dot)
                    edges+=addedEdges
                    previous.append(next)
                    previous.append(id)
                    previous2=next
                elif "else" in elseSt:
                    next+=1
                    id = next
                    dot.node(str(id),"else",shape="diamond")
                    dot.edge(str(previous2),str(id))
                    edges+=1
                    next,addedEdges = genCFGAux(elseSt["else"]["content"],id,-1,dot)
                    edges+=addedEdges
                    previous.append(next)
                    previous.append(id)
        elif "func" in statement:
            next+=1
            id = next
            dot.node(str(id),"func:"+statement["func"]["name"])
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

    return next,edges

                    

def genCFG(code,output):
    dot = graphviz.Digraph()
    dot.node(str(0),"begin",)
    dot.node(str(-2),"end")
    nodes,edges = genCFGAux(code,0,-2,dot)
    dot.render('CFGraphs/'+output, format="png")

    contexts[output]={"nodes":nodes+2,"edges":edges}

def genCFGs(code):
    global contexts
    genCFG(code,"global")
    return contexts
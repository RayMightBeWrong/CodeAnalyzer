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
        elif "switch" in statement:
            next+=1
            id = next
            dot.node(str(id),"switch",shape="diamond")
            for i in previous:
                dot.edge(str(i),str(id))
                edges+=1
            previous=[]
            previous2 = id
            if statement["switch"]["default"] == {}:
                previous.append(id)

            
            for case in statement["switch"]["cases"]:
                next+=1
                id = next
                dot.node(str(id),"case",shape="diamond")
                dot.edge(str(previous2),str(id))
                edges+=1
                next,addedEdges,previous3 = genCFGAux(case["case"]["content"],id,-1,dot)
                edges+=addedEdges
                previous.extend(previous3)

            if statement["switch"]["default"] != {}:
                next+=1
                id = next
                dot.node(str(id),"default",shape="diamond")
                dot.edge(str(previous2),str(id))
                edges+=1
                next,addedEdges,previous3 = genCFGAux(statement["switch"]["default"]["default"]["content"],id,-1,dot)
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
import graphviz

def genCFGAux(code,begin,end,dot):
    previous= [begin]
    next = begin
    for statement in code:
        if "dclVar" in statement:
            next+=1
            id = next
            dot.node(str(id),"declVar")
            for i in previous:
                dot.edge(str(i),str(id))
            previous=[id]
        elif list(statement.keys())[0] in ["floop","wloop","dwloop"]:
            name = list(statement.keys())[0]
            next+=1
            id = next
            dot.node(str(id),name)
            for i in previous:
                dot.edge(str(i),str(id))
            previous=[id]
            next = genCFGAux(statement[name]["content"],id,id,dot)
        elif "if" in statement:
            next+=1
            id = next
            dot.node(str(id),"if",shape="diamond")
            for i in previous:
                dot.edge(str(i),str(id))
            next = genCFGAux(statement["if"]["content"],id,-1,dot)
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
                    next = genCFGAux(elseSt["elif"]["content"],id,-1,dot)
                    previous.append(next)
                    previous.append(id)
                    previous2=next
                elif "else" in elseSt:
                    next+=1
                    id = next
                    dot.node(str(id),"else",shape="diamond")
                    dot.edge(str(previous2),str(id))
                    next = genCFGAux(elseSt["else"]["content"],id,-1,dot)
                    previous.append(next)
                    previous.append(id)
        elif "func" in statement:
            next+=1
            id = next
            dot.node(str(id),"func")
            for i in previous:
                dot.edge(str(i),str(id))
            previous=[id]
        elif "dclFun" in statement:
            genCFG(statement["dclFun"]["content"],statement["dclFun"]["name"])

    if end!=-1:
        for i in previous:
            dot.edge(str(i),str(end))

    return next

                    

def genCFG(code,output):
    dot = graphviz.Digraph()
    dot.node(str(0),"begin",)
    dot.node(str(-2),"end")
    genCFGAux(code,0,-2,dot)
    print(dot.source)
    dot.render('doctest-output/'+output, format="png")
    
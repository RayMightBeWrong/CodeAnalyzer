from grammar import grammar
from lark import Lark
from analyzer import analyzer
import json

def html_complete(fname,body):
    return '''
<!DOCTYPE html>
<html>
    <style>
        /* Remove default bullets */
        ul, #myUL {{
        list-style-type: none;
        }}

        /* Remove margins and padding from the parent ul */
        #myUL {{
        margin: 0;
        padding: 0;
        }}

        /* Style the caret/arrow */
        .caret {{
        cursor: pointer;
        user-select: none; /* Prevent text selection */
        }}

        /* Create the caret/arrow with a unicode, and style it */
        .caret::before {{
        content: "\\25B6";
        color: black;
        display: inline-block;
        margin-right: 6px;
        }}

        /* Rotate the caret/arrow icon when clicked on (using JavaScript) */
        .caret-down::before {{
        transform: rotate(90deg);
        }}

        /* Hide the nested list */
        .nested {{
        display: none;
        }}

        /* Show the nested list when the user clicks on the caret/arrow (with JavaScript) */
        .active {{
        display: block;
        }} 

        .error {{position: relative;
        display: inline-block;
        border-bottom: 1px dotted black;
        color: red;
        }}
        .warning{{position: relative;
        display: inline-block;
        border-bottom: 1px dotted black;
        color: orange;
        }}
        .code-block{{
            border: 1px solid grey; 
            background-color: #f2f2f2;
            margin: 10px
        }}
        .code {{
            position: relative;
            display: inline-block;
            margin-left: 10px
        }}
        .warning .errortext  {{
            visibility: hidden;
            width: 350px;
            background-color: #555;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 5px 0;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -40px;
            opacity: 0;
            transition: opacity 0.3s;
        }}
        .error .errortext  {{
        visibility: hidden;
        width: 350px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px 0;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -40px;
        opacity: 0;
        transition: opacity 0.3s;
        }}
        .error .errortext::after {{
        content: "";
        position: absolute;
        top: 100%;
        left: 20%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #555 transparent transparent transparent;
        }}
        .error:hover .errortext {{
        visibility: visible;
        opacity: 1;
        }}


        .warning .errortext::after {{
        content: "";
        position: absolute;
        top: 100%;
        left: 20%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #555 transparent transparent transparent;
        }}
        .warning:hover .errortext {{
        visibility: visible;
        opacity: 1;
        }}

        </style>
    <head>
        <title> Code Analyzer Report </title>
        <meta charset="utf-8"/>
    </head>
    <body>
        <h1> Code Analyzer Report: {fname}</h1>
'''.format(fname=fname)+body+"""<script>
    var toggler = document.getElementsByClassName("caret");
var i;

for (i = 0; i < toggler.length; i++) {
  toggler[i].addEventListener("click", function() {
    this.parentElement.querySelector(".nested").classList.toggle("active");
    this.classList.toggle("caret-down");
  });
} 
</script>"""+"""</body>
</html>"""

def html_variables(variables):
    html="""
        <h3>Variables Used</h3>
        <table style="border-collapse: collapse; width: 50%; height: 81px;" border="1">
            <thead>
                <tr>
                    <th>Variable Name</th>
                    <th>Type</th>
                    <th>Context</th>
                    <th>Values</th>
                </tr>
            </thead>
            <tbody>
                {tbody}
            </tbody>
        </table>
    """
    tbody=""
    for var in variables:
        tbody+="""
            <tr>
                <td>{name}</th>
                <td>{type}</th>
                <td>{contxt}</th>
                <td>{values}</th>
            </tr>
        """.format(name=var["name"],type=var["type"],contxt=var["context"],values=var["values"])
    return html.format(tbody=tbody)


def prepareVars(declVar:dict):
    variables=[]
    for contxt in declVar.keys():
        for name in declVar[contxt].keys():
            variables.append({"name":name,"context":contxt,"type":declVar[contxt][name]["type"],"values":declVar[contxt][name]["value"]})
    return variables

def html_instruc(counter,instructions):
    html="""
            <h3> Intructions Used</h3>
            <p> In total, there were {counter} instructions used!
            <p> In the table bellow, we can see these instructions organized by type:</p>
            <table style="border-collapse: collapse; width: 10%; height: 81px;" border="1">
            <thead>
                <tr>
                    <th>Type</th>
                    <th>Number</th>
                </tr>
            </thead>
            <tbody>
                {tbody}
            </tbody>
        </table>
    """
    tbody=""
    for type in instructions.keys():
        tbody+="""
            <tr>
                <td>{type}</td>
                <td>{number}</td>
            </tr>
        """.format(type=type,number=instructions[type])
    return html.format(counter=counter,tbody=tbody)

def prepareLabels(data):
    labels={}
    unused = data["unused"]
    for key in unused.keys():
        line  =unused[key]["line"]
        start =unused[key]["column"]
        end =unused[key]["end_column"]
        
        line-=1
        start-=1
        end-=1

        if not line in labels: 
            labels[line] = {}

        if not start in labels[line]: 
            labels[line][start]=[]

        labels[line][start].append({"msg":"Variable initialized but never used","level":"warning","end":end})
    
    for var in data["notInit"]:
        line  =var["line"]
        start =var["column"]
        end   =var["end_column"]

        line-=1
        start-=1
        end-=1

        if not line in labels: 
            labels[line] = {}

        if not start in labels[line]: 
            labels[line][start]=[]

        labels[line][start].append({"msg":"Value for variable never assigned","level":"warning","end":end})
    
    for var in data["undecl"]:
        line  =var["line"]
        start =var["column"]
        end   =var["end_column"]

        line-=1
        start-=1
        end-=1

        if not line in labels: 
            labels[line] = {}

        if not start in labels[line]: 
            labels[line][start]=[]

        labels[line][start].append({"msg":"Undeclared variable","level":"error","end":end})
    
    for warn in data["warnings"]:
        line  =warn["meta"]["line"]
        start =warn["meta"]["column"]
        end   =warn["meta"]["end_column"]

        line-=1
        start-=1
        end-=1

        if not line in labels: 
            labels[line] = {}

        if not start in labels[line]: 
            labels[line][start]=[]

        labels[line][start].append({"msg":warn["errorMsg"],"level":"warning","end":end})
    
    for error in data["errors"]:
        line  =error["meta"]["line"]
        start =error["meta"]["column"]
        end   =error["meta"]["end_column"]

        line-=1
        start-=1
        end-=1

        if not line in labels: 
            labels[line] = {}

        if not start in labels[line]: 
            labels[line][start]=[]

        labels[line][start].append({"msg":error["errorMsg"],"level":"error","end":end})
    
    return labels

def html_code(code,labels):
    html="""<h3>Annotated Code</h3>
    <pre><div class="code-block"><code>\n"""
    lines = code.split('\n')
    
    for line_num, line in enumerate(lines):
        html+='<p style="margin-top: -20px;" class="code">'
        if line_num in labels:
            endin ={}
            [].reverse
            for n,char in enumerate(line):
                if n in endin:
                    endin[n].reverse()
                    for end in endin[n]:
                        html+='<span class="errortext">'+ end["level"] +":" + end["msg"] + "</span></div>"      
                    endin.pop(n)
                
                if n in labels[line_num]:
                     for each in labels[line_num][n]:
                        html+='<div class="{level}">'.format(level=each["level"])
                        if not each["end"] in endin: endin[each["end"]]=[each]
                        else:endin[each["end"]].append(each)
                html+=char
            
        else: html+=line
        html+='</p>\n'
        
    html+="</code></div></pre>"
    return html

def context_builder(context,tree,instr):
    indexCntxt=0
    build={}
    for i in instr:
        if i != None:
            name = list(i.keys())[0]
            if name=="if":
                build[name+"_" + list(tree[context].keys())[indexCntxt]]=context_builder(list(tree[context].keys())[indexCntxt],tree[context],i[name]["content"])
                remove_nested="elif_" +list(tree[context].keys())[indexCntxt]
                remove_nested2="else_" +list(tree[context].keys())[indexCntxt]
                indexCntxt+=1
                for elcond in i[name]["elses"]:
                    if elcond == i[name]["elses"][-1]:
                        build["elif_" + list(tree[context].keys())[indexCntxt]]=context_builder(context,tree,[elcond])[remove_nested2]
                    else:
                        build["elif_" + list(tree[context].keys())[indexCntxt]]=context_builder(context,tree,[elcond])[remove_nested]
                    
                    indexCntxt+=1

            elif name=="switch":
                build[name+"_" + list(tree[context].keys())[indexCntxt]]=context_builder(list(tree[context].keys())[indexCntxt],tree[context],i[name]["cases"])
                build[name+"_" + list(tree[context].keys())[indexCntxt]]=context_builder(context,tree,[i[name]["default"]])
                indexCntxt+=1
            
            elif not isinstance(i[name],dict):
                if not name in build: build[name]=0
                build[name] += 1

            elif "content" in i[name]:
                
                build[name+"_" + list(tree[context].keys())[indexCntxt]]=context_builder(list(tree[context].keys())[indexCntxt],tree[context],i[name]["content"])
                indexCntxt+=1
            else:
                if not name in build: build[name]=0
                build[name] += 1
            
    return build

def html_context(context):
    html=""
    for i in context.keys():
        if isinstance(context[i],int):
            html+="<li>" + i + ":" + str(context[i]) +"</li>"
        else:
            html+='<li><span class="caret">'+ i +'</span>\n'
            html+='<ul class="nested">\n'
            html+=html_context(context[i])
            html+="</ul></li>"
    return html

def html_nested(tree,nested):
    html="""<h3>Instruction Counter based on Context</h3>"""
    html+='<ul id="myUL">\n'
    html+=html_context({"global": context_builder("global",tree,nested)})
    html+="</ul>"

    return html


input_file="test2.code"
codef = open(input_file,"r")
code = codef.read()

p = Lark(grammar,propagate_positions=True)
parse_tree = p.parse(code)
data = analyzer().visit(parse_tree)
f = open("test.html","w")
body =html_variables(prepareVars(data["vars"]))
body+=html_instruc(data["instr_counter"],data["type_counter"])
body+=html_nested(data["contextTree"],data["nested"])
body+=html_code(code,prepareLabels(data))



f.write(
    html_complete(input_file,body)
        )

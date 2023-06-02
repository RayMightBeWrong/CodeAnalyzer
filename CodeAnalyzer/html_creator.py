import json
import os

def html_complete(fname,body):
    return '''
<!DOCTYPE html>
<html>
    <link rel="stylesheet" href="https://unpkg.com/spectre.css/dist/spectre.min.css">
    <link rel="stylesheet" href="https://unpkg.com/spectre.css/dist/spectre-exp.min.css">
    <link rel="stylesheet" href="https://unpkg.com/spectre.css/dist/spectre-icons.min.css">
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
        overflow: visible;
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
            margin-left: 10px
        }}
        .warning .errortext  {{
            visibility: hidden;
            width: auto;
            background-color: #555;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            opacity: 0;
            transition: opacity 0.3s;
        }}
        .error .errortext  {{
        visibility: hidden;
        width: auto;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        opacity: 0;
        transition: opacity 0.3s;
        }}


        .error:hover .errortext {{
        visibility: visible;
        opacity: 1;
        }}


        
        .warning:hover .errortext {{
        visibility: visible;
        opacity: 1;
        }}

        .collapsible {{
            color: #444;
            cursor: pointer;
            padding: 18px;
            width: 100%;
            border: none;
            text-align: left;
            outline: none;
            font-size: 15px;
            background-color:  #f1f1f1;
            }}


        /* Style the collapsible content. Note: hidden by default */
        .content {{
        padding: 0 18px;
        display: none;
        overflow: hidden;
        background-color: #f1f1f1;
        }}

        </style>
    <head>
        <title> Code Analyzer Report </title>
        <meta charset="utf-8"/>
    </head>
    <body style="margin: 20px;">
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

var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
}
</script>"""+"""
<script>
var cf = 1;
var sd = 1;
showDivsCF(cf);
showDivsSD(sd);

function plusDivsCF(n) {
  showDivsCF(cf += n);
}

function plusDivsSD(n) {
  showDivsSD(sd += n);
}

function showDivsCF(n) {
  var i;
  var x = document.getElementsByClassName("CFGraphs");
  if (n > x.length) {cf = 1}
  if (n < 1) {cf = x.length} ;
  for (i = 0; i < x.length; i++) {
    x[i].style.display = "none";
  }
  x[cf-1].style.display = "block";
}

function showDivsSD(n) {
  var i;
  var x = document.getElementsByClassName("SDGraphs");
  if (n > x.length) {sd = 1}
  if (n < 1) {sd = x.length} ;
  for (i = 0; i < x.length; i++) {
    x[i].style.display = "none";
  }
  x[sd-1].style.display = "block";
}

</script>
"""+"""</body>
</html>"""

def html_func(functions):
    html="""

        <table style="border-collapse: collapse; width: 50%; height: 81px;" border="1">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Arguments</th>
                    <th>Return Type</th>
                </tr>
            </thead>
            <tbody>
                {tbody}
            </tbody>
        </table>
        </div>
    """
    tbody=""
    for i in functions.keys():
        tbody+="""
            <tr>
                <td>{name}</td>
                <td>{type}</td>
                <td>{contxt}</td>
            </tr>
        """.format(name=i,type=functions[i]["args"],contxt=functions[i]["retType"])
    return html.format(tbody=tbody)

def html_variables(variables):
    html="""
        <table  class="table table-striped table-hover" style="border-collapse: collapse; width: 70%; height: 81px;" border="1">
            <thead>
                <tr>
                    <th>Name</th>
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
                <td>{name}</td>
                <td>{type}</td>
                <td>{contxt}</td>
                <td>{values}</td>
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
        </div>
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
    html="""
    <h3>Analyzed Code</h3>
    <pre class="code" data-lang="python"><div class="code-block"><code>\n"""
    lines = code.split('\n')
    
    for line_num, line in enumerate(lines):
        html+='<p style="margin-top: -30px;">'
        if line_num in labels:
            endin ={}
            [].reverse
            for n,char in enumerate(line):
                if n in endin:
                    endin[n].reverse()
                    errors=""
                    for end in endin[n]:
                        errors+= end["level"] +":" + end["msg"] + "\n"

                    html+='<span class="errortext">'+ errors+ "</span>"    
                    
                    for end in endin[n]:
                        html+= "</span>"
                    
                    endin.pop(n)
                
                if n in labels[line_num]:
                     for each in labels[line_num][n]:
                        html+='<span class="{level}">'.format(level=each["level"])
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
                if_context=list(tree[context].keys())[indexCntxt]
                
                build["if_" + str(if_context)] = context_builder(if_context,tree[context],i[name]["content"])
                
                indexCntxt+=1
                for elcond in i[name]["elses"]:
                    nw_context=list(tree[context].keys())[indexCntxt]
                    if elcond == i[name]["elses"][-1] and "else" in i[name]["elses"][-1]:
                        build["else_" + str(nw_context)]=context_builder(nw_context,tree[context],elcond["else"]["content"])
                    else:
                        build["elif_" + str(nw_context)]=context_builder(nw_context,tree[context],elcond["elif"]["content"])
                    
                    indexCntxt+=1

            elif name=="switch":
                
                nw_context=list(tree[context].keys())[indexCntxt]
                build[name+"_" + list(tree[context].keys())[indexCntxt]]=context_builder(context,tree,i[name]["cases"])
                indexCntxt+=1
                nw_context=list(tree[context].keys())[indexCntxt]
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

    html='<ul id="myUL">\n'
    html+=html_context({"global": context_builder("global",tree,nested)})
    html+="</ul>"

    return html

def html_analyzerOutput(nested):
    html="<pre class=\"code\" data-lang=\"JSON\" ><code>"+json.dumps(nested,indent=2)+"</code></pre>"

    return html

def html_graph(info, graph):
    if graph == 'cf':
        graph_name = "Control Flow Graphs"
        folder = "CFGraphs"
        plus_function = "plusDivsCF"
    elif graph == 'sd':
        graph_name = "System Dependency Graphs"
        folder = "SDGraphs"
        plus_function = "plusDivsSD"

    html=""
    html+="<h4>" + graph_name + "</h4>"
    for file in os.listdir(folder):
        if file.endswith(".png"):
            context = file.replace(".png","")
            nodes = info[context]["nodes"]
            edges = info[context]["edges"]
            html+="<div class=\"" + folder + "\">"
            html+=f"""
            <span>
                <button class="w3-button w3-display-left" onclick="{plus_function}(-1)">&#10094;</button>
                {file}
                <button class="w3-button w3-display-right" onclick="{plus_function}(+1)">&#10095;</button></span><p></p>""".format(file=file.replace(".png","") + " context")

            html+="""
            <p> Were found {nodes} nodes and {edges} edges.</p>
            <p> The calculated MCabe's complexity equals: {mcabes}</p>""".format(nodes=nodes,edges=edges,mcabes=edges-nodes+2)
            
            html+="""<img style="max-height:600px" src="{path}" class="img-fit-contain">""".format(path= os.path.join(folder, file))
            html+="""</div>"""
    
    return html

def collapse(containned,title):
    html="""<div style="margin-top: 24px;"> <button type="button" class="collapsible"><h3>"""+title+"""</h3></button>"""
    html+="""<div class="content">"""
    html +=containned
    html+="""</div></div>"""
    return html

def create_html(input,data):
    body =html_code(input,prepareLabels(data))
    body+=collapse(html_graph(data["cfg_info"], 'cf'),"Generated Control Flow Graphs")
    body+=collapse(html_graph(data["sdg_info"], 'sd'),"Generated System Dependency Graphs")
    body+=collapse(html_variables(prepareVars(data["vars"])),"Variables Used")
    body+=collapse(html_func(data["functions"]),"Functions Used")
    body+=collapse(html_instruc(data["instr_counter"],data["type_counter"]),"Instructions Used")
    body+=collapse(html_nested(data["contextTree"],data["nested"]),"Defined Contexts")
    body+=collapse(html_analyzerOutput(data["nested"]),"Analyzers Output")
    
    return html_complete("",body)

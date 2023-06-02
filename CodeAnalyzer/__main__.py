import argparse
from grammar import grammar
from analyzer import analyzer
from html_creator import create_html
from lark import Lark
from genGraphs import genCFGs


def main():
    parser = argparse.ArgumentParser(
                prog='CodeAnalyzer',
                description='Code analyzer that produces an html with a report about the input file')

    parser.add_argument("filename",help="Path of the input file")    # positional argument
    parser.add_argument("-o","--outputFile",help="Name of the output file",default="output.html")
    args = parser.parse_args()


    # Read input file
    codef = open(args.filename,"r")
    code = codef.read()

    # Create parser
    p = Lark(grammar,propagate_positions=True)
    
    
    #Clear output directory
    import os
    
    dir = 'CFGraphs/'
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))



    #Parse the inputfile
    parse_tree = p.parse(code)
    # Start Interpreter
    data = analyzer().visit(parse_tree)

    # Open output file
    f = open(args.outputFile,"w")

    # Create the CFG 
    data["cfg_info"] =genCFGs(data["code"])



    # Compile html
    html =create_html(code,data)

    

    # Write the html code
    f.write(html)

    # Close file descriptors
    f.close()
        

        
    codef.close()






if __name__ == '__main__':
    # execute only if run as the entry point into the program
    main()

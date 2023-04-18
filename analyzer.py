#!/usr/bin/python3

from lark import Lark
from lark import Discard
from lark.visitors import Interpreter

from grammar import grammar
from html_creator import html_builder

frase = """
a = 5;
"""
p = Lark(grammar)
parse_tree = p.parse(frase)
#print(parse_tree.pretty())
print(html_builder())

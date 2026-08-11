#!/usr/bin/env python3

from typing import List
from pgl_lexer import PglLexer
from pgl_parser import PglParser
from pgl_ast import Generator, Variations
from pgl_generator import DefTable, PglExpander, PglGenerator, IdCounter, Node
import argparse
import sys
import itertools
import pathlib

class PglTester(PglGenerator):
    """
    Node visitor class that generates the pattern permutations based on the AST.
    """

    def __init__(self, lang, output_path, split):

        # The generated code (list of strings)
        self.code: List[List,Variations] = []
        self.defTable = DefTable()
        self.typeDefTable = DefTable()
        self.typeDef = None
        self.lang = lang
        self.output_path = output_path
        self.split = split
        self.counter=0

    def visit_Program(self, node: Node, buf=sys.stdout):
        # super().visit_Program(node, buf)

        def dict_product(dicts):
            return (dict(zip(dicts, x)) for x in itertools.product(*dicts.values()))
        for _statement in node.statements:
            if _statement is not None:
                if isinstance(_statement, Generator):
                    typedefTableFiltered = { ty.name: self.typeDefTable[ty.name] for ty in _statement.types }
                    for self.typeDef in list(dict_product(typedefTableFiltered)):
                        self.codeReset()
                        self.visit(_statement)
                        self.add('\n')
                        typedef = str(self.typeDef[_statement.types[-1].name])
                        self.counter=0
                        buf = open(self.output_path+"/"+_statement.name+"_"+typedef+"_"+str(self.counter//self.split)+".c", "w")
                        for i in itertools.product(*self.code):
                            
                            if self.counter%self.split==0:
                                buf.close()
                                buf = open(self.output_path+"/"+_statement.name+"_"+typedef+"_"+str(self.counter//self.split)+".c", "w")

                            buf.write(''.join(map(str, i)))
                            self.counter+=1

                        buf.close()

                        # Create .c file
                        buf = open(self.output_path+"/"+_statement.name+"_"+typedef+".c", "w")
                        # for i in range(0,self.counter//self.split+1):
                        #     buf.write('#include "'+_statement.name+'_'+typedef+'_'+str(i)+'.c"\n')
                        buf.write('#include <stdlib.h>\n')
                        buf.write('#include "'+_statement.name+'_'+typedef+'.h"\n')
                        size=max(IdCounter("").counters.values())

                        for i in range(1,size+1):
                            buf.write('fun_'+typedef+' '+_statement.name+"_"+str(i)+"_"+typedef+';\n')
                        buf.write('pfun_'+typedef+' *function_'+typedef+';\n')
                        buf.write('void functions_'+typedef+'() {\n')
                        buf.write('function_'+typedef+' = malloc(N_TESTS*sizeof(pfun_'+typedef+'));\n')
                        for i in range(1,size+1):
                            buf.write('function_'+typedef+'['+str(i-1)+']='+_statement.name+"_"+str(i)+"_"+typedef+";\n")
                        buf.write('}\n\n')
                        buf.close()

                        # Create .h file
                        buf = open(self.output_path+"/"+_statement.name+"_"+typedef+".h", "w")

                        buf.write('#ifndef '+typedef.upper()+'_H_INCLUDED\n')
                        buf.write('#define '+typedef.upper()+'_H_INCLUDED\n')
                        buf.write('#define N_TESTS '+str(size)+'\n')
                        for line in _statement.extra:
                            if line:
                                buf.write(str(line)+'\n')

                        buf.write('extern pfun_'+typedef+' *function_'+typedef+';\n')
                        buf.write('void functions_'+typedef+'();\n')
                        buf.write('#endif\n')
                        buf.close()
                            
                else:
                    self.visit(_statement)
        
        


    def visit_Generator(self, node: Node):
        if self.lang == "c":
            self.visit_CGenerator(node)
        elif self.lang == "f90":
            self.visit_F90Generator(node)
        else:
            raise Exception("Language not supported")
        
        self.add("\n")

    def visit_CGenerator(self, node: Node):
        for include in node.includes_instruction:
            self.add(str(include))
        if node.types[-1].pointer_array[-1].name == "out":
            functype = str(self.typeDef[node.types[-1].name])
        else:
            functype = "void"
        self.add(functype + " ")
        counter = IdCounter(node.name, "pattern")
        self.add(counter)
        typedef = str(self.typeDef[node.types[-1].name])
        self.add("_"+typedef)
        self.add("(")
        for i, _type in enumerate(node.types):
            self.visit(_type)
            if i < len(node.types)-1:
                self.add(', ')
        self.add(")")
        types = ""
        for i, _type in enumerate(node.types):
            for j, _var in enumerate(_type.pointer_array):
                types += str(self.typeDef[_type.name])
                types+="*"*_var.pointers
                if j < len(_type.pointer_array)-1:
                    types += ', '
            if i < len(node.types)-1:
                types += ', '

        node.extra[0] = "typedef " + functype + "(*pfun_" +typedef+")("+types+");"
        node.extra[1] = "typedef " + functype + "(fun_" +typedef+")("+types+");"
        self.visit(node.instructions)
        if node.types[-1].pointer_array[-1].name == "out":
            self.code[-1] = ["return out;\n}"]

    def visit_F90Generator(self, node: Node):        
        self.add("subroutine ")
        self.add(IdCounter(node.name, "pattern"))
        self.add("_"+str(self.typeDef[node.types[-1].name]))
        self.add("(")
        for i, _type in enumerate(node.types):
            for j, _var in enumerate(_type.pointer_array):
                self.add(_var.name)
                if j < len(_type.pointer_array)-1:
                    self.add(', ')
            if i < len(node.types)-1:
                self.add(', ')
        self.add(")\n")
        for i, _type in enumerate(node.types):
            self.visit(_type)
            self.add('\n')
        self.visit(node.instructions)
        self.add("\nend subroutine\n")


def main():

    cli = argparse.ArgumentParser(description = "PGL - Pattern Generator Language")
    languages = ["c", "f90"]
    cli.add_argument("-l", "--language", type=str.lower, help="Language type", choices=languages, default="c")
    cli.add_argument("-i", "--input", help="Input file", required=True)
    cli.add_argument("-o", "--output", help="Output path", required=True)
    cli.add_argument("-s", "--split", type=int, help="Max number of functions generated per file", default=10)
    args = cli.parse_args()

    global lang_type
    lang_type = args.language

    lexer = PglLexer()
    text = open(args.input).read()

    tokens = lexer.tokenize(text) # Creates a generator of tokens
    parser = PglParser(text)
    ast = parser.parse(tokens) # The entry point to the parser
    expander = PglExpander()
    expander.visit(ast)
    
    # Creates the output directory if it does not exist
    pathlib.Path(args.output).mkdir(parents=True, exist_ok=True)

    generator = PglTester(lang=lang_type, output_path=args.output, split=args.split)
    generator.visit(ast)

if __name__ == '__main__':
    main()
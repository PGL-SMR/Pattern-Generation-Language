#!/usr/bin/env python3

from pgl_lexer import PglLexer
from pgl_parser import PglParser
from pgl_ast2pgl import PglEmitter
from pgl_ast2dot import DotEmitter
from pgl_generator import PglExpander, PglGenerator
import argparse
import sys

def main():

    cli = argparse.ArgumentParser(description = "PGL - Pattern Generator Language")
    languages = ["c", "f90"]
    cli.add_argument("-l", "--language", type=str.lower, help="Language type", choices=languages, default="c")
    cli.add_argument("-i", "--input", help="Input file", required=True)
    cli.add_argument("-d", "--debug", help="Debug", action='store_true')
    args = cli.parse_args()

    global lang_type, debug
    lang_type = args.language
    debug = args.debug

    lexer = PglLexer()
    text = open(args.input).read()

    if debug:
        tokens = lexer.tokenize(text) # Creates a generator of tokens
        print("[Debug] Lexer tokens:")
        for token in tokens:
            print(token)
        print("")
    
    tokens = lexer.tokenize(text) # Creates a generator of tokens
    parser = PglParser(text)
    ast = parser.parse(tokens) # The entry point to the parser

    if debug:
        print("[Debug] Parser AST:")
        ast.show(buf=sys.stdout, showcoord=True)
        print("")

    emitter = PglEmitter()

    if debug:
        print("[Debug] Emit PGL from AST:")
        emitter.visit(ast)
        emitter.show()
        print("")

    # if debug:
    #     dot = DotEmitter(args.input)
    #     print("[Debug] Emit DOT from AST:")
    #     dot.visit(ast)
    #     dot.show()
    #     print("")

    expander = PglExpander()
    expander.visit(ast)
    if debug:
        print("[Debug] Expanded Parser AST:")
        ast.show(buf=sys.stdout, showcoord=True)
        print("")
    generator = PglGenerator(lang=lang_type)
    generator.visit(ast)

    if debug:
        print("[Debug] Generator List:")        
        generator.show()
        print("")

if __name__ == '__main__':
    main()
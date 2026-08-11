from sly import Parser
from pgl_lexer import PglLexer
from pgl_ast import *


class PglParser(Parser):

    def __init__(self, text, importing=False):
        self.text = text
        self.importing = importing

    def _production_coord(self, p):
        last_cr = self.text.rfind('\n', 0, p.index)
        if last_cr < 0:
            last_cr = -1
        column = p.index - (last_cr)
        return Coord(p.lineno, column)

    tokens = PglLexer.tokens

    # Un-comment the following line to output the parser logs for debugging any conflicts
    # debugfile = 'parser.out'

    start = 'program'

    # This sets the order of execution. The last values will have a higher precedence
    precedence = (
       ('left', EMPTY),
       ('left', ID),
       ('left', LBRACE, RBRACE),
       ('left', LPAREN, RPAREN),
       ('left', LBRACKET, RBRACKET),
       ('left', POINTER),
       ('left', STATEMENT),
       ('right', DOLLAR),
       ('left', ELIF),
       ('left', NEW_LINE) 
    )

    @_('statements')
    def program(self, p):
        return Program(p[0])

    @_('statement_line')
    def statements(self, p):
        return [p.statement_line]

    @_('statements statement_line')
    def statements(self, p):
        return p.statements + [p.statement_line]

    @_('NEW_LINE')
    def statement_line(self, p):
        return None

    @_('statement NEW_LINE',
    'statement %prec STATEMENT')
    def statement_line(self, p):
        return p[0]

    @_('type_definition',
       'definition',
       'pattern_declaration',
       'import_')
    def statement(self, p):
        return p[0]

    @_('IMPORT STRING')
    def import_(self, p):
        file_name = p.STRING
        if file_name.startswith('\"') or file_name.startswith('\''):
            file_name = file_name[1:-1]
        return Import(file_name, coord=self._production_coord(p))

    @_('instructions')
    def variation(self, p):
        return p[0]

    @_('variation')
    def variation_list(self, p):
        return [p.variation]

    @_('variation_list OR variation')
    def variation_list(self, p):
        return p.variation_list + [p.variation]

    @_('TYPE ID COLON variation_list')
    def type_definition(self, p):
        return TypeDef(name=p.ID, types=Variations(p.variation_list), coord=self._production_coord(p))

    @_('ID')
    def parameter_decl(self, p):
        return Code(p[0], isId=True, coord=self._production_coord(p))

    @_('expansion')
    def parameter_decl(self, p):
        return p[0]

    @_('parameter_decl')
    def parameter_list(self, p):
        return [p.parameter_decl]

    @_('parameter_list COMMA parameter_decl')
    def parameter_list(self, p):
        return p.parameter_list + [p.parameter_decl]

    @_('parameter_list')
    def parameters(self, p):
        return ParamList(p[0], coord=self._production_coord(p))

    @_('ID')
    def expression(self, p):
        return Code(p[0], isId=True, coord=self._production_coord(p))

    @_('CODE',
       'EQUALS',
       'POINTER',
       'STRING')
    def expression(self, p):
        return Code(p[0], coord=self._production_coord(p))

    @_('ID LPAREN expression_parameters RPAREN')
    def expression_func(self, p):
        exps = []
        for exp in p.expression_parameters:
            exps.append(exp)
            exps.append(Code(","))
        exps.pop()
        return Instructions([Code(p[0], coord=self._production_coord(p))] + [Code(p[1])] + exps + [Code(p[3])],coord=self._production_coord(p))

    @_('expression')
    def expression_list(self, p):
        return [p.expression]

    @_('expression_list expression')
    def expression_list(self, p):
        return p.expression_list + [p.expression]

    @_('expression_list')
    def expressions(self, p):
        return Instructions(p.expression_list, coord=self._production_coord(p))

    @_('expressions',
       'expansion',
       'expression_func')
    def expression_decl(self, p):
        return p[0]

    @_('expression_decl')
    def expression_parameters(self, p):
        return [p.expression_decl]

    @_('expression_parameters COMMA expression_decl')
    def expression_parameters(self, p):
        return p.expression_parameters + [p.expression_decl]

    @_('DEF ID LPAREN parameters RPAREN COLON variation_list',
       'DEF ID LPAREN empty RPAREN COLON variation_list')
    def definition(self, p):
        return Def(name=p.ID, vars=p.parameters, instructions=Variations(p.variation_list, coord=self._production_coord(p)), coord=self._production_coord(p))

    @_('DECL ID LPAREN declaration_type_expansion_list RPAREN brace_block EQUALS brace_block',
       'DECL ID LPAREN empty RPAREN brace_block EQUALS brace_block')
    def pattern_declaration(self, p):

        if self.importing:
            return None

        includes_instruction=[]
        _b=p.brace_block0.content
        if isinstance(_b, Lines):
            for line in _b.lines:
                if isinstance(line, Instructions):
                    for inst in line.instructions:  
                        if isinstance(inst, Include):
                            includes_instruction.append(inst)

        includes_replacement=[]
        _b=p.brace_block1.content
        if isinstance(_b, Lines):
            for line in _b.lines:
                if isinstance(line, Instructions):
                    for inst in line.instructions:                    
                        if isinstance(inst, Include):
                            includes_replacement.append(inst)                        
        
        return Generator(name=p.ID, types=p[3], instructions=p.brace_block0, includes_instruction=includes_instruction, replacement=p.brace_block1, includes_replacement=includes_replacement, coord=self._production_coord(p))

    @_('INCLUDE')
    def include(self, p):
        return Include(p[0], coord=self._production_coord(p))

    @_('ID')
    def code(self, p):
        return Code(p[0], isId=True, coord=self._production_coord(p))

    @_('CODE',
       'EQUALS',
       'COMMA',
       'POINTER',
       'LBRACKET',
       'RBRACKET',
       'STRING')
    def code(self, p):
        return Code(p[0], coord=self._production_coord(p))

    @_('code',
       'expansion',
       'type_expansion',
       'brace_block',
       'paren_block',
       'operation',
       'include')
    def instruction(self, p):
        return p[0]

    @_('instruction')
    def instruction_list(self, p):
        return [p.instruction]

    @_('instruction_list instruction')
    def instruction_list(self, p):
        return p.instruction_list + [p.instruction]

    @_('instruction_list')
    def instructions(self, p):
        return Instructions(p.instruction_list, coord=self._production_coord(p))

    @_('instructions NEW_LINE',
       'NEW_LINE')
    def instruction_line(self, p):
        if len(p)>1:
            return p.instructions
        else:
            return None

    @_('instruction_line')
    def instruction_lines(self, p):
        return [p.instruction_line]

    @_('instruction_lines instruction_line')
    def instruction_lines(self, p):
        return p.instruction_lines + [p.instruction_line]

    @_('instruction_lines')
    def lines(self, p):
        return Lines(p.instruction_lines)

    @_('LBRACE lines RBRACE', # multiple lines
       'LBRACE instructions RBRACE', # 1 line
       'LBRACE empty RBRACE') # empty
    def brace_block(self, p):
        return Block(p[0], p[1], p[2], coord=self._production_coord(p))

    @_('LPAREN lines RPAREN', # multiple lines
       'LPAREN instructions RPAREN', # 1 line
       'LPAREN empty RPAREN') # empty
    def paren_block(self, p):
        return Block(p[0], p[1], p[2], coord=self._production_coord(p))

    @_('DOLLAR ID LPAREN expression_parameters RPAREN')
    def expansion(self, p):
        return Expansion(name=p.ID, vars=p.expression_parameters, coord=self._production_coord(p))

    @_('DOLLAR ID')
    def type_expansion(self, p):
        return TypeExpansion(name=p.ID, coord=self._production_coord(p))

    @_('declaration_type_expansion')
    def declaration_type_expansion_list(self, p):
        return [p.declaration_type_expansion]

    @_('declaration_type_expansion_list COMMA declaration_type_expansion')
    def declaration_type_expansion_list(self, p):
        return p.declaration_type_expansion_list + [p.declaration_type_expansion]

    @_('DOLLAR ID LPAREN pointer_array_list RPAREN',
       'DOLLAR ID LPAREN empty RPAREN')
    def declaration_type_expansion(self, p):
        return TypeDecl(p.ID, p[3], coord=self._production_coord(p))

    @_('empty')
    def pointers(self, p):
        return 0

    @_('pointers POINTER',
       'POINTER')
    def pointers(self, p): # Return the number of pointers
        if len(p)>1:
            return p.pointers + 1
        else:
            return 1

    @_('LBRACKET ID RBRACKET',
       'LBRACKET CODE RBRACKET')
    def array(self, p):
        return p[1]

    @_('empty')
    def arrays(self, p):
        return None

    @_('arrays array',
       'array')
    def arrays(self, p):
        if len(p)>1:
            return p.arrays + [p.array]
        else:
            return [p.array]

    @_('pointers ID arrays')
    def pointer_array(self, p):
        return PointerArray(p.pointers, p.ID, p.arrays)

    @_('pointer_array')
    def pointer_array_list(self, p):
        return [p.pointer_array]

    @_('pointer_array_list COMMA pointer_array')
    def pointer_array_list(self, p):
        return p.pointer_array_list + [p.pointer_array]

    @_('conditional_operation')
    def operation(self, p):
        return p[0]

    @_('EQ',
       'NE')
    def operator(self, p):
        return p[0]

    @_('type_expansion operator STRING',
       'type_expansion operator ID',
       'STRING operator type_expansion',
       'ID operator type_expansion')
    def condition(self, p):
        if isinstance(p[0], str):
            p[0] = Code(p[0], coord=self._production_coord(p))
        if isinstance(p[2], str):
            p[2] = Code(p[2], coord=self._production_coord(p))
        return Comparison(p[1], [p[0]] + [p[2]], coord=self._production_coord(p))

    @_('ELSE brace_block')
    def else_(self, p):
        return [(None, p.brace_block)]

    @_('elif_list else_',
       'elif_list',
       'else_',
       'empty')
    def elif_else_opt(self, p):
        if len(p)>1:
            return p[0] + p[1]
        if p[0]:
            return p[0]
        else:
            return []

    @_('IF LPAREN condition RPAREN brace_block elif_else_opt')
    def conditional_operation(self, p):
        condition_block = [(p.condition, p.brace_block)] + p.elif_else_opt
        conditions = [c for c, _ in condition_block]
        blocks = [b for _, b in condition_block]
        return IfOperation(conditions, blocks, coord=self._production_coord(p))

    @_('ELIF LPAREN condition RPAREN brace_block')
    def elif_(self, p):
        return [(p.condition, p.brace_block)]

    @_('elif_',
       'elif_list elif_')
    def elif_list(self, p):
        if len(p)>1:
            return p.elif_list + p.elif_
        else:
            return p.elif_

    @_('  %prec EMPTY')
    def empty(self, p):
        return None

    def error(self, p):
        if p:
            print("Syntax error at", print_token(self.text, p))
        else:
            print("Syntax error at EOF")

# Compute column.
#     input is the input text string
#     token is a token instance
def find_column(text, token):
    last_cr = text.rfind('\n', 0, token.index)
    if last_cr < 0:
        last_cr = 0
    column = (token.index - last_cr) + 1
    return column

def print_token(text, token):
    return f"Token {token.type} : {token.value} @{token.lineno},{find_column(text, token)}"

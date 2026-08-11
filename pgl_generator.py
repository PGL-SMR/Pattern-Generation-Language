import sys
from typing import List
from pgl_lexer import PglLexer
from pgl_parser import PglParser
from pgl_ast import Node, Code, Variations, Generator
import itertools
import copy

operation = {
    "!=": lambda l, r: str(l) != str(r),
    "==": lambda l, r: str(l) == str(r)
}

class NodeVisitor:
    """A base NodeVisitor class for visiting ast nodes.
    Subclass it and define your own visit_XXX methods, where
    XXX is the class name you want to visit with these
    methods.
    """

    _method_cache = None

    def visit(self, node):
        """Visit a node."""

        if self._method_cache is None:
            self._method_cache = {}

        visitor = self._method_cache.get(node.__class__.__name__)
        if visitor is None:
            method = "visit_" + node.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            self._method_cache[node.__class__.__name__] = visitor

        return visitor(node)

    def generic_visit(self, node):
        """Called if no explicit visitor function exists for a
        node. Implements preorder visiting of the node.
        """
        for _, child in node.children():
            self.visit(child)

class NodeTransformer(NodeVisitor):
    """A base NodeTransformer class for transforming ast nodes.
    Subclass it and define your own visit_XXX methods, where
    XXX is the class name you want to visit with these
    methods.
    """

    def generic_visit(self, node):
        """Called if no explicit visitor function exists for a
        node. Implements preorder visiting of the node.
        """
        for field, child in node.children():
            self.attr_handle(node, field, self.visit(child))
        return node

    def attr_handle(self, node, field, attr):
        if "[" in field:
            position = int(field[field.find("[")+1:field.find("]")])
            field = field[:field.find("[")]
            list = getattr(node, field)
            if attr:
                list[position] = attr
            else:
                del list[position] # Maybe bug other iterations
        else:
            if attr:
                setattr(node, field, attr)
            else:
                delattr(node, field)

class DefTable(dict):
    def __init__(self, deff=None):
        super().__init__()
        self.deff = deff

    def add(self, name, value):
        self[name] = value

    def lookup(self, name):
        ret = self.get(name, None)
        if not ret:
            raise Exception("Expansion $"+name + " not defined previously.")

        return ret

    def substitute(self, name: str, params: list):
        def flatten(parent, node):
            ret=[]
            if not isinstance(node, tuple):
                node=("parent", node)
            ret.append((parent, node))
            for child in node[1].children():
                ret.extend(flatten(node[1], child))
            return ret
        lookup = self.lookup(name)

        if not isinstance(lookup, tuple):
            raise Exception("Expansion $"+name + " is a TypeExpansion, and cannot have parameters.")

        defs, instructions = lookup

        if len(defs.params) != len(params):
            raise Exception("Expansion $"+name + " expects " + str(len(defs.params)) + " parameters, but " + str(len(params)) + " were given.")
        
        to_substitute = []

        # Substitute parameters
        instructions = copy.deepcopy(instructions)
        for i, _var in enumerate(defs.params): # itertools.product
            for parent, (name, _inst) in flatten(instructions, instructions):
                if isinstance(_inst, Code):
                    if _inst.code == _var.code:
                        if "[" in name:
                            position = int(name[name.find("[")+1:name.find("]")])
                            name = name[:name.find("[")]
                            to_substitute.append((parent, name, position, copy.deepcopy(params[i])))
                        else:
                            position=None
                            to_substitute.append((parent, name, position, copy.deepcopy(params[i])))

        for parent, name, position, param in to_substitute:
            if position is not None:
                list = getattr(parent, name)
                list[position] = param
            else:
                setattr(parent, name, param)

        return instructions


    def show(self, buf=sys.stdout):
        for key, value in self.items():
            if isinstance(value, tuple):
                buf.write(f'{key}(')
                value[0].show(buf=buf, showcoord=True)
                buf.write(') = ')
                value[1].show(buf=buf, showcoord=True)
                buf.write('\n')
            else:
                buf.write(f'{key} = ')
                value.show(buf=buf, showcoord=True)
                buf.write('\n')

class IdCounter():

    counters={}

    def __init__(self, id, type=""):
        self.name=id+"_"+type
        self.id=id
        self.counters[self.name]=0

    def __str__(self):
        self.counters[self.name] += 1
        return self.id+"_"+str(self.counters[self.name])

class PglExpander(NodeTransformer):
    """
    Node visitor class that transforms the AST Expansion nodes.
    """

    def __init__(self):
        self.defTable = DefTable()

    def visit_Import(self, node: Node):
        import_text = open(node.filename).read()
        lexer = PglLexer()
        parser = PglParser(import_text, importing=True)
        import_tokens = lexer.tokenize(import_text)
        import_ast = parser.parse(import_tokens)
        node.ast = import_ast.statements
        for _statement in node.ast:
            self.visit(_statement)
        return node

    def visit_Def(self, node: Node):
        def flatten(parent, node):
            ret=[]
            if not isinstance(node, tuple):
                node=("parent", node)
            ret.append((parent, node))
            for child in node[1].children():
                ret.extend(flatten(node[1], child))
            return ret
        self.visit(node.instructions)

        ret_instructions = Variations([])
        instructions = copy.deepcopy(node.instructions)
        var_list = []
        parent_names = []
        for parent, (name, _inst) in flatten(instructions, instructions):
            if isinstance(_inst, Variations) and _inst != instructions:
                var_list.append(_inst)
                parent_names.append((parent, name))

        for vars in itertools.product(*var_list):
            for i, _var in enumerate(vars):
                (parent, name) = parent_names[i]

                if "[" in name:
                    position = int(name[name.find("[")+1:name.find("]")])
                    name = name[:name.find("[")]
                    list = getattr(parent, name)
                    list[position] = copy.deepcopy(_var)
                else:
                    setattr(parent, name, copy.deepcopy(_var))

            new_instructions = copy.deepcopy(instructions)
            ret_instructions.vars.extend(new_instructions.vars)   

        self.defTable.add(node.name,(node.vars, ret_instructions))
        return node

    def visit_Expansion(self, node: Node):

        var_list = []
        for _var in node.vars:
            _var = self.visit(_var)
            if isinstance(_var, Variations):
                var_list.append(_var)
            else:
                var_list.append([_var])

        instructions = Variations([])

        for vars in itertools.product(*var_list):
            new_instructions = self.defTable.substitute(node.name, vars)
            instructions.vars.extend(new_instructions.vars)                      

        instructions = self.visit(instructions)
        return instructions


class PglGenerator(NodeVisitor):
    """
    Node visitor class that generates the pattern permutations based on the AST.
    """

    def __init__(self, lang="c"):

        # The generated code (list of strings)
        self.code: List[List,Variations] = []
        self.defTable = DefTable()
        self.typeDefTable = DefTable()
        self.typeDef = None
        self.lang = lang

    def add(self, element):
        if isinstance(element, Variations):
            self.code.append(element)
        else:
            # if element == "\n" and self.code[-1] == [" "]:
            #     return

            self.code.append([element])

    def codeReset(self):
        self.code = []

    def show(self, buf=sys.stdout):
        buf.write(str(self.code))

    def visit_Program(self, node: Node, buf=sys.stdout):
        def dict_product(dicts):
            return (dict(zip(dicts, x)) for x in itertools.product(*dicts.values()))
        # node.show()
        for _statement in node.statements:
            if _statement is not None:
                if isinstance(_statement, Generator):
                    typedefTableFiltered = { ty.name: self.typeDefTable[ty.name] for ty in _statement.types }
                    for self.typeDef in list(dict_product(typedefTableFiltered)):
                        self.codeReset()
                        self.visit(_statement)
                        self.add('\n')
                        for i in itertools.product(*self.code):
                            buf.write(''.join(map(str, i)))
                else:
                    self.visit(_statement)
        # self.defTable.show()

    def visit_Code(self, node: Node):
        if node.code == ";" and self.code[-1] == " ":
            self.code[-1]=node.code
        else:
            self.add(node.code)

    def visit_Instructions(self, node: Node):
        for i, _instruction in enumerate(node.instructions):
            if i > 0:
                if isinstance(node.instructions[i-1], Code) and isinstance(node.instructions[i], Code):
                    if node.instructions[i-1].isId and node.instructions[i].isId:
                        self.add(' ')
            self.visit(_instruction)
            if not isinstance(_instruction, Code):
                self.add(' ')

    def visit_ParamList(self, node: Node):
        for i, _param in enumerate(node.params):
            self.visit(_param)
            if i < len(node.params)-1:
                self.add(', ')

    def visit_Lines(self, node: Node):
        for _line in node.lines:
            if _line is not None:
                self.visit(_line)
                self.add('\n')

    def visit_Variations(self, node: Node):
        self.add(node)

    def visit_Block(self, node: Node):
        if self.lang=="c":
            self.add(node.start)
            if node.start == '{':
                self.add('\n')
            self.visit(node.content)
            self.add(node.end)
        elif self.lang=="f90":
            if node.start != '{':
                self.add(node.start)
            self.visit(node.content)
            if node.end != '}':
                self.add(node.end)

    def visit_Def(self, node: Node):
        self.defTable.add(node.name,(node.vars, node.instructions))

    def visit_TypeExpansion(self, node: Node):
        self.add(str(self.typeDef[node.name]))

    def visit_TypeDef(self, node: Node):
        self.typeDefTable.add(node.name, node.types)

    def visit_TypeDecl(self, node: Node):
        if self.lang == "c":
            for i, _var in enumerate(node.pointer_array):
                self.add(str(self.typeDef[node.name]) + " " + str(_var))
                if i < len(node.pointer_array)-1:
                    self.add(', ')
        elif self.lang == "f90":
            for i, _var in enumerate(node.pointer_array):
                dims = ""
                if _var.arrays is not None:
                    dims = ", dimension("
                    for j, dim in enumerate(_var.arrays):
                        dims += dim
                        if j < len(_var.arrays)-1:
                            dims += ", "
                    dims += ")"
                self.add(str(self.typeDef[node.name]) + dims + " :: " + _var.name)
                self.add('\n')

    def visit_IfOperation(self, node: Node):
        for i, condition in enumerate(node.conditions):
            if condition is not None:
                if isinstance(condition.terms[0], Code):
                    code = condition.terms[0].code
                    type = self.typeDef[condition.terms[1].name]
                else:
                    code = condition.terms[1].code
                    type = self.typeDef[condition.terms[0].name]
                if operation[condition.operator](type, code):
                    self.visit(node.blocks[i].content)
                    break
            else:
                self.visit(node.blocks[i].content)
                break            

    def visit_Generator(self, node: Node):
        self.add(self.lang+" {\n")
        if self.lang == "c":
            self.visit_CGenerator(node)
        elif self.lang == "f90":
            self.visit_F90Generator(node)
        else:
            raise Exception("Language not supported")
        
        self.add("\n}")

    def visit_CGenerator(self, node: Node):
        for include in node.includes_instruction:
            self.add(str(include))
        self.add("void ")
        self.add(IdCounter(node.name, "pattern"))
        self.add("(")
        for i, _type in enumerate(node.types):
            self.visit(_type)
            if i < len(node.types)-1:
                self.add(', ')
        self.add(")")
        self.visit(node.instructions)
        self.add("\n} = ")
        self.add("{\n")
        for include in node.includes_replacement:
            self.add(str(include))
        self.add("void ")
        self.add(IdCounter(node.name, "replacement"))
        self.add("(")
        for i, _type in enumerate(node.types):
            self.visit(_type)
            if i < len(node.types)-1:
                self.add(', ')
        self.add(")")
        self.visit(node.replacement)

    def visit_F90Generator(self, node: Node):        
        self.add("subroutine ")
        self.add(IdCounter(node.name, "pattern"))
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
        self.add("} = {\n")
        self.add("subroutine ")
        self.add(IdCounter(node.name, "replacement"))
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
        self.visit(node.replacement)
        self.add("\nend subroutine\n")
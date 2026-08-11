import sys
from typing import List
from pgl_ast import Node, Code

class NodeVisitor:
    """A base NodeVisitor class for visiting uc_ast nodes.
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


class PglEmitter(NodeVisitor):
    """
    Node visitor class that regenerates the PGL program based on the AST, 
    for testing purposes.
    """

    def __init__(self):

        # The generated code (list of strings)
        self.code: List[str] = []

    def show(self, buf=sys.stdout):
        buf.write(''.join(self.code))

    def visit_Program(self, node: Node):
        for _statement in node.statements:
            if _statement is not None:
                self.visit(_statement)
                self.code.append('\n')

    def visit_Code(self, node: Node):
        if node.code == ";" and self.code[-1] == " ":
            self.code[-1]=node.code
        else:
            self.code.append(node.code)

    def visit_Instructions(self, node: Node):
        for i, _instruction in enumerate(node.instructions):
            if i > 0:
                if isinstance(node.instructions[i-1], Code) and isinstance(node.instructions[i], Code):
                    if node.instructions[i-1].isId and node.instructions[i].isId:
                        self.code.append(' ')
            self.visit(_instruction)
            if not isinstance(_instruction, Code):
                self.code.append(' ')

    def visit_ParamList(self, node: Node):
        for i, _param in enumerate(node.params):
            self.visit(_param)
            if i < len(node.params)-1:
                self.code.append(', ')

    def visit_Lines(self, node: Node):
        for _line in node.lines:
            if _line is not None:
                self.visit(_line)
                self.code.append('\n')

    def visit_Variations(self, node: Node):
        for i, _variation in enumerate(node.vars):
            self.visit(_variation)
            if i < len(node.vars)-1:
                self.code.append(" | ")

    def visit_Block(self, node: Node):
        self.code.append(node.start)
        if node.start == '{':
            self.code.append('\n')
        self.visit(node.content)
        self.code.append(node.end)

    def visit_Def(self, node: Node):
        self.code.append("def "+node.name)
        self.code.append("(")
        self.visit(node.vars)
        self.code.append("): ")
        self.visit(node.instructions)

    def visit_TypeExpansion(self, node: Node):
        self.code.append('$'+node.name)

    def visit_TypeDef(self, node: Node):
        self.code.append("type "+node.name+": ")
        self.visit(node.types)

    def visit_TypeDecl(self, node: Node):
        self.code.append('$'+node.name)
        self.code.append("(")
        for i, _var in enumerate(node.pointer_array):
            self.code.append(str(_var))
            if i < len(node.pointer_array)-1:
                self.code.append(', ')
        self.code.append(")")

    def visit_Expansion(self, node: Node):
        self.code.append('$'+node.name)
        self.code.append("(")
        for i, _var in enumerate(node.vars):
            self.visit(_var)
            if i < len(node.vars)-1:
                self.code.append(', ')
        self.code.append(")")

    def visit_IfOperation(self, node: Node):
        for i, condition in enumerate(node.conditions):
            if condition is not None:
                if (i==0):
                    self.code.append('$if')
                else:
                    self.code.append('$elif')
                self.code.append('(')
                self.visit(condition.terms[0])
                self.code.append(' '+condition.operator+' ')
                self.visit(condition.terms[1])
                self.code.append(') ')
            else:
                self.code.append('$else ')
            self.visit(node.blocks[i])  

    def visit_Generator(self, node: Node):
        self.code.append("decl "+node.name)
        self.code.append("(")
        for i, _type in enumerate(node.types):
            self.visit(_type)
            if i < len(node.types)-1:
                self.code.append(', ')
        self.code.append(")")
        self.visit(node.instructions)
        self.code.append(" = ")
        self.visit(node.replacement)
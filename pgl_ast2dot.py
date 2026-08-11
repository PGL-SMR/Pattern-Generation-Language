import sys
from typing import List
from pgl_ast import Node, Code
from graphviz import Digraph

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
        self.graph.node(hash(node), label=node.__class__.__name__, _attributes={"shape": "ellipse"})
        for _, child in node.children():
            self.visit(child)
            self.graph.edge(hash(node), hash(child))
            


class DotEmitter(NodeVisitor):
    """
    Node visitor class that regenerates the DOT program based on the AST, 
    for visualization purposes.
    """

    def __init__(self, fname):
        self.graph = Digraph("g", filename=fname + ".gv", node_attr={"shape": "record"})

    def show(self):
        self.graph.view()

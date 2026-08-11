
from typing import List
from dataclasses import dataclass
from abc import ABC
from abc import abstractmethod
import sys


def represent_node(obj, indent):
    def _repr(obj, indent, printed_set):
        """
        Get the representation of an object, with dedicated pprint-like format for lists.
        """
        if isinstance(obj, list):
            indent += 1
            sep = ",\n" + (" " * indent)
            final_sep = ",\n" + (" " * (indent - 1))
            return (
                "["
                + (sep.join((_repr(e, indent, printed_set) for e in obj)))
                + final_sep
                + "]"
            )
        elif isinstance(obj, Node):
            if obj in printed_set:
                return ""
            else:
                printed_set.add(obj)
            result = obj.__class__.__name__ + "("
            indent += len(obj.__class__.__name__) + 1
            attrs = []

            # convert each node attribute to string
            for name, value in vars(obj).items():

                # is an irrelevant attribute: skip it.
                if name in ('bind', 'coord'):
                    continue

                # relevant attribute not set: skip it.
                if value is None:
                    continue

                # relevant attribute set: append string representation.
                value_str = _repr(value, indent + len(name) + 1, printed_set)
                attrs.append(name + "=" + value_str)

            sep = ",\n" + (" " * indent)
            final_sep = ",\n" + (" " * (indent - 1))
            result += sep.join(attrs)
            result += ")"
            return result
        elif isinstance(obj, str):
            return obj
        else:
            return str(obj)

    # avoid infinite recursion with printed_set
    printed_set = set()
    return _repr(obj, indent, printed_set)

class Node(ABC):
    """Abstract base class for AST nodes."""

    attr_names = ()

    @abstractmethod
    def __init__(self, coord=None):
        self.coord = coord

    def __repr__(self):
        """Generates a python representation of the current node"""
        return represent_node(self, 0)

    def children(self):
        """A sequence of all children that are Nodes"""
        pass

    def show(
        self,
        buf=sys.stdout,
        offset=0,
        attrnames=False,
        nodenames=False,
        showcoord=False,
        _my_node_name=None,
    ):
        """Pretty print the Node and all its attributes and children (recursively) to a buffer.
        buf:
            Open IO buffer into which the Node is printed.
        offset:
            Initial offset (amount of leading spaces)
        attrnames:
            True if you want to see the attribute names in name=value pairs. False to only see the values.
        nodenames:
            True if you want to see the actual node names within their parents.
        showcoord:
            Do you want the coordinates of each Node to be displayed.
        """
        lead = " " * offset
        if nodenames and _my_node_name is not None:
            buf.write(lead + self.__class__.__name__ + " <" + _my_node_name + ">: ")
            inner_offset = len(self.__class__.__name__ + " <" + _my_node_name + ">: ")
        else:
            buf.write(lead + self.__class__.__name__ + ":")
            inner_offset = len(self.__class__.__name__ + ":")

        if self.attr_names:
            if attrnames:
                nvlist = [
                    (n, represent_node(getattr(self, n), offset+inner_offset+1+len(n)+1))
                    for n in self.attr_names
                    if getattr(self, n) is not None
                ]
                attrstr = ", ".join("%s=%s" % nv for nv in nvlist)
            else:
                vlist = [getattr(self, n) for n in self.attr_names]
                attrstr = ", ".join(
                    represent_node(v, offset + inner_offset + 1) for v in vlist
                )
            buf.write(" " + attrstr)

        if showcoord:
            if self.coord and self.coord.line != 0:
                buf.write(" %s" % self.coord)
        buf.write("\n")

        for (child_name, child) in self.children():
            # print(child_name, child)
            child.show(buf, offset + 4, attrnames, nodenames, showcoord, child_name)

class Coord():
    """Coordinates of a syntactic element. Consists of:
    - Line number
    - (optional) column number, for the Lexer
    """

    __slots__ = ("line", "column")

    def __init__(self, line, column=None):
        self.line = line
        self.column = column

    def __str__(self):
        if self.line and self.column is not None:
            coord_str = "@ %s:%s" % (self.line, self.column)
        elif self.line:
            coord_str = "@ %s" % (self.line)
        else:
            coord_str = ""
        return coord_str

class Import(Node):
    attr_names = ('filename',)

    def __init__(self, filename, coord=None):
        self.filename = filename
        self.ast = None
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.ast or []):
            if child is not None:
                nodelist.append(("ast[%d]" % i, child))
        return tuple(nodelist)

class Include(Node):
    attr_names = ('code',)

    def __init__(self, code, coord=None):
        self.code = code
        self.coord = coord

    def children(self):
        return ()

    def __repr__(self):
        return self.code + "\n"

class Code(Node):
    attr_names = ('code',)

    def __init__(self, code, isId=False, coord=None):
        self.code = code
        self.isId = isId
        self.coord = coord

    def children(self):
        return ()

    def __repr__(self):
        return self.code

class Instructions(Node):
    attr_names = ()

    def __init__(self, instructions, coord=None):
        self.instructions = instructions
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.instructions or []):
            nodelist.append(("instructions[%d]" % i, child))
        return tuple(nodelist)

    def __repr__(self):
        repr=""
        for i, _instruction in enumerate(self.instructions):
            if i > 0:
                # if isinstance(self.instructions[i-1], Code) and isinstance(self.instructions[i], Code):
                if str(self.instructions[i-1])[-1].isalpha() and str(self.instructions[i])[0].isalpha():
                    repr += " "
            repr+=str(_instruction)
        return repr

class ParamList(Node):
    attr_names = ()

    def __init__(self, params, coord=None):
        self.params = params
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.params or []):
            nodelist.append(("params[%d]" % i, child))
        return tuple(nodelist)

class Lines(Node):
    attr_names = ()

    def __init__(self, lines, coord=None):
        self.lines = lines
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.lines or []):
            if child is not None:
                nodelist.append(("lines[%d]" % i, child))
        return tuple(nodelist)

class Variations(Node):
    attr_names = ()

    def __init__(self, vars, coord=None):
        self.vars = vars
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.vars or []):
            nodelist.append(("vars[%d]" % i, child))
        return tuple(nodelist)

    def __iter__(self):
        return iter(self.vars)

    def __repr__(self):
        return '|'.join([str(var) for var in self.vars])

class Block(Node):
    attr_names = ('start',)

    def __init__(self, start, content, end, coord=None):
        self.start = start
        self.content = content
        self.end = end
        self.coord = coord

    def children(self):
        nodelist = []
        if self.content is not None:
            nodelist.append(("content", self.content))
        return tuple(nodelist)

    def __repr__(self):
        if self.start == '{':
            return self.start + '\n' + str(self.content) + self.end
        else:
            return self.start + str(self.content) + self.end


class Def(Node):
    attr_names = ('name',)

    def __init__(self, name, vars, instructions, coord=None):
        self.name = name
        self.vars = vars
        self.instructions = instructions
        self.coord = coord

    def children(self):
        nodelist = []
        if self.vars is not None:
            nodelist.append(("vars", self.vars))
        if self.instructions is not None:
            nodelist.append(("instructions", self.instructions))
        return tuple(nodelist)

class TypeExpansion(Node):
    attr_names = ('name',)

    def __init__(self, name, coord=None):
        self.name = name
        self.coord = coord

    def children(self):
        return ()

class TypeDef(Node):
    attr_names = ('name',)

    def __init__(self, name, types, coord=None):
        self.name = name
        self.types = types
        self.coord = coord

    def children(self):
        nodelist = []
        if self.types is not None:
            nodelist.append(("types", self.types))
        return tuple(nodelist)

class TypeDecl(Node):
    attr_names = ('name',)

    def __init__(self, name, pointer_array, coord=None):
        self.name = name
        self.pointer_array = pointer_array
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.pointer_array or []):
            nodelist.append(("pointer_array[%d]" % i, child))
        return tuple(nodelist)

class PointerArray(Node):
    attr_names = ('pointers','name', 'arrays')

    def __init__(self, pointers, name, arrays, coord=None):
        self.pointers = pointers
        self.name = name
        self.arrays = arrays
        self.coord = coord

    def __repr__(self):
        string="*"*self.pointers + self.name
        if self.arrays:
            for a in self.arrays:
                string += "[" + str(a) + "]"
        return string

    def children(self):
        return ()

class Expansion(Node):
    attr_names = ('name',)

    def __init__(self, name, vars, coord=None):
        self.name = name
        self.vars = vars
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.vars or []):
            nodelist.append(("vars[%d]" % i, child))
        return tuple(nodelist)

class IfOperation(Node):
    attr_names = ()

    def __init__(self, conditions, blocks, coord=None):
        self.conditions = conditions
        self.blocks = blocks
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.conditions or []):
            if child is not None:
                nodelist.append(("conditions[%d]" % i, child))
            nodelist.append(("blocks[%d]" % i, self.blocks[i]))
        return tuple(nodelist)

class Comparison(Node):
    attr_names = ('operator',)

    def __init__(self, operator, terms, coord=None):
        self.operator = operator
        self.terms = terms
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.terms or []):
            nodelist.append(("terms[%d]" % i, child))
        return tuple(nodelist)

class Generator(Node):
    attr_names = ('name',)

    def __init__(self, name, types, instructions, includes_instruction, replacement, includes_replacement, coord=None):
        self.name = name
        self.types = types
        self.instructions = instructions
        self.includes_instruction = includes_instruction
        self.replacement = replacement
        self.includes_replacement = includes_replacement
        self.coord = coord
        self.extra = [None, None]

    def children(self):
        nodelist = []
        for i, child in enumerate(self.types or []):
            nodelist.append(("types[%d]" % i, child))
        for i, child in enumerate(self.includes_instruction or []):
            nodelist.append(("includes_instruction[%d]" % i, child))
        if self.instructions is not None:
            nodelist.append(("instructions", self.instructions))
        for i, child in enumerate(self.includes_replacement or []):
            nodelist.append(("includes_replacement[%d]" % i, child))
        if self.replacement is not None:
            nodelist.append(("replacement", self.replacement))
        return tuple(nodelist)

class Program(Node):
    attr_names = ()

    def __init__(self, statements, coord=None):
        self.statements = statements
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.statements or []):
            if child is not None:
                nodelist.append(("statements[%d]" % i, child))
        return tuple(nodelist)
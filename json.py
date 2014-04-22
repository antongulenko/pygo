from rpython.rlib.rstring import StringBuilder
from rpython.rlib.parsing.ebnfparse import parse_ebnf, make_parse_function
from rpython.rlib.parsing.tree import Symbol, Nonterminal, RPythonVisitor
from rpython.tool.pairtype import extendabletype

# This is a small RPython library for parsing json.
# The result is a simple AST that can be in turn traversed and turned into a more appropriate format.
# TODO - this is usefull and should probably be merged into rlib.

json_grammar = """
    STRING: "\\"([^\\"]|\\\\\\")*\\"";
    NUMBER: "\-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][\+\-]?[0-9]+)?";
    TRUE: "true";
    FALSE: "false";
    NULL: "null";
    IGNORE: " |\n";
    value: <STRING> | <NUMBER> | <object> | <array> | <NULL> |
           <TRUE> | <FALSE>;
    object: ["{"] ["}"] | ["{"] (entry [","])* entry ["}"];
    array: ["["] ["]"] | ["["] (value [","])* value ["]"];
    entry: STRING [":"] value;
"""

def setup_parser():
	json_regexs, json_rules, json_ast = parse_ebnf(json_grammar)
	json_parse = make_parse_function(json_regexs, json_rules, eof=True)
	return json_parse, json_ast

json_parse, json_ast = setup_parser()

# Union-Object to represent a json structure in a static way
class JsonBase(object):
    __metaclass__ = extendabletype

    is_string = is_int = is_float = is_bool = is_object = is_array = is_null = False

    def __init__(self):
        raise NotImplementedError("abstract base class")

    def tostring(self):
        raise NotImplementedError("abstract base class")

    def is_primitive(self):
        return False

    def _unpack_deep(self):
        "NON_RPYTHON"

    def value_array(self):
        raise TypeError

    def value_object(self):
        raise TypeError

    def value_string(self):
        raise TypeError

    def value_float(self):
        raise TypeError

class JsonPrimitive(JsonBase):
    def __init__(self):
        pass

    def is_primitive(self):
        return True

class JsonNull(JsonPrimitive):
    is_null = True

    def tostring(self):
        return "null"

    def _unpack_deep(self):
        return None

class JsonFalse(JsonPrimitive):
    is_false = True

    def tostring(self):
        return "false"

    def _unpack_deep(self):
        return False


class JsonTrue(JsonPrimitive):
    is_true = True

    def tostring(self):
        return "true"

    def _unpack_deep(self):
        return True

class JsonInt(JsonPrimitive):
    is_int = True

    def __init__(self, value):
        self.value = value

    def tostring(self):
        return str(self.value)

    def _unpack_deep(self):
        return self.value

class JsonFloat(JsonPrimitive):
    is_float = True

    def __init__(self, value):
        self.value = value

    def tostring(self):
        return str(self.value)

    def value_float(self):
        return self.value

    def _unpack_deep(self):
        return self.value

class JsonString(JsonPrimitive):
    is_string = True

    def __init__(self, value):
        self.value = value

    def tostring(self):
        # this function should really live in a slightly more accessible place
        from pypy.objspace.std.bytesobject import string_escape_encode
        return string_escape_encode(self.value, '"')

    def _unpack_deep(self):
        return self.value

    def value_string(self):
        return self.value

class JsonObject(JsonBase):
    is_object = True

    def __init__(self, dct):
        self.value = dct

    def tostring(self):
        return "{%s}" % ", ".join(["\"%s\": %s" % (key, self.value[key].tostring()) for key in self.value])

    def _unpack_deep(self):
        result = {}
        for key, value in self.value.iteritems():
            result[key] = value._unpack_deep()
        return result

    def value_object(self):
        return self.value

class JsonArray(JsonBase):
    is_array = True

    def __init__(self, lst):
        self.value = lst

    def tostring(self):
        return "[%s]" % ", ".join([e.tostring() for e in self.value])

    def _unpack_deep(self):
        return [e._unpack_deep() for e in self.value]

    def value_array(self):
        return self.value

json_null = JsonNull()

json_true = JsonTrue()

json_false = JsonFalse()

class Visitor(RPythonVisitor):
    def visit_STRING(self, node):
        s = node.token.source
        l = len(s) - 1
        # Strip the " characters
        if l < 0:
            return JsonString("")
        else:
            return JsonString(unescape(s)) # XXX escaping

    def visit_NUMBER(self, node):
        try:
            return JsonInt(int(node.token.source))
        except ValueError:
            return JsonFloat(float(node.token.source))

    def visit_NULL(self, node):
        return json_null

    def visit_TRUE(self, node):
        return json_true

    def visit_FALSE(self, node):
        return json_false

    def visit_object(self, node):
        dict = {}
        for entry in node.children:
            key = self.dispatch(entry.children[0])
            assert key.is_string, "Only strings allowed as object keys"
            dict[key.value_string()] = self.dispatch(entry.children[1])
        return JsonObject(dict)

    def visit_array(self, node):
        return JsonArray([self.dispatch(c) for c in node.children])

def unescape(chars):
    builder = StringBuilder(len(chars)*2) # just an estimate
    assert chars[0] == '"'
    i = 1
    while True:
        ch = chars[i]
        i += 1
        if ch == '"':
            return builder.build()
        elif ch == '\\':
            i = decode_escape_sequence(i, chars, builder)
        else:
            builder.append(ch)

def decode_escape_sequence(i, chars, builder):
    ch = chars[i]
    i += 1
    put = builder.append
    if ch == '\\':  put('\\')
    elif ch == '"': put('"' )
    elif ch == '/': put('/' )
    elif ch == 'b': put('\b')
    elif ch == 'f': put('\f')
    elif ch == 'n': put('\n')
    elif ch == 'r': put('\r')
    elif ch == 't': put('\t')
    elif ch == 'u':
        raise ValueError("unicode escape sequence not supported yet") # XXX
    else:
        raise ValueError("Invalid \\escape: %s" % (ch, ))
    return i

def loads(string):
    ast = json_parse(string)
    transformed = json_ast().transform(ast)
    return Visitor().dispatch(transformed)

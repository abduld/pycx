import unittest
import inspect
import ast
import cgen as c
from functools import wraps


class Return(c.Generable):
    def __init__(self, value):
        self.value = value

    def generate(self):
        yield "return %s;" % (self.value)

class FieldAccess(c.Generable):
    def __init__(self, val, attr):
        self.val = val
        self.attr = attr

    def generate(self):
        yield "%s.%s" % (self.val, self.attr)


class BinOp(c.Generable):
    def __init__(self, op, lvalue, rvalue):
        self.op = op
        self.lvalue = lvalue
        self.rvalue = rvalue

    def generate(self):
        yield "%s %s %s" % (self.lvalue, self.op, self.rvalue)

def ctype(ty):
    if ty == "int64" or ty == "i64":
        return "int64_t"
    elif ty == "uint64" or ty == "u64":
        return "uint64_t"
    elif ty == "int" or ty == "int32" or ty == "i32":
        return "int32_t"
    elif ty == "uint32" or ty == "u32":
        return "uint32_t"
    elif ty == "int16" or ty == "i16":
        return "int16_t"
    elif ty == "uint16" or ty == "u16":
        return "uint16_t"
    elif ty == "int8" or ty == "i8":
        return "int8_t"
    elif ty == "uint8" or ty == "u8":
        return "uint8_t"
    elif ty == "float" or ty == "float32" or ty == "f32":
        return "float"
    elif ty == "double" or ty == "float64" or ty == "f64":
        return "double"
    else:
        raise ValueError("unable to map dtype '%s'" % ctype)

def show_ast(func):
    def wrapper():
        i = inspect.getsource(func)
        tree = ast.parse(i)

        class ASTWrapper(ast.NodeTransformer):
            def generic_visit(self, node):
                if isinstance(node, str):
                    return node
                print(ast.dump(node))
                print('unable to find visit_' + node.__class__.__name__)
                return node
            def get_visitor(self, node):
                method = 'visit_' + node.__class__.__name__
                visitor = getattr(self, method, self.generic_visit)
                return visitor
            def accept(self, node):
                visitor = self.get_visitor( node)
                return visitor(node)
            def visit_Module(self, node):
                return self.accept(node.body[0])
            def visit_list(self, node):
                return c.Block([self.accept(e) for e in node])
            def visit_Return(self, node):
                return Return(self.accept(node.value))
            def visit_BinOp(self, node):
                left = self.accept(node.left)
                right = self.accept(node.right)
                op = self.accept(node.op)
                return BinOp(op, left, right)
            def visit_Name(self, node):
                return node.id
            def visit_Add(self, node):
                return "+"
            def visit_Attribute(self, node):
                return FieldAccess(
                    self.accept(node.value),
                    self.accept(node.attr)
                )
            def visit_Assign(self, node):
                return c.Assign(
                    self.accept(node.targets[0]),
                    self.accept(node.value)
                )
            def visit_FunctionDef(self, node):
                func = c.FunctionBody(
                    c.FunctionDeclaration(c.Const(c.Pointer(c.Value("void", node.name))), []),
                    self.accept(node.body)
                )
                return func
            def visit_Expr(self, node):
                return self.accept(node.value)
            def visit_Call(self, node):
                if node.func.id == "typed":
                    ty = ctype(node.args[1].id)
                    return c.Value(ty, self.accept(node.args[0]))
                return node
            def visit_Num(self, node):
                if isinstance(node.n, int):
                    return ast.Call(func=ast.Name(id='Integer', ctx=ast.Load()),
                                    args=[node], keywords=[])
                return node
        newast = ASTWrapper().visit(tree)
        # return ast.dump(newast)
        return newast
    return wrapper


@show_ast
def add(x, y):
    typed(idx, int)
    idx = threadIdx.x
    return x + y

class MyTest(unittest.TestCase):
    def test(self):
        print(add())


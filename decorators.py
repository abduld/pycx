import unittest
import inspect
import ast
import cgen as c
from functools import wraps


class Return(c.Generable):
    def __init__(self, value):
        self.value = value

    def generate(self):
        yield "return  %s;" % (self.value)

class BinOp(c.Generable):
    def __init__(self, op, lvalue, rvalue):
        self.op = op
        self.lvalue = lvalue
        self.rvalue = rvalue

    def generate(self):
        yield "%s %s %s" % (self.lvalue, self.op, self.rvalue)

def show_ast(func):
    def wrapper():
        i = inspect.getsource(func)
        tree = ast.parse(i)

        class ASTWrapper(ast.NodeTransformer):
            def generic_visit(self, node):
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
                print(ast.dump(node))
                left = self.accept(node.left)
                right = self.accept(node.right)
                op = self.accept(node.op)
                return BinOp(op, left, right)
            def visit_Name(self, node):
                return node.id
            def visit_Add(self, node):
                return "+"
            def visit_FunctionDef(self, node):
                func = c.FunctionBody(
                    c.FunctionDeclaration(c.Const(c.Pointer(c.Value("char", node.name))), []),
                    self.accept(node.body)
                )
                return func
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
    return x + y

class MyTest(unittest.TestCase):
    def test(self):
        print(add())


import unittest
import inspect
import ast
from functools import wraps

def show_ast(func):
    @wraps(func)
    def wrapper():
        i = inspect.getsource(func)
        tree = ast.parse(i)
        return ast.dump(tree)
    return wrapper


@show_ast
def add(x, y):
    return x + y

class MyTest(unittest.TestCase):
    def test(self):
        print(add())


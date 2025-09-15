import ast

from mathphysicslib.expresso import Constant,Mul, Add, Var, Pow

def parse_to_func(func: str):
    if not isinstance(func, str):
        raise TypeError("expression must be in string form")
    node = ast.parse(func, mode="eval").body
    return convert(node)

def convert(node):
    
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return Constant(node.value)
        raise TypeError("Constant type is invalid")

    if isinstance(node, ast.Name):
        return Var(node.id)

    if isinstance(node, ast.BinOp):
        if isinstance(node.op, ast.Add):
            return Add(convert(node.left), convert(node.right))
        if isinstance(node.op, ast.Mult):
            return Mul(convert(node.left), convert(node.right))
        if isinstance(node.op, ast.Pow):
            return Pow(convert(node.left), convert(node.right))
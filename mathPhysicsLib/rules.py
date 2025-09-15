from mathphysicslib.expresso import Constant,Mul, Add, Var, Pow
from mathphysicslib.ast_parser import parse_to_func, convert
import math

def power_rule(base, exponent):
    if isinstance(base, Var) and isinstance(exponent, Constant):
        return Mul(Constant(exponent.value),Pow(base, Constant(exponent.value - 1)))
    elif isinstance(base, Constant):
        return Constant(0)

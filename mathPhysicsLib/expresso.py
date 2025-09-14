class Expr:
    pass
class Constant:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return str(self.value)    
    
class Var:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name

class Add:
    def __init__(self, *terms):
        self.terms = terms
    def __repr__(self):
        return "(" + " + ".join(map(str, self.terms)) + ")"
    
class Mul:
    def __init__(self, *factors):
        self.factors = factors
    def __repr__(self):
        return "(" + " * ".join(map(str, self.factors)) + ")"
    
class Pow:
    def __init__(self,base, *exponent):
        self.base = base
        self.exponent = exponent
    def __repr__(self):
        return f"({self.base} ** {self.exponent})"
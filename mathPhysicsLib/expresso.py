class Expr:
    pass # Base class for all expressions (placeholder)

class Constant(Expr):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return str(self.value)
    def __eq__(self, other):
        # Equality works only if other is also Constant and has same value
        if isinstance(other, Constant):
            return self.value == other.value
        return False
    
def constant_conversion(const):
    # Helper: wrap int/float into Constant (excludes bools)
    if  (isinstance(const, int) or isinstance(const, float)) and not isinstance(const, bool):
        return Constant(const)
    else:
        return const
    
class Var(Expr):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name
    def __eq__(self, other):
        # Equality works only if other is Var with same name
        if isinstance(other, Var):
            return self.name == other.name
        return False

def variadic_flatten(expr, func_type):
    """
      Flatten nested variadic expressions like Add(Add(...)) or Mul(Mul(...))
      into a single-level expression.
      """
    flattened = []
    if func_type not in variadic_field:
        raise TypeError(f"Variadic flattening unsupported for {getattr(func_type, '__name__', func_type)}")
    field = variadic_field[func_type]
    if not isinstance(expr, func_type):
        return expr
    for x in getattr(expr, field):
        if isinstance(x, func_type):
            # Recursive flattening of nested structure
            flattened.extend(getattr(variadic_flatten(x, func_type), field))
        else:
            flattened.append(x)
    return func_type(*flattened)

class Add(Expr):
    def __init__(self, *terms):
        self.terms = []
        total = 0 # sum of constant
        for i in terms:
            i = constant_conversion(i)
            if isinstance(i, Constant):
                total = total + i.value # fold constants together
            elif isinstance(i, Add):
                # flatten nested Adds
                i = variadic_flatten(i, Add)
                for j in i.terms:
                    j = constant_conversion(j)
                    if isinstance(j, Constant):
                        total = total + j.value
                    else:
                        self.terms.append(j)
            else:
                self.terms.append(i)
        if total != 0:        
            self.terms.append(Constant(total)) # keep final constant if nonzero
        if not self.terms:
            self.terms.append(Constant(0)) # ensure empty sum becomes 0
                
    def __repr__(self):
        # Pretty-print as "(a + b + c)"
        return "(" + " + ".join(map(str, self.terms)) + ")"
    
    def __eq__(self, other):
        # Compare ignoring term order by sorting string representations (will make proper key later)
        if not isinstance(other, Add):
            return False
        return sorted(self.terms, key=str) == sorted(other.terms, key=str)

class Mul(Expr):
    def __init__(self, *factors):
        self.factors = factors # placeholder: no flattening/constant folding yet
    def __repr__(self):
        return "(" + " * ".join(map(str, self.factors)) + ")"

# Mapping of variadic classes to their attribute fields
variadic_field = {Add:"terms", Mul:"factors"}

class Pow(Expr):
    def __init__(self,base, exponent): # placeholder: no flattening/constant folding yet
        self.base = base
        self.exponent = exponent
    def __repr__(self):
        return f"({self.base} ** {self.exponent})"
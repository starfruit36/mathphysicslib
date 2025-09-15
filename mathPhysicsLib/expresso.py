class Expr:
    pass # Base class for all expressions (placeholder)

class Constant(Expr):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return str(self.value)
    
    def key(self):
        v = self.value
        if v == 0:
            return ("Const", 0)
        if isinstance(v, float):
            if v.is_integer():
                return ("Const", int(v))
            return ("Const", v)
        if isinstance(v, int):
            return ("Const", v)
        return ("Const", v)
    
    def __eq__(self, other):
        # Equality works only if other is also Constant and has same value
        return isinstance(other, Constant) and self.key() == other.key()
    def __hash__(self):
        return hash(self.key())
    
def constant_conversion(const):
    # Helper: wrap int/float into Constant (excludes bools)
    if  (isinstance(const, int) or isinstance(const, float)) and not isinstance(const, bool):
        return Constant(const)
    elif isinstance(const, bool):
        raise TypeError("Boolean expression is not supported")
    else:
        return const
    
class Var(Expr):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name
    def key(self):
        n = self.name
        return ("Var", n)
    def __eq__(self, other):
        # Equality works only if other is Var with same name
        return isinstance(other, Var) and self.key() == other.key()
    def __hash__(self):
        return hash(self.key())

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
            self.terms = [Constant(0)] # ensure empty sum becomes 0
                
    def __repr__(self):
        # Pretty-print as "(a + b + c)"
        return "(" + " + ".join(map(str, self.terms)) + ")"

    def key(self):
        child_keys = [t.key() for t in self.terms]
        not_const = []
        consts = []
        for i, j in zip(self.terms, child_keys):
            if isinstance(i, Constant):
                consts.append(i.value)
            else:
                not_const.append(j)
        if consts:
            const_val = consts[0]
        else: 
            const_val = 0
        not_const_sorted = tuple(sorted(not_const))
        return ("Add", not_const_sorted, const_val)

    def __eq__(self, other):
        return isinstance(other, Add) and self.key() == other.key()
    
    def __hash__(self):
        return hash(self.key())

class Mul(Expr):
    def __init__(self, *factors):
        self.factors = []
        product = 1  # product of constant
        for i in factors:
            i = constant_conversion(i)
            if isinstance(i, Constant) and i.value == 0:
                self.factors = [Constant(0)]
                return
            elif isinstance(i, Constant) and i.value != 0:
                product = product * i.value  # fold constants together
            elif isinstance(i, Mul):
                # flatten nested Mul
                i = variadic_flatten(i, Mul)
                for j in i.factors:
                    j = constant_conversion(j)
                    if isinstance(j, Constant):
                        product = product * j.value
                    else:
                        self.factors.append(j)
            else:
                self.factors.append(i)
        if product != 1:
            self.factors.append(Constant(product))  # keep final constant if not 1
        if not self.factors:
            self.factors = [Constant(1)]  # ensure empty product becomes 1
    def __repr__(self):
        return "(" + " * ".join(map(str, self.factors)) + ")"
    
    def key(self):
        child_keys = [t.key() for t in self.factors]
        not_const = []
        consts = []
        for i, j in zip(self.factors, child_keys):
            if isinstance(i, Constant):
                consts.append(i.value)
            else:
                not_const.append(j)
        if consts:
            const_val = consts[0]
        else: 
            const_val = 1
        not_const_sorted = tuple(sorted(not_const))
        return ("Mul", not_const_sorted, const_val)

    def __eq__(self, other):
        # Compare ignoring term order by sorting string representations (will make proper key later)
        return isinstance(other, Mul) and self.key() == other.key()
    
    def __hash__(self):
        return hash(self.key())

# Mapping of variadic classes to their attribute fields
variadic_field = {Add:"terms", Mul:"factors"}

class Pow(Expr):
    def __init__(self,base, exponent):
        self.base = constant_conversion(base)
        self.exponent = constant_conversion(exponent)

    @staticmethod
    def pow_fold(base, exponent):
        """
        Smart factory for Pow that returns the most reduced Expr it safely can.
         - Only fold when result is exact.
         - Handle trivial identities first.
         - Constant^constant: (non neg ints only) -> Constant.
         - Power-of-power: ( (x**a)**b) -> x**(a*b) for integer a,b.
         - Otherwise return Pow(base, exponent) with children normalized via constant_conversion.
        Notes:
         - 0**0 -> raises 
         - 0**negative -> raises Division by zero
         - We intentionally do not distribute over products/sums or evaluate floats here to avoid rounding errors.
        """
        base = constant_conversion(base)
        exponent = constant_conversion(exponent)
        # Trivial identities & guarded zero cases
        if isinstance(exponent, Constant) and exponent.value == 0:
            if isinstance(base, Constant) and base.value == 0:
                raise ValueError("Can't compute 0**0")
            return Constant(1)
        if isinstance(exponent, Constant) and exponent.value == 1:
            return base
        if isinstance(base, Constant) and base.value == 1:
            return Constant(1)
        if isinstance(base, Constant) and base.value == 0:
            if isinstance(exponent, Constant) and exponent.value > 0:
                return Constant(0)
            elif isinstance(exponent, Constant) and exponent.value == 0:
                raise ValueError("Can't compute 0**0")
            elif isinstance(exponent, Constant) and exponent.value < 0:
                raise ValueError("Division by zero")
        # Fold int^ non neg int
        if (isinstance(base, Constant) and isinstance(exponent, Constant) 
            and type(base.value) == int and type(exponent.value) == int
            and exponent.value >= 0):
            return Constant(base.value**exponent.value)            
        # (x**a)**b -> x**(a*b), when a,b are ints
        if isinstance(base, Pow):
            inner = Pow.pow_fold(base.base, base.exponent)
            if isinstance(inner, Pow):
                if (isinstance(exponent, Constant) and isinstance(inner.exponent, Constant)
                    and isinstance(exponent.value, int) and isinstance(inner.exponent.value, int)):
                    prod = exponent.value * inner.exponent.value
                    return Pow.pow_fold(inner.base, Constant(prod))
                # Can't combine exponents, keep folded inner
                return Pow(inner, exponent)
            else:
                # inner become non Pow, try folding at inner
                return Pow.pow_fold(inner, exponent)
        # Keep as Pow    
        return Pow(base, exponent)
                     
    def __repr__(self):
        return f"({self.base} ** {self.exponent})"
    def key(self):
        return ("Pow", self.base.key(), self.exponent.key())
    def __eq__(self, other):
        # Compare base & exponent as-is
        return isinstance(other, Pow) and self.key() == other.key()
    def __hash__(self):
        return hash(self.key())
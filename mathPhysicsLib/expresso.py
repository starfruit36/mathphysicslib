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
    elif isinstance(const, bool):
        raise TypeError("Boolean expression is not supported")
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
            self.factors.append(Constant(1))  # ensure empty product becomes 1
            
    def __repr__(self):
        return "(" + " * ".join(map(str, self.factors)) + ")"

    def __eq__(self, other):
        # Compare ignoring term order by sorting string representations (will make proper key later)
        if not isinstance(other, Mul):
            return False
        return sorted(self.factors, key=str) == sorted(other.factors, key=str)

# Mapping of variadic classes to their attribute fields
variadic_field = {Add:"terms", Mul:"factors"}

class Pow(Expr):
    def __init__(self,base, exponent):
        self.base = base
        self.exponent = exponent

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

    def __eq__(self, other):
        # Compare base & exponent as-is
        if not isinstance(other, Pow):
            return False
        return self.base == other.base and self.exponent == other.exponent
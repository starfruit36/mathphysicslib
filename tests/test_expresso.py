import pytest


from mathphysicslib.expresso import Add, Mul, Var, Constant, Pow, variadic_field
from mathphysicslib.expresso import constant_conversion, variadic_flatten

def test_constant_conversion():
    c1 = constant_conversion(3)
    c2 = constant_conversion(2.5)

    assert isinstance(c1, Constant) and c1.value == 3
    assert isinstance(c2, Constant) and c2.value == 2.5

def test_constant_conversion_non_numbers():
    x = Var("x")
    obj = object()
    assert constant_conversion(x) is x
    assert constant_conversion(obj) is obj

def test_variadic_flatten_nested_adds():
    x, y, z = Var("x"), Var("y"), Var("z")
    nested = Add(x, Add(y, Add(z, Constant(1))))
    flat = variadic_flatten(nested, Add)
    # all terms at one level, constants folded by Add constructor
    assert isinstance(flat, Add)
    # Check content types 
    assert sorted(map(str, flat.terms)) == sorted([str(x), str(y), str(z), "1"])

def test_variadic_flatten_input_not_instance():
    x = Var("x")
    out = variadic_flatten(x, Add)
    assert out is x  

def test_variadic_flatten_wrong_type():
    x = Var("x")
    with pytest.raises(TypeError):
        variadic_flatten(Add(x), Pow)

def test_add_folds_constants():
    x = Var("x")
    expr = Add(x, Constant(2), Constant(3))
    # Should become x + 5
    constants = [t for t in expr.terms if isinstance(t, Constant)]
    non_consts = [t for t in expr.terms if not isinstance(t, Constant)]
    assert len(constants) == 1 and constants[0].value == 5
    assert non_consts == [x]

def test_add_sum_zero():
    expr = Add(Constant(2), Constant(-2))
    # Should normalize to just Constant(0)
    assert len(expr.terms) == 1 and isinstance(expr.terms[0], Constant) and expr.terms[0].value == 0

def test_add_empty_constructor():
    expr = Add()
    assert len(expr.terms) == 1 and isinstance(expr.terms[0], Constant) and expr.terms[0].value == 0

def test_add_folds_inner_constants():
    x, y = Var("x"), Var("y")
    expr = Add(Add(Constant(1), x), Add(y, Constant(2)))
    # Expect x + y + 3
    constants = [t for t in expr.terms if isinstance(t, Constant)]
    syms = [t for t in expr.terms if not isinstance(t, Constant)]
    assert len(constants) == 1 and constants[0].value == 3
    assert sorted(map(str, syms)) == sorted([str(x), str(y)])

def test_add_order_insensitive():
    x, y = Var("x"), Var("y")
    a = Add(x, y, Constant(3))
    b = Add(Constant(1), y, x, Constant(2))  # folds to x + y + 3
    assert a == b

def test_add_inequality_with_different_terms():
    x, y = Var("x"), Var("y")
    a = Add(x, y)
    b = Add(x, x)
    assert a != b
    
def test_mul_flattens():
    x = Var("x")
    expr = Mul(Mul(2, x), 3)  # Flatten to (x * 6) or (6 * x)
    factors = expr.factors
    assert any(isinstance(f, Var) and f.name == "x" for f in factors)
    assert any(isinstance(f, Constant) and f.value == 6 for f in factors)

def test_mul_zero():
    x = Var("x")
    expr = Mul(x, 7, 0, Mul(3, "x"))
    # If any factor is 0, product is 0
    assert len(expr.factors) == 1
    assert isinstance(expr.factors[0], Constant) and expr.factors[0].value == 0

def test_mul_no_factors():
    expr = Mul()  # empty product -> 1
    assert len(expr.factors) == 1
    assert isinstance(expr.factors[0], Constant) and expr.factors[0].value == 1

def test_mul_order_insensitive():
    x, y = Var("x"), Var("y")
    a = Mul(2, x, y)
    b = Mul(y, 2, x)
    assert a == b

def pf(base, exp):
    return Pow.pow_fold(base, exp)

def test_pow_trivial_identities():
    x = Var("x")
    assert pf(x, 1) == x
    assert pf(1, x) == Constant(1)
    assert pf(x, 0) == Constant(1)

def test_pow_zero_base():
    assert pf(0, 3) == Constant(0)
    with pytest.raises(ValueError):
        pf(0, 0)
    with pytest.raises(ValueError):
        pf(0, -1)

def test_pow_fold():
    assert pf(2, 3) == Constant(8)
    assert pf(0, 5) == Constant(0)
    assert pf(-2, 5) == Constant(-32)   

def test_pow_power_of_power():
    x = Var("x")
    # (x**4)**5 -> x**20
    folded = pf(Pow(Var("x"), Constant(4)), Constant(5))
    assert isinstance(folded, Pow)
    assert folded.base == x
    assert isinstance(folded.exponent, Constant) and folded.exponent.value == 20

def test_pow_equality():
    x = Var("x")
    a = Pow(Pow(x, Constant(4)), Constant(3))
    b = Pow(x, Constant(12))
    assert a != b            # structural
    assert pf(a.base, a.exponent) == b  # after folding they match

def test_variadic_registry():
    assert variadic_field.get(Add) == "terms"
    assert variadic_field.get(Mul) == "factors"
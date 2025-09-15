import pytest


from mathphysicslib.expresso import Add, Mul, Var, Constant, Pow, variadic_field
from mathphysicslib.expresso import constant_conversion, variadic_flatten

def test_constant_conversion():
    c1 = constant_conversion(3)
    c2 = constant_conversion(2.5)
    t  = constant_conversion(True)   # bools must NOT be wrapped
    f  = constant_conversion(False)

    assert isinstance(c1, Constant) and c1.value == 3
    assert isinstance(c2, Constant) and c2.value == 2.5
    assert not isinstance(t, Constant) and t is True
    assert not isinstance(f, Constant) and f is False

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

def test_add_preserves_non_numeric_terms():
    # True/False should NOT be folded as 1/0
    expr = Add(True, Var("x"), Constant(2))
    # Expect terms: True, x, 2  (2 may be folded if other constants exist)
    assert any(t is True for t in expr.terms)
    assert any(isinstance(t, Var) and t.name == "x" for t in expr.terms)
    assert any(isinstance(t, Constant) and t.value == 2 for t in expr.terms)

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

def test_variadic_registry():
    assert variadic_field.get(Add) == "terms"
    assert variadic_field.get(Mul) == "factors"
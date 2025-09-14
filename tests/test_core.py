import pytest
def test_validate_var_name_good():
    from mathphysicslib.core import validate_var_name
    validate_var_name("x")

@pytest.mark.parametrize("bad", [None, 123, 1.2, [], (), {}, object()])
def test_validate_var_name_type_error(bad):
    from mathphysicslib.core import validate_var_name
    with pytest.raises(TypeError) as e:
        validate_var_name(bad)
    assert str(e.value) == "variable type is invalid"

def test_validate_var_name_empty_string():
    from mathphysicslib.core import validate_var_name
    with pytest.raises(ValueError) as e:
        validate_var_name("")
    assert str(e.value) == "variable cannot be empty"
    with pytest.raises(ValueError) as e:
        validate_var_name("         ")
    assert str(e.value) == "variable cannot be empty"

def test_normalize_string_order_positive():
    from mathphysicslib.core import normalize_respect_to
    assert normalize_respect_to("x", order=3) == ["x", "x", "x"]

def test_normalize_string_order_zero():
    from mathphysicslib.core import normalize_respect_to
    assert normalize_respect_to("x", order=0) == []

def test_normalize_string_order_negative():
    from mathphysicslib.core import normalize_respect_to
    with pytest.raises(ValueError) as e:
        normalize_respect_to("x", order=-1)
    assert str(e.value) == "order cannot be negative"

def test_normalize_string_order_wrong_type():
    from mathphysicslib.core import normalize_respect_to
    with pytest.raises(TypeError) as e:
        normalize_respect_to("x", order=1.5)
    assert str(e.value) == "order must be an integer"

def test_normalize_empty_string():
    from mathphysicslib.core import normalize_respect_to
    with pytest.raises(ValueError) as e:
        normalize_respect_to("", order=1)
    assert str(e.value) == "variable cannot be empty"

def test_normalize_list_good():
    from mathphysicslib.core import normalize_respect_to
    assert normalize_respect_to(["x", "y", "x"]) == ["x", "y", "x"]

def test_normalize_tuple_good():
    from mathphysicslib.core import normalize_respect_to
    assert normalize_respect_to(("theta", "r")) == ["theta", "r"]

@pytest.mark.parametrize("bad", ["", 0, None, 1.2, [], {}, object()])
def test_normalize_list_with_bad_element(bad):
    from mathphysicslib.core import normalize_respect_to
    with pytest.raises((TypeError, ValueError)) as e:
        normalize_respect_to(["x", bad, "y"])
    msg = str(e.value)
    assert msg in {"variable cannot be empty", "variable type is invalid"}

def test_normalize_dict_ok():
    from mathphysicslib.core import normalize_respect_to
    d = {"x": 2, "y": 1}  # insertion order
    assert normalize_respect_to(d) == ["x", "x", "y"]

def test_normalize_dict_zero_count():
    from mathphysicslib.core import normalize_respect_to
    assert normalize_respect_to({"x": 0, "y": 0}) == []

def test_normalize_dict_negative_count():
    from mathphysicslib.core import normalize_respect_to
    with pytest.raises(ValueError) as e:
        normalize_respect_to({"x": -1})
    assert str(e.value) == "number of variable appearances cannot be negative"

def test_normalize_dict_nonint_appearance():
    from mathphysicslib.core import normalize_respect_to
    with pytest.raises(TypeError) as e:
        normalize_respect_to({"x": 1.2})
    assert str(e.value) == "number of variable appearances is invalid"

def test_normalize_dict_bad_key_type():
    from mathphysicslib.core import normalize_respect_to
    with pytest.raises(TypeError) as e:
        normalize_respect_to({123: 1})
    assert str(e.value) == "variable type is invalid"

def test_normalize_dict_empty_key():
    from mathphysicslib.core import normalize_respect_to
    with pytest.raises(ValueError) as e:
        normalize_respect_to({"": 1})
    assert str(e.value) == "variable cannot be empty"

@pytest.mark.parametrize("bad", [None, 1, 3.14, {"x"}, object()])
def test_normalize_unsupported_type(bad):
    from mathphysicslib.core import normalize_respect_to
    with pytest.raises(TypeError) as e:
        normalize_respect_to(bad)
    assert str(e.value) == "variable type is invalid"

def test_derivative_empty_path():
    from mathphysicslib.core import derivative
    sentinel = object()
    assert derivative(sentinel, "x", order=0) is sentinel

def test_derivative_empty_func():
    from mathphysicslib.core import derivative
    with pytest.raises(ValueError) as e:
        derivative(None, "x", order=1)
    assert str(e.value) == "function cannot be empty"

def test_integral_empty_path():
    from mathphysicslib.core import integral
    sentinel = object()
    assert integral(sentinel, "x", order=0) is sentinel

def test_integral_empty_func():
    from mathphysicslib.core import integral
    with pytest.raises(ValueError) as e:
        integral(None, "x", order=1)
    assert str(e.value) == "function cannot be empty"
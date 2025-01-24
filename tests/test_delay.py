import pytest
from genia.interpreter import Delay, Interpreter

@pytest.fixture
def interpreter():
    return Interpreter()

# 1. Test if a delay evaluates correctly once
def test_delay_evaluates_once(interpreter):
    called = [0]

    def expensive():
        called[0] += 1
        return 42

    d = Delay(expensive)
    assert d.value(interpreter) == 42
    assert d.value(interpreter) == 42
    assert called[0] == 1

# 2. Test if delay caches the result
def test_delay_caches_result(interpreter):
    d = Delay(lambda: 42)
    assert d.value(interpreter) == 42
    assert d.value(interpreter) == 42

# 3. Test if delay handles exceptions correctly
def test_delay_raises_exception(interpreter):
    def error_func():
        raise ValueError("Test Error")

    d = Delay(error_func)
    with pytest.raises(ValueError, match="Test Error"):
        d.value(interpreter)

# 4. Test if delay rethrows exceptions on subsequent accesses
def test_delay_rethrows_exception(interpreter):
    def error_func():
        raise ValueError("Persistent Error")

    d = Delay(error_func)
    for _ in range(3):
        with pytest.raises(ValueError, match="Persistent Error"):
            d.value(interpreter)

# 5. Test if delay works in a multi-threaded environment
def test_delay_thread_safety(interpreter):
    from concurrent.futures import ThreadPoolExecutor

    called = [0]

    def expensive():
        called[0] += 1
        return 42

    d = Delay(expensive)

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(lambda _: d.value(interpreter), range(10)))

    assert all(result == 42 for result in results)
    assert called[0] == 1

# 6. Test if delay handles non-callable expressions
def test_delay_non_callable_expression(interpreter):
    d = Delay(100)
    assert d.value(interpreter) == 100

# 7. Test if delay can be used in a list
def test_delay_in_list(interpreter):
    delayed_list = [Delay(lambda i=i: i * 2) for i in range(5)]
    assert delayed_list[0].value(interpreter) == 0
    assert delayed_list[3].value(interpreter) == 6

# 8. Test if delay returns the correct type
def test_delay_returns_correct_type(interpreter):
    d = Delay(lambda: "test")
    assert d.value(interpreter) == "test"

# 9. Test if multiple delays work independently
def test_multiple_delays(interpreter):
    d1 = Delay(lambda: 1)
    d2 = Delay(lambda: 2)
    assert d1.value(interpreter) == 1
    assert d2.value(interpreter) == 2

# 10. Test if delay handles functions with side effects
def test_delay_with_side_effects(interpreter):
    side_effect_list = []

    def side_effect_func():
        side_effect_list.append("effect")
        return len(side_effect_list)

    d = Delay(side_effect_func)
    assert d.value(interpreter) == 1
    assert d.value(interpreter) == 1
    assert side_effect_list == ["effect"]

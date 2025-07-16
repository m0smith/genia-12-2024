import random
from genia.interpreter import GENIAInterpreter


def test_randrange_foreign_function():
    random.seed(0)
    interp = GENIAInterpreter()
    assert interp.run("randrange(6)") == 3
    random.seed(0)
    assert interp.run("randrange(1, 6)") == 4


def test_randint_native_function():
    random.seed(0)
    interp = GENIAInterpreter()
    result = interp.run("randint(1, 6)")
    assert result == 4


def test_roll_function():
    random.seed(0)
    code = """
define roll(sides) -> roll(1, sides)
define roll(0, _) -> 0
define roll(n, sides) -> randint(1, sides) + roll(n - 1, sides)
roll(2, 6)
"""
    interp = GENIAInterpreter()
    result = interp.run(code)
    assert result == 8



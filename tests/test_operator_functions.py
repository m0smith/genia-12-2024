import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from genia.interpreter import GENIAInterpreter


def run(code: str):
    interp = GENIAInterpreter()
    return interp.run(code)


def test_add_operator_as_function():
    assert run("+(1,2,3,4)") == 10


def test_mul_operator_no_args():
    assert run("*()") == 1


def test_operator_as_argument():
    code = """
    define compose(f,g) -> define(a,b) -> f(g(a,b))
    define double(x) -> x * x
    f = compose(double, +)
    f(2,3)
    """
    assert run(code) == 25

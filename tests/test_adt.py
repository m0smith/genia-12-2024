import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from genia.interpreter import GENIAInterpreter


def test_adt_constructor():
    code = """
    data Option = Some(a) | None
    Some(5)
    """
    interp = GENIAInterpreter()
    result = interp.run(code)
    assert result == {'type': 'Option', 'ctor': 'Some', 'values': [5]}


def test_adt_pattern_match():
    code = """
    data Option = Some(a) | None
    fn unwrap(Some(x)) -> x | (None()) -> 0
    unwrap(Some(7))
    """
    interp = GENIAInterpreter()
    assert interp.run(code) == 7


def test_adt_pattern_match_none():
    code = """
    data Option = Some(a) | None
    fn unwrap(Some(x)) -> x | (None()) -> 0
    unwrap(None())
    """
    interp = GENIAInterpreter()
    assert interp.run(code) == 0


def test_trio_constructor():
    code = """
    data Trio = Trio(a, b, c)
    Trio(1, 2, 3)
    """
    interp = GENIAInterpreter()
    result = interp.run(code)
    assert result == {'type': 'Trio', 'ctor': 'Trio', 'values': [1, 2, 3]}


def test_trio_pattern_match():
    code = """
    data Trio = Trio(a, b, c)
    fn sum_trio(Trio(x, y, z)) -> x + y + z
    sum_trio(Trio(1, 2, 3))
    """
    interp = GENIAInterpreter()
    assert interp.run(code) == 6


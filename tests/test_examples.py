import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from genia.interpreter import GENIAInterpreter


def test_board_full_without_ffi():
    code = """
    TRUE  = 1 == 1
    FALSE = 1 == 2

    define equal?(x) -> define(y) -> x == y | (x, y) -> x == y

    define every?(pred) -> define(list) -> every?(pred, list)
    define every?(_, []) -> TRUE
    define every?(pred, [head, ..tail]) when pred(head) -> every?(pred, tail)
    define every?(pred, [head, ..tail]) -> FALSE

    define board_full(b) -> every?(define(x) -> x != " ", b)
    board_full(["X","O","X","O","X","O","X","O","X"])
    """
    interp = GENIAInterpreter()
    assert interp.run(code) is True


def test_duplicate_with_reduce():
    code = """
    define reduce(f, acc) -> define(list) -> reduce(f, acc, list)
    define reduce(_, acc, []) -> acc
    define reduce(func, acc, [f, ..r]) -> reduce(func, func(acc, f), r)

    define duplicates(v, n) -> reduce(define(acc, _) -> [..acc, v], [], 1..n)
    duplicates(5, 3)
    """
    interp = GENIAInterpreter()
    assert interp.run(code) == [5,5,5]

def test_string_pattern_matching():
    code = """
    define switch("X") -> "O" | (_) -> "X"
    switch("X")
    """
    interp = GENIAInterpreter()
    assert interp.run(code) == "O"
    
def test_simple_assigment():
    code = """
    x = 1
    """
    interp = GENIAInterpreter()
    assert interp.run(code) == 1
    
def test_local_assigment():
    code = """
    define f() -> (x = 2)
    f()
    """
    interp = GENIAInterpreter()
    assert interp.run(code) == 2

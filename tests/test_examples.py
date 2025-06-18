import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from genia.interpreter import GENIAInterpreter


def test_board_full_without_ffi():
    code = """
    TRUE  = 1 == 1
    FALSE = 1 == 2

    fn equal?(x) -> fn(y) -> x == y | (x, y) -> x == y

    fn every?(pred) -> fn(list) -> every?(pred, list)
    fn every?(_, []) -> TRUE
    fn every?(pred, [head, ..tail]) when pred(head) -> every?(pred, tail)
    fn every?(pred, [head, ..tail]) -> FALSE

    fn board_full(b) -> every?(fn(x) -> x != " ", b)
    board_full(["X","O","X","O","X","O","X","O","X"])
    """
    interp = GENIAInterpreter()
    assert interp.run(code) is True


def test_duplicate_with_reduce():
    code = """
    fn reduce(f, acc) -> fn(list) -> reduce(f, acc, list)
    fn reduce(_, acc, []) -> acc
    fn reduce(func, acc, [f, ..r]) -> reduce(func, func(acc, f), r)

    fn duplicates(v, n) -> reduce(fn(acc, _) -> [..acc, v], [], 1..n)
    duplicates(5, 3)
    """
    interp = GENIAInterpreter()
    assert interp.run(code) == [5,5,5]


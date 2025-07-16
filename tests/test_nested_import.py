import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from genia.interpreter import GENIAInterpreter


def test_nested_module_import():
    code = """
    define create_board() -> foreign "genia.hosted.tictactoe.create_board"
    define check_win(b, p) -> foreign "genia.hosted.tictactoe.check_win"
    board = create_board()
    check_win(board, "X")
    """
    interp = GENIAInterpreter()
    result = interp.run(code)
    assert result is False

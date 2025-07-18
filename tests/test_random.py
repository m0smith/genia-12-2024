import random
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from genia.interpreter import GENIAInterpreter

SCRIPT_PATH = Path(__file__).resolve().parent.parent / 'scripts' / 'dice.genia'
FILE_CONTENT = SCRIPT_PATH.read_text()

def run(code: str):
    interp = GENIAInterpreter()
    return interp.run(FILE_CONTENT + '\n' + code, args=[])
BASE_FUNCTIONS = FILE_CONTENT.split('[count, sides]')[0]

def runOLD(code: str):
    interp = GENIAInterpreter()
    return interp.run(BASE_FUNCTIONS + '\n' + code)


def test_randrange_foreign_function():
    random.seed(0)
    interp = GENIAInterpreter()
    assert interp.run("randrange(6)") == 3
    random.seed(0)
    assert interp.run("randrange(1, 6)") == 4


def test_randint_native_function():
    random.seed(0)
    result = run("randint(1, 6)")
    assert result == 4


def test_roll_function():
    random.seed(0)
    result = run("roll(2, 6)")
    assert result == 8



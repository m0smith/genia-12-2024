from genia.interpreter import GENIAInterpreter
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

SCRIPT_PATH = Path(__file__).resolve().parent.parent / 'scripts' / 'fns.genia'
FILE_CONTENT = SCRIPT_PATH.read_text()
BASE_FUNCTIONS = FILE_CONTENT.split('\nf = compose')[0]


def run(code: str):
    interp = GENIAInterpreter()
    return interp.run(BASE_FUNCTIONS + '\n' + code)


def test_compose_two_functions():
    code = 'f = compose(double, add)\nf(1,2)'
    assert run(code) == 9


def test_compose_three_functions():
    code = 'f = compose(double, add, add)\nf(2,3)'
    assert run(code) == 25


def test_compose_varargs_arguments():
    code = '\n'.join([
        'define add3(a,b,c) -> a + b + c',
        'f = compose(double, add3)',
        'f(1,2,3)'
    ])
    assert run(code) == 36

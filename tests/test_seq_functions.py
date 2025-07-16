import sys
from pathlib import Path
import pytest
sys.path.append(str(Path(__file__).resolve().parent.parent))

from genia.interpreter import GENIAInterpreter

# Load base functions directly from scripts/seq.genia up to the utility section
SCRIPT_PATH = Path(__file__).resolve().parent.parent / 'scripts' / 'seq.genia'
FILE_CONTENT = SCRIPT_PATH.read_text()
BASE_FUNCTIONS = FILE_CONTENT.split('define inc')[0]
# Provide missing helper used by distinct
BASE_FUNCTIONS += "\ndefine equal?(x) -> define(y) -> x == y | (x, y) -> x == y"

def run(code: str):
    interp = GENIAInterpreter()
    return interp.run(BASE_FUNCTIONS + '\n' + code)

def test_distinct_small():
    code = 'distinct([1,1,2,3,2,3])'
    assert run(code) == [1,2,3]

@pytest.mark.skip(reason="Takes too long to run")
def test_distinct_large():
    n = 2000
    code = f'distinct(1..{n})'
    result = run(code)
    assert result == list(range(1, n+1))

def test_distinct2_small():
    code = 'distinct2([1,1,2,2,3,3,2])'
    assert run(code) == [1,2,3]

def test_interleve_two_lists():
    code = 'interleve([1,2,3], [4,5,6])'
    assert run(code) == [1,4,2,5,3,6]

def test_interleve_large():
    n = 1000
    code = f'interleve(1..{n}, {n+1}..{2*n})'
    result = run(code)
    expected = []
    for a, b in zip(range(1, n+1), range(n+1, 2*n+1)):
        expected.extend([a, b])
    assert result == expected

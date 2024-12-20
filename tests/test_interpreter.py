import pytest
import sys
from pathlib import Path

# Add the parent directory to the system path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from genia.interpreter import GENIAInterpreter

@pytest.fixture
def interpreter():
    return GENIAInterpreter()

def test_multiple_arities(interpreter):
    code = """
    fn add() -> 0;
    fn add(a) -> a;
    fn add(a, b) -> a + b;

    add();
    add(5);
    add(2, 3);
    """
    result = interpreter.run(code)
    assert result == 5  # The last function call `add(2, 3)` should return 5
    
def test_function_with_pattern_matching(interpreter):
    code = """
    fn fact(0) -> 1;
    fn fact(n) when n > 0 -> n * fact(n - 1);

    fact(5);
    """
    result = interpreter.run(code)
    assert result == 120

def test_awk_field_parsing(interpreter):
    code = """
    print($0);        # Print entire record
    print(NR);        # Print record number
    print(NF);        # Print number of fields
    print($1);        # Print first field
    print($NF);       # Print last field
    """
    # interpreter = GENIAInterpreter()
    
    # Simulate input records for AWK mode
    input_lines = [
        "alpha beta gamma",
        "one two three four",
        "hello world"
    ]

    # Run the interpreter in AWK mode
    result = interpreter.run(code, args=input_lines, awk_mode=True)

    # Define the expected outputs
    expected_outputs = [
        "alpha beta gamma",  # $0
        "1",                 # NR
        "3",                 # NF
        "alpha",             # $1
        "gamma",             # $NF
        "one two three four",
        "2",
        "4",
        "one",
        "four",
        "hello world",
        "3",
        "2",
        "hello",
        "world"
    ]

    # Validate that the output matches expectations
    assert result == expected_outputs


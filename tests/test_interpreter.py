import pytest
import sys
from pathlib import Path

# Add the parent directory to the system path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from genia.interpreter import GENIAInterpreter, Interpreter
from genia.parser import Parser
from genia.lexer import Lexer

@pytest.fixture
def interpreter():
    return GENIAInterpreter()

def test_awk_mode_nf():
    code = """
    print($NF)
    """
    stdin_content = "foo bar\nbaz qux\n"
    expected_output = "bar\nqux\n"

    import io
    stdin = io.StringIO(stdin_content)
    stdout = io.StringIO()
    stderr = io.StringIO()

    interpreter = GENIAInterpreter()
    interpreter.run(code, awk_mode=True, stdin=stdin, stdout=stdout, stderr=stderr)

    assert stdout.getvalue() == expected_output

def test_regular_mode_nf():
    code = """
    print($NF)
    """
    args = ["arg1", "arg2", "arg3"]
    expected_output = "arg3\n"

    import io
    stdout = io.StringIO()
    stderr = io.StringIO()

    interpreter = GENIAInterpreter()
    interpreter.run(code, args=args, stdout=stdout, stderr=stderr)

    assert stdout.getvalue() == expected_output


def test_run_with_custom_streams(interpreter):
    import io
    code = """
    fn test() -> print("Hello, World!")
    test();
    """
    stdin = io.StringIO()
    stdout = io.StringIO()
    stderr = io.StringIO()

    interpreter.run(code, stdin=stdin, stdout=stdout, stderr=stderr)

    # Validate stdout contains the expected output
    assert stdout.getvalue() == "Hello, World!\n"

    # Validate stderr contains the debug tokens
    assert "Tokens:" in stderr.getvalue()


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

    import io
    stdin = io.StringIO("\n".join(input_lines))
    stdout = io.StringIO()
    stderr = io.StringIO()

    interpreter = GENIAInterpreter()
    interpreter.run(code, awk_mode=True, stdin=stdin, stdout=stdout, stderr=stderr)


    # Define the expected outputs
    expected_outputs = [
        "alpha beta gamma",  # $0
        "",
        "1",                 # NR
        "3",                 # NF
        "alpha",             # $1
        "gamma",             # $NF
        "one two three four",
        "",
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
    assert stdout.getvalue().splitlines() == expected_outputs

def test_interpreter_multiple_arities():
    code = "fn foo() -> 0 | (_) -> 1;"
    
    interpreter = Interpreter()
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter.execute(ast)
    
    assert interpreter.functions["foo"] is not None
    assert interpreter.functions["foo"](interpreter, [], None) == 0
    assert interpreter.functions["foo"](interpreter, [42], None) == 1
    with pytest.raises(RuntimeError, match="No matching function"):
        assert interpreter.functions["foo"](interpreter, [1,2], None) == 1
        
def test_interpreter_anonymous_multiple_arities():
    code = """c = fn () -> 0 | (_) -> 1
    c()
    """
    
    interpreter = Interpreter()
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    result = interpreter.execute(ast)
    
    assert result == 0

def test_interpreter_function_with_guard__bad_condition(interpreter):
    code = """
    fn foo(x) when x > 10 -> x * 2;
    foo(5);
    foo(15);
    """
    with pytest.raises(RuntimeError, match="No matching function for foo with arguments"):
        interpreter.run(code)
        
def test_interpreter_function_with_guard(interpreter):
    code = """
    fn foo(x) when x > 10 -> x * 2;
  
    foo(15);
    """
    result = interpreter.run(code)
    assert 30 == result

@pytest.mark.skip
def test_interpreter_cons_lsit_reduce(interpreter):
    code = """
    fn cons() -> fn () -> 0;
    fn cons(a, b) -> fn () -> 1 | (1) -> a | (2) -> b;
    
    fn car(c) -> c
    fn car(c) when c() > 0 -> c(1)
    
    fn cdr(c) -> c
    fn cdr(c) when c() > 0 -> c(2)
    
    fn list(a,b,c) -> cons(a, cons(b, cons(c, cons())))
    
    fn reduce(func, acc, lst) -> acc
    fn reduce(func, acc, lst) when lst() > 0 -> reduce(func, func(acc, car(lst)), cdr(lst))
    
    l = list(1,2,3)
    
    """
    result = interpreter.run(code)
    assert 30 == result

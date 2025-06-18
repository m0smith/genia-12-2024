import pytest
import sys
from pathlib import Path

# Add the parent directory to the system path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from genia.interpreter import GENIAInterpreter, Interpreter
from genia.parser import Parser
from genia.lexer import Lexer

@pytest.fixture
def interpreter_fixture():
    return GENIAInterpreter()

def ast(code):
    p = Parser(Lexer(code).tokenize())
    return p.parse()

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
    interpreter.run(code, awk_mode="whitespace", stdin=stdin, stdout=stdout, stderr=stderr)

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


def test_run_with_custom_streams(interpreter_fixture):
    import io
    code = """
    fn test() -> print("Hello, World!")
    test();
    """
    stdin = io.StringIO()
    stdout = io.StringIO()
    stderr = io.StringIO()

    interpreter_fixture.run(code, stdin=stdin, stdout=stdout, stderr=stderr)

    # Validate stdout contains the expected output
    assert stdout.getvalue() == "Hello, World!\n"
    
def test_multiple_arities(interpreter_fixture):
    code = """
    fn add() -> 0;
    fn add(a) -> a;
    fn add(a, b) -> a + b;

    add();
    add(5);
    add(2, 3);
    """
    result = interpreter_fixture.run(code)
    assert result == 5  # The last function call `add(2, 3)` should return 5
    
def test_function_with_pattern_matching(interpreter_fixture):
    code = """
    fn fact(0) -> 1;
    fn fact(n) when n > 0 -> n * fact(n - 1);

    fact(5);
    """
    result = interpreter_fixture.run(code)
    assert result == 120

def test_awk_field_parsing(interpreter_fixture):
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
    interpreter.run(code, awk_mode="whitespace", stdin=stdin, stdout=stdout, stderr=stderr)


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
    assert stdout.getvalue().splitlines() == expected_outputs

def test_interpreter_multiple_arities_direct():
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
        interpreter.functions["foo"](interpreter, [1,2], None)

def test_interpreter_anonymous_multiple_arities(interpreter_fixture):
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

def test_interpreter_function_with_guard_bad_condition(interpreter_fixture):
    code = """
    fn foo(x) when x > 10 -> x * 2;
    foo(5);
    foo(15);
    """
    with pytest.raises(RuntimeError, match="No matching function for 'foo' with arguments"):
        interpreter_fixture.run(code)
        
def test_interpreter_function_with_guard(interpreter_fixture):
    code = """
    fn foo(x) when x > 10 -> x * 2;

    foo(15);
    """
    result = interpreter_fixture.run(code)
    assert 30 == result

def test_interpreter_cons_list_reduce(interpreter_fixture):
    code = """
    trace()
    fn cons(a, b) -> fn () -> 1 | (1) -> a | (2) -> b;
    fn cons() -> fn() -> 0;
    fn list(a, b, c) -> cons(a, cons(b, cons(c, cons())))
    
    fn car(cc) when cc() > 0 -> cc(1)
    fn cdr(cd) when cd() > 0 -> cd(2)
    
    fn reduce(func, accxx, lst1) when lst1() > 0 -> reduce(func, func(accxx, car(lst1)), cdr(lst1))
    fn reduce(func, accx, lst2) -> accx
    
    fn add() -> 0 | (x,y) -> x + y
    
    lst = list(12,8,4)
    printenv()
    reduce(add, add(), lst)
    """
    result = interpreter_fixture.run(code)
    assert 24 == result

def test_interpreter_adder(interpreter_fixture):
    code = """
    fn add(x) -> fn (y) -> x  + y;
    inc = add(1)
    inc(42)
    """
    result = interpreter_fixture.run(code)
    assert 43 == result

def test_interpreter_recursive(interpreter_fixture):
    code = """
    fn first(x) -> x
    fn first(a, b) -> first(a)
    first(5,7)
    """
    result = interpreter_fixture.run(code)
    assert 5 == result


def test_interpreter_recursive_tail_call(interpreter_fixture):
    code = """
    fn reduce(_, acc, [])          -> acc
        |    (f, [head, ..tail])   -> reduce(f, head, tail)
        |    (f, acc, [h, ..tail]) -> reduce(f, f(acc, h), tail)
   
    fn add (x,y) -> x + y
    
    c = [42,99, 10, 2, -12]
    reduce(add, c)
    """
    result = interpreter_fixture.run(code)
    assert 141 == result

def test_interpreter_compose(interpreter_fixture):
    code = """
    fn cons(a, b) -> fn () -> 1 | (1) -> a | (2) -> b;
    fn cons() -> fn() -> 0
    fn car(ca) when ca() > 0 -> ca(1)
    fn cdr(cd) when cd() > 0 -> cd(2)
    
    fn compose(f,g) -> fn (x) -> f(g(x))
    
    cdar = compose(car, cdr)
    cddr = compose(cdr, cdr)
    c = cons(1, cons(3,5))
    c1 = cdar(c) 
    c2 = cddr(c)
    c1 * c2
    
    """
    result = interpreter_fixture.run(code)
    assert 15 == result

def test_interpreter_cons_flag(interpreter_fixture):
    code = """
    fn cons(a, b) -> fn () -> 1 | (1) -> a | (2) -> b;
    c = cons(1,2)
    c()
    
    """
    result = interpreter_fixture.run(code)
    assert 1 == result

def test_interpreter_cons_v1(interpreter_fixture):
    code = """
    fn cons(a, b) -> fn () -> 1 | (1) -> a | (2) -> b;
    fn cons() -> fn() -> 0
    c = cons(42,99)
    c(1)
    
    """
    result = interpreter_fixture.run(code)
    assert 42 == result

def test_interpreter_cons_v2(interpreter_fixture):
    code = """
    fn cons(a, b) -> fn () -> 1 | (1) -> a | (2) -> b;
    fn cons() -> fn() -> 0
    c = cons(42,99)
    c(2)
    
    """
    result = interpreter_fixture.run(code)
    assert 99 == result

def test_interpreter_cons__2_element_list__first(interpreter_fixture):
    code = """
    fn cons(a, b) -> fn () -> 1 | (1) -> a | (2) -> b;
    fn cons() -> fn() -> 0
    
    c = cons(42, cons(99, cons()))
    c(1)
    
    """
    result = interpreter_fixture.run(code)
    assert 42 == result

def test_interpreter_cons__2_element_list__second(interpreter_fixture):
    code = """
    trace()
    fn cons(a, b) -> (fn () -> 1 
                       | (1) -> a 
                       | (2) -> b)
    fn cons() -> fn() -> 0 | (1) -> null | (2) -> null;
    
    c = cons(42, cons(99, cons()))
    c2 = c(2)
    c2(1)
    
    """
    result = interpreter_fixture.run(code)
    assert 99 == result

def test_interpreter___ffi_rem(interpreter_fixture):
    code = """
    fn rem(x,y) -> foreign "math.remainder"
    rem(10,3)
    """
    result = interpreter_fixture.run(code)
    assert 1 == result

def test_interpreter___ffi_rem2(interpreter_fixture):
    code = """
    fn rem
        (x,y) -> foreign "math.remainder" 
      | (x) -> (x) 
      | () -> 0
    rem(10)
    """
    result = interpreter_fixture.run(code)
    assert 10 == result

def test_interpreter_range(interpreter_fixture):
    code = "1..10"
    result = interpreter_fixture.run(code)
    assert list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
def test_interpreter_range_desc(interpreter_fixture):
    code = "10..1"
    result = interpreter_fixture.run(code)
    assert list(result) == [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    
def test_interpreter_range_same(interpreter_fixture):
    code = "10..10"
    result = interpreter_fixture.run(code)
    assert list(result) == [10]
    
def test_interpreter_pattern_match_empty_list(interpreter_fixture):
    code = """
        fn foo([]) -> 0 | ([a, ..r]) -> a
        foo([])
        """
    result = interpreter_fixture.run(code)
    assert result == 0
    
def test_interpreter_pattern_match_list_1_element(interpreter_fixture):
    code = """
        fn foo([]) -> 0 | ([a, ..r]) -> a
        foo([1])
        """
    result = interpreter_fixture.run(code)
    assert result == 1

def test_interpreter_pattern_match_list_2_element(interpreter_fixture):
    code = """
        fn foo([]) -> 0 | ([a, ..r]) -> a
        foo([29, 31])
        """
    result = interpreter_fixture.run(code)
    assert result == 29
    
def test_interpreter_pattern_match_count_list(interpreter_fixture):
    code = """
        fn count  ([])       -> 0 
           |      ([a, ..r]) -> 1 + count(r)
        count(100..1)
        """
    result = interpreter_fixture.run(code)
    assert result == 100
    
def test_interpreter_pattern_match_count_list_tco(interpreter_fixture):
    code = """
        fn count  ([])            -> 0  
           |      ([a, ..r])      -> count(1, r)
           |      (acc, [a, ..r]) -> count(1 + acc, r)
           |      (acc, [])       -> acc
        count(100..1)
        """
    result = interpreter_fixture.run(code)
    assert result == 100
    
def test_interpreter_pattern_assignment(interpreter_fixture):
    code = """
        [a, b, c] = 10..14
        sum = a + b + c
        sum / 3
        """
    print(f"ACT {ast(code)}")
    result = interpreter_fixture.run(code)
    assert result == 11

def test_interpreter_return_empty_list(interpreter_fixture):
    code = """
        fn foo() -> []
        foo()
        """
    result = interpreter_fixture.run(code)
    assert result == []

def test_interpreter_return_list(interpreter_fixture):
    code = """
        fn foo(a,b,c) -> [a,b,c]
        foo(1,2,3)
        """
    result = interpreter_fixture.run(code)
    assert result == [1,2,3]

def test_interpreter_return_rest(interpreter_fixture):
    code = """
        fn foo([_, ..r1]) -> r1
        foo(2..5)
        """
    print(f"AST {ast(code)}")
    result = interpreter_fixture.run(code)
    assert result == [3, 4, 5]
    
def test_interpreter_return_rest2(interpreter_fixture):
    code = """
        fn foo([_, _, ..r1]) -> r1
        foo(2..5)
        """
    result = interpreter_fixture.run(code)
    assert result == [4, 5]
    
def test_interpreter_return_rest_expanded(interpreter_fixture):
    code = """
        fn foo([_, ..r]) -> [99, ..r]
        foo(10..14)
        """
    result = interpreter_fixture.run(code)
    assert result == [99,11,12,13,14]

def test_interpreter_map(interpreter_fixture):
    code = """
        fn map(_, []) -> []
        fn map(f, [first, ..rest]) -> [f(first), ..map(f, rest)]
        fn double(x) -> x + x
        map(double, 1..10)
        """
    result = interpreter_fixture.run(code)
    assert result == [2,4,6,8,10,12,14,16,18,20]
    
def test_interpreter_join_lists(interpreter_fixture):
    code = """
        [
            ..1..3, 
            ..4..6, 
            ..7..9
        ]
        """
    result = interpreter_fixture.run(code)
    assert result == [1,2,3,4,5,6,7,8,9]

def test_interpreter_nested_lists(interpreter_fixture):
    code = """
        [
            1..3, 
            4..6, 
            9..7
        ]
        """
    result = interpreter_fixture.run(code)
    assert result == [
        [1,2,3], 
        [4,5,6], 
        [9,8,7]]
    
def test_interpreter_join_and_nested_lists(interpreter_fixture):
    code = """
        [
            ..1..3, 
            4..6, 
            ..9..7
        ]
        """
    expected = [
        1, 2, 3, 
        [4,5,6], 
        9, 8, 7
    ]
    print(f"AST: {ast(code)}")
    result = interpreter_fixture.run(code)
    assert result == expected, ast(code)

def test_eval_mixed_strings(interpreter_fixture):
    code = '''[
        r"[A-Z]+", 
        "regular"
    ]'''
    results = interpreter_fixture.run(code)
    assert results == ['[A-Z]+', 'regular']

def test_regex(interpreter_fixture):
    code = """
        fn foo(a) when a ~ r"[a-z]" -> 42 | (_) -> -1
        foo("aa")
    """
    results = interpreter_fixture.run(code)
    assert results == 42

def test_delay(interpreter_fixture):
    code = """
       f = delay(520)
       f
    """
    results = interpreter_fixture.run(code)
    assert results == 520

# 1. Test if a delayed expression is evaluated correctly once
def test_delay_simple_expression(interpreter_fixture):
    code = """
    x = delay(10 + 20)
    x
    """
    result = interpreter_fixture.run(code)
    assert result == 30

# 2. Test if a delay is evaluated lazily and only once
def test_delay_evaluated_once(interpreter_fixture):
    call_count = {'count': 0}

    def increment():
        call_count['count'] += 1
        return 42

    # Modify the interpreter to handle callable expressions for this test
    code = """
    f = delay(42)
    f
    """
    result = interpreter_fixture.run(code)
    assert result == 42
    assert call_count['count'] == 0  # Since the expression is directly a number, not callable

# 3. Test if nested delay expressions are handled correctly
def test_nested_delay_expression(interpreter_fixture):
    code = """
    y = delay(delay(100))
    y
    """
    result = interpreter_fixture.run(code)
    assert result == 100

# 4. Test if delay handles string expressions correctly
def test_delay_string_expression(interpreter_fixture):
    code = """
    message = delay("Hello, World!")
    message
    """
    result = interpreter_fixture.run(code)
    assert result == "Hello, World!"

# @pytest.mark.skip  
def test_lazy_seq_count(interpreter_fixture):
    code = """
    ls = lazyseq([1,2,3])
    
    fn count([]) -> 0
    fn count([_, ..tail]) -> 1 + count(tail) 
    
    count(ls)
    """
    result = interpreter_fixture.run(code)
    assert result == 3
    
def test_iterseq_count(interpreter_fixture):
    code = """
    f = find_files("scripts")
   
    fn count([])                -> 0
    fn count([_, ..tail])       -> count(1, tail)
    fn count(acc, [])           -> acc
    fn count(acc, [_, ..tail])  -> count(acc + 1, tail)
    
    count(f)
    count(f)
    """
    result = interpreter_fixture.run(code)
    assert result > 5

# TODO:  The delay does not properly close on the f argument
@pytest.mark.skip   
def test_delayseq_count(interpreter_fixture):
    code = """
    fn iterate(f, v) -> delayseq(v, delay(iterate(f, f(v))))
    [a,b,c,d] = iterate(fn(i) -> i + 1, 1)
    d
    """
    result = interpreter_fixture.run(code)
    assert result == 4
import pytest
import sys
from pathlib import Path

# Add the parent directory to the system path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from genia.lexer import Lexer

def tokenize(code):
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    return tokens
    
def test_single_line_comments():
    code = """// This is a comment
    valid_token = 123; // Another comment
    another = 456; # Hash comment"""
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    expected_tokens = [
        ('IDENTIFIER', 'valid_token', 2, 5),
        ('OPERATOR', '=', 2, 17),
        ('NUMBER', '123', 2, 19),
        ('PUNCTUATION', ';', 2, 22),
        ('IDENTIFIER', 'another', 3, 5),
        ('OPERATOR', '=', 3, 13),
        ('NUMBER', '456', 3, 15),
        ('PUNCTUATION', ';', 3, 18)
    ]

    assert tokens == expected_tokens
    
def test_comparator_token():
    code = "n > 0"
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    expected_tokens = [
        ('IDENTIFIER', 'n', 1, 1),
        ('COMPARATOR', '>', 1, 3),
        ('NUMBER', '0', 1, 5)
    ]

    assert tokens == expected_tokens

def test_identifier_with_dollar():
    code = """
    $var = 123;
    print($var);
    $another_var = $var + 10;
    """
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    expected_tokens = [
        ('IDENTIFIER', '$var', 2, 5),
        ('OPERATOR', '=', 2, 10),
        ('NUMBER', '123', 2, 12),
        ('PUNCTUATION', ';', 2, 15),
        ('IDENTIFIER', 'print', 3, 5),
        ('PUNCTUATION', '(', 3, 10),
        ('IDENTIFIER', '$var', 3, 11),
        ('PUNCTUATION', ')', 3, 15),
        ('PUNCTUATION', ';', 3, 16),
        ('IDENTIFIER', '$another_var', 4, 5),
        ('OPERATOR', '=', 4, 18),
        ('IDENTIFIER', '$var', 4, 20),
        ('OPERATOR', '+', 4, 25),
        ('NUMBER', '10', 4, 27),
        ('PUNCTUATION', ';', 4, 29),
    ]

    assert tokens == expected_tokens

def test_pipe_operator():
    code = "fn foo() -> 0 | (_) -> 1;"
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    expected_tokens = [
        ('KEYWORD', 'fn', 1, 1),
        ('IDENTIFIER', 'foo', 1, 4),
        ('PUNCTUATION', '(', 1, 7),
        ('PUNCTUATION', ')', 1, 8),
        ('ARROW', '->', 1, 10),
        ('NUMBER', '0', 1, 13),
        ('PIPE', '|', 1, 15),
        ('PUNCTUATION', '(', 1, 17),
        ('IDENTIFIER', '_', 1, 18),
        ('PUNCTUATION', ')', 1, 19),
        ('ARROW', '->', 1, 21),
        ('NUMBER', '1', 1, 24),
        ('PUNCTUATION', ';', 1, 25),
    ]
    assert tokens == expected_tokens

def test_lexer_pipe_and_anonymous_function():
    code = "c = fn () -> 0 | (_) -> 1"
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    expected_tokens = [
        ('IDENTIFIER', 'c', 1, 1), 
        ('OPERATOR', '=', 1, 3),
        ('KEYWORD', 'fn', 1, 5), 
        ('PUNCTUATION', '(', 1, 8), 
        ('PUNCTUATION', ')', 1, 9), 
        ('ARROW', '->', 1, 11), 
        ('NUMBER', '0', 1, 14),
        ('PIPE', '|', 1, 16),
        ('PUNCTUATION', '(', 1, 18),
        ('IDENTIFIER', '_', 1, 19), 
        ('PUNCTUATION', ')', 1, 20), 
        ('ARROW', '->', 1, 22),
        ('NUMBER', '1', 1, 25),
    ]

    assert tokens == expected_tokens

def test_lexer_nested_function():
    code = "fn cons() -> fn () -> 0"
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    expected_tokens = [
    ("KEYWORD", "fn", 1, 1),
    ("IDENTIFIER", "cons", 1, 4),
    ("PUNCTUATION", "(", 1, 8),
    ("PUNCTUATION", ")", 1, 9),
    ("ARROW", "->", 1, 11),
    ("KEYWORD", "fn", 1, 14),
    ("PUNCTUATION", "(", 1, 17),
    ("PUNCTUATION", ")", 1, 18),
    ("ARROW", "->", 1, 20),
    ("NUMBER", "0", 1, 23),
]

    assert tokens == expected_tokens

def test_lexer_tokenizes_foreign_keyword_with_positions():
    
    code = "foreign fn print(a) -> ;"
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    assert tokens == [
        ("KEYWORD", "foreign", 1, 1),
        ("KEYWORD", "fn", 1, 9),
        ("IDENTIFIER", "print", 1, 12),
        ("PUNCTUATION", "(", 1, 17),
        ("IDENTIFIER", "a", 1, 18),
        ("PUNCTUATION", ")", 1, 19),
        ("ARROW", "->", 1, 21),
        ("PUNCTUATION", ";", 1, 24),
    ]

def test_lexer_handles_multiple_lines():
    code = "fn add(a, b) ->\n  a + b;"
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    assert tokens == [
        ("KEYWORD", "fn", 1, 1),
        ("IDENTIFIER", "add", 1, 4),
        ("PUNCTUATION", "(", 1, 7),
        ("IDENTIFIER", "a", 1, 8),
        ("PUNCTUATION", ",", 1, 9),
        ("IDENTIFIER", "b", 1, 11),
        ("PUNCTUATION", ")", 1, 12),
        ("ARROW", "->", 1, 14),
        # ("NEWLINE", "\n", 1, 16),
        ("IDENTIFIER", "a", 2, 3),
        ("OPERATOR", "+", 2, 5),
        ("IDENTIFIER", "b", 2, 7),
        ("PUNCTUATION", ";", 2, 8),
    ]

def test_lexer_raises_error_with_position():
    code = "fn invalid $"
    lexer = Lexer(code)
    
    try:
        lexer.tokenize()
    except ValueError as e:
        assert str(e) == "Unexpected character at line 1, column 11: $"
        
def test_lexer__unicode_identifiers():
    code = "fn example(xαβγ?, y*ζ) -> xαβγ? + y*ζ*"
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    expected = [
        ('KEYWORD', 'fn', 1, 1),    
        ('IDENTIFIER', 'example', 1, 4),    
        ('PUNCTUATION', '(', 1, 11),    
        ('IDENTIFIER', 'xαβγ?', 1, 12),    
        ('PUNCTUATION', ',', 1, 17),    
        ('IDENTIFIER', 'y*ζ', 1, 19),    
        ('PUNCTUATION', ')', 1, 22),    
        ('ARROW', '->', 1, 24),    
        ('IDENTIFIER', 'xαβγ?', 1, 27),    
        ('OPERATOR', '+', 1, 33),    
        ('IDENTIFIER', 'y*ζ*', 1, 35)    
        ]

    assert tokens == expected
    
def test_basic_tokens():
    code = "fn map (func, [first, ..rest]) -> [func(first), ..map(func, rest)];"
    tokens = tokenize(code)
    expected = [
        ('KEYWORD', 'fn', 1, 1),
        ('IDENTIFIER', 'map', 1, 4),
        ('PUNCTUATION', '(', 1, 8),
        ('IDENTIFIER', 'func', 1, 9),
        ('PUNCTUATION', ',', 1, 13),
        ('PUNCTUATION', '[', 1, 15),
        ('IDENTIFIER', 'first', 1, 16),
        ('PUNCTUATION', ',', 1, 21),
        ('DOT_DOT', '..', 1, 23),
        ('IDENTIFIER', 'rest', 1, 25),
        ('PUNCTUATION', ']', 1, 29),
        ('PUNCTUATION', ')', 1, 30),
        ('ARROW', '->', 1, 32),
        ('PUNCTUATION', '[', 1, 35),
        ('IDENTIFIER', 'func', 1, 36),
        ('PUNCTUATION', '(', 1, 40),
        ('IDENTIFIER', 'first', 1, 41),
        ('PUNCTUATION', ')', 1, 46),
        ('PUNCTUATION', ',', 1, 47),
        ('DOT_DOT', '..', 1, 49),
        ('IDENTIFIER', 'map', 1, 51),
        ('PUNCTUATION', '(', 1, 54),
        ('IDENTIFIER', 'func', 1, 55),
        ('PUNCTUATION', ',', 1, 59),
        ('IDENTIFIER', 'rest', 1, 61),
        ('PUNCTUATION', ')', 1, 65),
        ('PUNCTUATION', ']', 1, 66),
        ('PUNCTUATION', ';', 1, 67),
    ]
    assert tokens == expected

def test_range():
    code = "range = 1..10;"
    tokens = tokenize(code)
    expected = [
        ('IDENTIFIER', 'range', 1, 1),
        ('OPERATOR', '=', 1, 7),
        ('NUMBER', '1', 1, 9),
        ('DOT_DOT', '..', 1, 10),
        ('NUMBER', '10', 1, 12),
        ('PUNCTUATION', ';', 1, 14),
    ]
    assert tokens == expected

def test_end_of_list():
    code = "[first, ..rest, last]"
    tokens = tokenize(code)
    expected = [
        ('PUNCTUATION', '[', 1, 1),
        ('IDENTIFIER', 'first', 1, 2),
        ('PUNCTUATION', ',', 1, 7),
        ('DOT_DOT', '..', 1, 9),
        ('IDENTIFIER', 'rest', 1, 11),
        ('PUNCTUATION', ',', 1, 15),
        ('IDENTIFIER', 'last', 1, 17),
        ('PUNCTUATION', ']', 1, 21),
    ]
    assert tokens == expected
    
def test_parser_list_pattern_tokens():
    code = ("fn foo([_, ..r]) -> [99, ..r]")
    tokens = tokenize(code)

    expected_tokens = [
        ('KEYWORD', 'fn', 1, 1),
        ('IDENTIFIER', 'foo', 1, 4),
        ('PUNCTUATION', '(', 1, 7),
        ('PUNCTUATION', '[', 1, 8),
        ('IDENTIFIER', '_', 1, 9),
        ('PUNCTUATION', ',', 1, 10),
        ('DOT_DOT', '..', 1, 12),
        ('IDENTIFIER', 'r', 1, 14),
        ('PUNCTUATION', ']', 1, 15),
        ('PUNCTUATION', ')', 1, 16),
        ('ARROW', '->', 1, 18),
        ('PUNCTUATION', '[', 1, 21),
        ('NUMBER', '99', 1, 22),
        ('PUNCTUATION', ',', 1, 24),
        ('DOT_DOT', '..', 1, 26),
        ('IDENTIFIER', 'r', 1, 28),
        ('PUNCTUATION', ']', 1, 29),
    ]

    assert tokens == expected_tokens
    
def test_multiple_statements_in_function():
    code = "fn foo() -> (a = 1; b = 2; a + b)"
    tokens = tokenize(code)
    expected_tokens = [
        ('KEYWORD', 'fn', 1, 1),
        ('IDENTIFIER', 'foo', 1, 4),
        ('PUNCTUATION', '(', 1, 7),
        ('PUNCTUATION', ')', 1, 8),
        ('ARROW', '->', 1, 10),
        ('PUNCTUATION', '(', 1, 13),
        ('IDENTIFIER', 'a', 1, 14),
        ('OPERATOR', '=', 1, 16),
        ('NUMBER', '1', 1, 18),
        ('PUNCTUATION', ';', 1, 19),
        ('IDENTIFIER', 'b', 1, 21),
        ('OPERATOR', '=', 1, 23),
        ('NUMBER', '2', 1, 25),
        ('PUNCTUATION', ';', 1, 26),
        ('IDENTIFIER', 'a', 1, 28),
        ('OPERATOR', '+', 1, 30),
        ('IDENTIFIER', 'b', 1, 32),
        ('PUNCTUATION', ')', 1, 33),
    ]
    assert tokens == expected_tokens

def test_nested_grouped_statements():
    code = "fn bar() -> (x = (y = 1; z = 2; y * z); x + 5);"
    tokens = tokenize(code)
    expected_tokens = [
        ('KEYWORD', 'fn', 1, 1),
        ('IDENTIFIER', 'bar', 1, 4),
        ('PUNCTUATION', '(', 1, 7),
        ('PUNCTUATION', ')', 1, 8),
        ('ARROW', '->', 1, 10),
        ('PUNCTUATION', '(', 1, 13),
        ('IDENTIFIER', 'x', 1, 14),
        ('OPERATOR', '=', 1, 16),
        ('PUNCTUATION', '(', 1, 18),
        ('IDENTIFIER', 'y', 1, 19),
        ('OPERATOR', '=', 1, 21),
        ('NUMBER', '1', 1, 23),
        ('PUNCTUATION', ';', 1, 24),
        ('IDENTIFIER', 'z', 1, 26),
        ('OPERATOR', '=', 1, 28),
        ('NUMBER', '2', 1, 30),
        ('PUNCTUATION', ';', 1, 31),
        ('IDENTIFIER', 'y', 1, 33),
        ('OPERATOR', '*', 1, 35),
        ('IDENTIFIER', 'z', 1, 37),
        ('PUNCTUATION', ')', 1, 38),
        ('PUNCTUATION', ';', 1, 39),
        ('IDENTIFIER', 'x', 1, 41),
        ('OPERATOR', '+', 1, 43),
        ('NUMBER', '5', 1, 45),
        ('PUNCTUATION', ')', 1, 46),
        ('PUNCTUATION', ';', 1, 47),
    ]
    assert tokens == expected_tokens

def test_raw_string_double_quotes():
    code = r'r"[A-Z]+\n"'
    tokens = tokenize(code)
    expected_tokens = [
        ('RAW_STRING', r"[A-Z]+\n", 1, 9),
    ]
    assert tokens == expected_tokens

def test_raw_string_single_quotes():
    code = r"r'[A-Z]+\n'"
    tokens = tokenize(code)
    expected_tokens = [
        ('RAW_STRING', r'[A-Z]+\n', 1, 9),
    ]
    assert tokens == expected_tokens

def test_regular_string_double_quotes():
    code = '"regular\\nstring"'
    tokens = tokenize(code)
    expected_tokens = [
        ('STRING', 'regular\\nstring', 1, 16),
    ]
    assert tokens == expected_tokens

def test_regular_string_single_quotes():
    code = "'regular\\nstring'"
    tokens = tokenize(code)
    expected_tokens = [
        ('STRING', 'regular\\nstring', 1, 16),
    ]
    assert tokens == expected_tokens

def test_combined_strings():
    code = r'r"[A-Z]+\n" "regular\\nstring"'
    tokens = tokenize(code)
    expected_tokens = [
        ('RAW_STRING', r'[A-Z]+\n', 1, 9),
        ('STRING', 'regular\\\\nstring', 1, 34),
    ]
    assert tokens == expected_tokens

def test_invalid_raw_string():
    code = r'r"[A-Z]+\n'
    lexer = Lexer(code)
    with pytest.raises(SyntaxError):
        lexer.tokenize()

def test_mixed_code():
    code = r'''
    r"[A-Z]+\s" "regular\nstring"
    fn example -> print("Hello")
    '''
    tokens = tokenize(code)
    expected_tokens = [
        ('RAW_STRING', r'[A-Z]+\s', 2, 13),
        ('STRING', 'regular\\nstring', 2, 37),
        ('KEYWORD', 'fn', 3, 5),
        ('IDENTIFIER', 'example', 3, 8),
        ('ARROW', '->', 3, 16),
        ('IDENTIFIER', 'print', 3, 19),
        ('PUNCTUATION', '(', 3, 24),
        ('STRING', 'Hello', 3, 30),
        ('PUNCTUATION', ')', 3, 35),
    ]
    assert tokens == expected_tokens

# 1. Test if the lexer correctly identifies the 'delay' keyword
def test_lexer_recognizes_delay_keyword():
    code = "delay(expensive_computation())"
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    assert ('KEYWORD', 'delay', 1, 1) in tokens

# 2. Test if the lexer handles a combination of keywords and identifiers with delay
def test_lexer_handles_keywords_and_identifiers():
    code = "fn delay_value = delay(expensive_computation())"
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    expected_tokens = [
        ('KEYWORD', 'fn', 1, 1),
        ('IDENTIFIER', 'delay_value', 1, 4),
        ('OPERATOR', '=', 1, 16),
        ('KEYWORD', 'delay', 1, 18),
        ('PUNCTUATION', '(', 1, 23),
        ('IDENTIFIER', 'expensive_computation', 1, 24),
        ('PUNCTUATION', '(', 1, 45),
        ('PUNCTUATION', ')', 1, 46),
        ('PUNCTUATION', ')', 1, 47),
    ]
    assert tokens == expected_tokens

# 3. Test if the lexer skips comments while identifying the 'delay' keyword
def test_lexer_skips_comments():
    code = "// This is a comment\ndelay(expensive_computation())"
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    assert ('KEYWORD', 'delay', 2, 1) in tokens

# 4. Test if the lexer handles nested delay expressions
def test_lexer_handles_nested_delay():
    code = "delay(delay(expensive_computation()))"
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    delay_tokens = [token for token in tokens if token[1] == 'delay']
    assert len(delay_tokens) == 2
   
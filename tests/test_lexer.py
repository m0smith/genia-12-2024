# tests/test_lexer.py

import pytest
import sys
from pathlib import Path
import textwrap

# Add the parent directory to the system path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from genia.lexer import Lexer, Token  # Ensure Token is imported if needed

def tokenize(code):
    lexer = Lexer(code)
    # Convert Token objects to tuples (type, value, line, column)
    tokens = [(token.type, token.value, token.line, token.column) for token in lexer.tokenize()]
    return tokens

def test_single_line_comments():
    code = textwrap.dedent("""\
        // This is a comment
        valid_token = 123; // Another comment
        another = 456; # Hash comment
        """)
    tokens = tokenize(code)
    # print(tokens)  # Remove or comment out after verification

    expected_tokens = [
        ('IDENTIFIER', 'valid_token', 2, 1),
        ('OPERATOR', '=', 2, 13),
        ('NUMBER', '123', 2, 15),
        ('PUNCTUATION', ';', 2, 18),
        ('IDENTIFIER', 'another', 3, 1),
        ('OPERATOR', '=', 3, 9),
        ('NUMBER', '456', 3, 11),
        ('PUNCTUATION', ';', 3, 14),
    ]

    assert tokens == expected_tokens

def test_comparator_token():
    code = "n > 0"
    tokens = tokenize(code)

    expected_tokens = [
        ('IDENTIFIER', 'n', 1, 1),
        ('COMPARATOR', '>', 1, 3),
        ('NUMBER', '0', 1, 5),
    ]

    assert tokens == expected_tokens

def test_identifier_with_dollar():
    code = textwrap.dedent("""\
        $var = 123;
        print($var);
        $another_var = $var + 10;
        """)
    tokens = tokenize(code)
    # print(tokens)  # Remove or comment out after verification

    expected_tokens = [
        ('IDENTIFIER', '$var', 1, 1),
        ('OPERATOR', '=', 1, 6),
        ('NUMBER', '123', 1, 8),
        ('PUNCTUATION', ';', 1, 11),
        ('IDENTIFIER', 'print', 2, 1),
        ('PUNCTUATION', '(', 2, 6),
        ('IDENTIFIER', '$var', 2, 7),
        ('PUNCTUATION', ')', 2, 11),
        ('PUNCTUATION', ';', 2, 12),
        ('IDENTIFIER', '$another_var', 3, 1),
        ('OPERATOR', '=', 3, 14),
        ('IDENTIFIER', '$var', 3, 16),
        ('OPERATOR', '+', 3, 21),
        ('NUMBER', '10', 3, 23),
        ('PUNCTUATION', ';', 3, 25),
    ]

    assert tokens == expected_tokens

def test_pipe_operator():
    code = "define foo() -> 0 | (_) -> 1;"
    tokens = tokenize(code)
    # print(tokens)  # Remove or comment out after verification

    expected_tokens = [
        ('KEYWORD', 'define', 1, 1),
        ('IDENTIFIER', 'foo', 1, 8),
        ('PUNCTUATION', '(', 1, 11),
        ('PUNCTUATION', ')', 1, 12),
        ('ARROW', '->', 1, 14),
        ('NUMBER', '0', 1, 17),
        ('PUNCTUATION', '|', 1, 19),
        ('PUNCTUATION', '(', 1, 21),
        ('IDENTIFIER', '_', 1, 22),
        ('PUNCTUATION', ')', 1, 23),
        ('ARROW', '->', 1, 25),
        ('NUMBER', '1', 1, 28),
        ('PUNCTUATION', ';', 1, 29),
    ]
    assert tokens == expected_tokens

def test_lexer_pipe_and_anonymous_function():
    code = "c = define () -> 0 | (_) -> 1"
    tokens = tokenize(code)
    # print(tokens)  # Remove or comment out after verification

    expected_tokens = [
        ('IDENTIFIER', 'c', 1, 1),
        ('OPERATOR', '=', 1, 3),
        ('KEYWORD', 'define', 1, 5),
        ('PUNCTUATION', '(', 1, 12),
        ('PUNCTUATION', ')', 1, 13),
        ('ARROW', '->', 1, 15),
        ('NUMBER', '0', 1, 18),
        ('PUNCTUATION', '|', 1, 20),
        ('PUNCTUATION', '(', 1, 22),
        ('IDENTIFIER', '_', 1, 23),
        ('PUNCTUATION', ')', 1, 24),
        ('ARROW', '->', 1, 26),
        ('NUMBER', '1', 1, 29),
    ]

    assert tokens == expected_tokens

def test_lexer_nested_function():
    code = "define cons() -> define () -> 0"
    tokens = tokenize(code)
    # print(tokens)  # Remove or comment out after verification

    expected_tokens = [
        ('KEYWORD', 'define', 1, 1),
        ('IDENTIFIER', 'cons', 1, 8),
        ('PUNCTUATION', '(', 1, 12),
        ('PUNCTUATION', ')', 1, 13),
        ('ARROW', '->', 1, 15),
        ('KEYWORD', 'define', 1, 18),
        ('PUNCTUATION', '(', 1, 25),
        ('PUNCTUATION', ')', 1, 26),
        ('ARROW', '->', 1, 28),
        ('NUMBER', '0', 1, 31),
    ]
    
    assert tokens == expected_tokens

def test_lexer_tokenizes_foreign_keyword_with_positions():
    code = "foreign define print(a) -> ;"
    tokens = tokenize(code)
    # print(tokens)  # Remove or comment out after verification

    expected_tokens = [
        ('KEYWORD', 'foreign', 1, 1),
        ('KEYWORD', 'define', 1, 9),
        ('IDENTIFIER', 'print', 1, 16),
        ('PUNCTUATION', '(', 1, 21),
        ('IDENTIFIER', 'a', 1, 22),
        ('PUNCTUATION', ')', 1, 23),
        ('ARROW', '->', 1, 25),
        ('PUNCTUATION', ';', 1, 28),
    ]

    assert tokens == expected_tokens

def test_lexer_handles_multiple_lines():
    code = textwrap.dedent("""\
        define add(a, b) ->
          a + b;""")
    tokens = tokenize(code)
    # print(tokens)  # Remove or comment out after verification

    expected_tokens = [
        ('KEYWORD', 'define', 1, 1),
        ('IDENTIFIER', 'add', 1, 8),
        ('PUNCTUATION', '(', 1, 11),
        ('IDENTIFIER', 'a', 1, 12),
        ('PUNCTUATION', ',', 1, 13),
        ('IDENTIFIER', 'b', 1, 15),
        ('PUNCTUATION', ')', 1, 16),
        ('ARROW', '->', 1, 18),
        ('IDENTIFIER', 'a', 2, 3),
        ('OPERATOR', '+', 2, 5),
        ('IDENTIFIER', 'b', 2, 7),
        ('PUNCTUATION', ';', 2, 8),
    ]

    assert tokens == expected_tokens

def test_lexer_raises_error_with_position():
    code = "define invalid $"
    lexer = Lexer(code)
    
    with pytest.raises(Lexer.SyntaxError) as exc_info:
        list(lexer.tokenize())
    assert "Unexpected character '$' at line 1, column 16" in str(exc_info.value)

def test_lexer_unicode_identifiers():
    code = "define example(xαβγ?, y*ζ) -> xαβγ? + y*ζ*"
    tokens = tokenize(code)
    # print(tokens)  # Remove or comment out after verification

    expected = [
        ('KEYWORD', 'define', 1, 1),
        ('IDENTIFIER', 'example', 1, 8),
        ('PUNCTUATION', '(', 1, 15),
        ('IDENTIFIER', 'xαβγ?', 1, 16),
        ('PUNCTUATION', ',', 1, 21),
        ('IDENTIFIER', 'y*ζ', 1, 23),
        ('PUNCTUATION', ')', 1, 26),
        ('ARROW', '->', 1, 28),
        ('IDENTIFIER', 'xαβγ?', 1, 31),
        ('OPERATOR', '+', 1, 37),
        ('IDENTIFIER', 'y*ζ*', 1, 39),
    ]

    assert tokens == expected

def test_basic_tokens():
    code = "define map (func, [first, ..rest]) -> [func(first), ..map(func, rest)];"
    tokens = tokenize(code)
    # print(tokens)  # Remove or comment out after verification

    expected = [
        ('KEYWORD', 'define', 1, 1),
        ('IDENTIFIER', 'map', 1, 8),
        ('PUNCTUATION', '(', 1, 12),
        ('IDENTIFIER', 'func', 1, 13),
        ('PUNCTUATION', ',', 1, 17),
        ('PUNCTUATION', '[', 1, 19),
        ('IDENTIFIER', 'first', 1, 20),
        ('PUNCTUATION', ',', 1, 25),
        ('OPERATOR', '..', 1, 27),
        ('IDENTIFIER', 'rest', 1, 29),
        ('PUNCTUATION', ']', 1, 33),
        ('PUNCTUATION', ')', 1, 34),
        ('ARROW', '->', 1, 36),
        ('PUNCTUATION', '[', 1, 39),
        ('IDENTIFIER', 'func', 1, 40),
        ('PUNCTUATION', '(', 1, 44),
        ('IDENTIFIER', 'first', 1, 45),
        ('PUNCTUATION', ')', 1, 50),
        ('PUNCTUATION', ',', 1, 51),
        ('OPERATOR', '..', 1, 53),
        ('IDENTIFIER', 'map', 1, 55),
        ('PUNCTUATION', '(', 1, 58),
        ('IDENTIFIER', 'func', 1, 59),
        ('PUNCTUATION', ',', 1, 63),
        ('IDENTIFIER', 'rest', 1, 65),
        ('PUNCTUATION', ')', 1, 69),
        ('PUNCTUATION', ']', 1, 70),
        ('PUNCTUATION', ';', 1, 71),
    ]
    assert tokens == expected

def test_range():
    code = "range = 1..10;"
    tokens = tokenize(code)
    # print(tokens)  # Remove or comment out after verification

    expected = [
        ('IDENTIFIER', 'range', 1, 1),
        ('OPERATOR', '=', 1, 7),
        ('NUMBER', '1', 1, 9),
        ('OPERATOR', '..', 1, 10),
        ('NUMBER', '10', 1, 12),
        ('PUNCTUATION', ';', 1, 14),
    ]
    assert tokens == expected

def test_negative_range_tokens():
    code = "-10..10"
    tokens = tokenize(code)

    expected = [
        ('OPERATOR', '-', 1, 1),
        ('NUMBER', '10', 1, 2),
        ('OPERATOR', '..', 1, 4),
        ('NUMBER', '10', 1, 6),
    ]
    assert tokens == expected

def test_end_of_list():
    code = "[first, ..rest, last]"
    tokens = tokenize(code)
    # print(tokens)  # Remove or comment out after verification

    expected = [
        ('PUNCTUATION', '[', 1, 1),
        ('IDENTIFIER', 'first', 1, 2),
        ('PUNCTUATION', ',', 1, 7),
        ('OPERATOR', '..', 1, 9),
        ('IDENTIFIER', 'rest', 1, 11),
        ('PUNCTUATION', ',', 1, 15),
        ('IDENTIFIER', 'last', 1, 17),
        ('PUNCTUATION', ']', 1, 21),
    ]
    assert tokens == expected

def test_parser_list_pattern_tokens():
    code = "define foo([_, ..r]) -> [99, ..r]"
    tokens = tokenize(code)
    # print(tokens)  # Remove or comment out after verification

    expected_tokens = [
        ('KEYWORD', 'define', 1, 1),
        ('IDENTIFIER', 'foo', 1, 8),
        ('PUNCTUATION', '(', 1, 11),
        ('PUNCTUATION', '[', 1, 12),
        ('IDENTIFIER', '_', 1, 13),
        ('PUNCTUATION', ',', 1, 14),
        ('OPERATOR', '..', 1, 16),
        ('IDENTIFIER', 'r', 1, 18),
        ('PUNCTUATION', ']', 1, 19),
        ('PUNCTUATION', ')', 1, 20),
        ('ARROW', '->', 1, 22),
        ('PUNCTUATION', '[', 1, 25),
        ('NUMBER', '99', 1, 26),
        ('PUNCTUATION', ',', 1, 28),
        ('OPERATOR', '..', 1, 30),
        ('IDENTIFIER', 'r', 1, 32),
        ('PUNCTUATION', ']', 1, 33),
    ]

    assert tokens == expected_tokens

def test_multiple_statements_in_function():
    code = "define foo() -> (a = 1; b = 2; a + b)"
    tokens = tokenize(code)
    # print(tokens)  # Remove or comment out after verification

    expected_tokens = [
        ('KEYWORD', 'define', 1, 1),
        ('IDENTIFIER', 'foo', 1, 8),
        ('PUNCTUATION', '(', 1, 11),
        ('PUNCTUATION', ')', 1, 12),
        ('ARROW', '->', 1, 14),
        ('PUNCTUATION', '(', 1, 17),
        ('IDENTIFIER', 'a', 1, 18),
        ('OPERATOR', '=', 1, 20),
        ('NUMBER', '1', 1, 22),
        ('PUNCTUATION', ';', 1, 23),
        ('IDENTIFIER', 'b', 1, 25),
        ('OPERATOR', '=', 1, 27),
        ('NUMBER', '2', 1, 29),
        ('PUNCTUATION', ';', 1, 30),
        ('IDENTIFIER', 'a', 1, 32),
        ('OPERATOR', '+', 1, 34),
        ('IDENTIFIER', 'b', 1, 36),
        ('PUNCTUATION', ')', 1, 37),
    ]
    assert tokens == expected_tokens

def test_nested_grouped_statements():
    code = "define bar() -> (x = (y = 1; z = 2; y * z); x + 5);"
    tokens = tokenize(code)
    # print(tokens)  # Remove or comment out after verification

    expected_tokens = [
        ('KEYWORD', 'define', 1, 1),
        ('IDENTIFIER', 'bar', 1, 8),
        ('PUNCTUATION', '(', 1, 11),
        ('PUNCTUATION', ')', 1, 12),
        ('ARROW', '->', 1, 14),
        ('PUNCTUATION', '(', 1, 17),
        ('IDENTIFIER', 'x', 1, 18),
        ('OPERATOR', '=', 1, 20),
        ('PUNCTUATION', '(', 1, 22),
        ('IDENTIFIER', 'y', 1, 23),
        ('OPERATOR', '=', 1, 25),
        ('NUMBER', '1', 1, 27),
        ('PUNCTUATION', ';', 1, 28),
        ('IDENTIFIER', 'z', 1, 30),
        ('OPERATOR', '=', 1, 32),
        ('NUMBER', '2', 1, 34),
        ('PUNCTUATION', ';', 1, 35),
        ('IDENTIFIER', 'y', 1, 37),
        ('OPERATOR', '*', 1, 39),
        ('IDENTIFIER', 'z', 1, 41),
        ('PUNCTUATION', ')', 1, 42),
        ('PUNCTUATION', ';', 1, 43),
        ('IDENTIFIER', 'x', 1, 45),
        ('OPERATOR', '+', 1, 47),
        ('NUMBER', '5', 1, 49),
        ('PUNCTUATION', ')', 1, 50),
        ('PUNCTUATION', ';', 1, 51),
    ]
    assert tokens == expected_tokens

def test_raw_string_double_quotes():
    code = r'r"[A-Z]+\n"'
    tokens = tokenize(code)
    # print(tokens)  # Remove or comment out after verification

    expected_tokens = [
        ('RAW_STRING', '[A-Z]+\\n', 1, 1),  # Quotes removed
    ]
    assert tokens == expected_tokens

def test_raw_string_single_quotes():
    code = r"r'[A-Z]+\n'"
    tokens = tokenize(code)
    # print(tokens)  # Remove or comment out after verification

    expected_tokens = [
        ('RAW_STRING', '[A-Z]+\\n', 1, 1),  # Quotes removed
    ]
    assert tokens == expected_tokens

def test_regular_string_double_quotes():
    code = '"regular\\nstring"'
    tokens = tokenize(code)
    # print(tokens)  # Remove or comment out after verification

    expected_tokens = [
        ('STRING', 'regular\nstring', 1, 1),
    ]
    assert tokens == expected_tokens

def test_regular_string_single_quotes():
    code = "'regular\\nstring'"
    tokens = tokenize(code)
    # print(tokens)  # Remove or comment out after verification

    expected_tokens = [
        ('STRING', 'regular\nstring', 1, 1),
    ]
    assert tokens == expected_tokens

def test_combined_strings():
    code = r'r"[A-Z]+\n" "regular\nstring"'
    tokens = tokenize(code)
    # print(tokens)  # Remove or comment out after verification

    expected_tokens = [
        ('RAW_STRING', '[A-Z]+\\n', 1, 1),          # Quotes removed
        ('STRING', 'regular\nstring', 1, 13),
    ]
    assert tokens == expected_tokens

def test_invalid_raw_string():
    code = r'r"[A-Z]+\n'  # Missing closing quote
    lexer = Lexer(code)
    with pytest.raises(Lexer.SyntaxError) as exc_info:
        list(lexer.tokenize())
    assert "Unexpected character" in str(exc_info.value)

def test_mixed_code():
    code = textwrap.dedent("""\
r"[A-Z]+\s" "regular\nstring"
define example -> print("Hello")
""")
    tokens = tokenize(code)
    # print(tokens)  # Remove or comment out after verification

    expected_tokens = [
        ('RAW_STRING', '[A-Z]+\\s', 1, 1),        # Quotes removed
        ('STRING', 'regular\nstring', 1, 13),
        ('KEYWORD', 'define', 2, 1),
        ('IDENTIFIER', 'example', 2, 8),
        ('ARROW', '->', 2, 16),
        ('IDENTIFIER', 'print', 2, 19),
        ('PUNCTUATION', '(', 2, 24),
        ('STRING', 'Hello', 2, 25),
        ('PUNCTUATION', ')', 2, 32),
    ]
    assert tokens == expected_tokens

# 1. Test if the lexer correctly identifies the 'delay' keyword
def test_lexer_recognizes_delay_keyword():
    code = "delay(expensive_computation())"
    tokens = tokenize(code)
    # print(tokens)  # Remove or comment out after verification

    expected_tokens = [
        ('KEYWORD', 'delay', 1, 1),
        ('PUNCTUATION', '(', 1, 6),
        ('IDENTIFIER', 'expensive_computation', 1, 7),
        ('PUNCTUATION', '(', 1, 28),
        ('PUNCTUATION', ')', 1, 29),
        ('PUNCTUATION', ')', 1, 30),
    ]
    assert tokens == expected_tokens

# 2. Test if the lexer handles a combination of keywords and identifiers with delay
def test_lexer_handles_keywords_and_identifiers():
    code = "define delay_value = delay(expensive_computation())"
    tokens = tokenize(code)
    # print(tokens)  # Remove or comment out after verification

    expected_tokens = [
        ('KEYWORD', 'define', 1, 1),
        ('IDENTIFIER', 'delay_value', 1, 8),
        ('OPERATOR', '=', 1, 20),
        ('KEYWORD', 'delay', 1, 22),
        ('PUNCTUATION', '(', 1, 27),
        ('IDENTIFIER', 'expensive_computation', 1, 28),
        ('PUNCTUATION', '(', 1, 49),
        ('PUNCTUATION', ')', 1, 50),
        ('PUNCTUATION', ')', 1, 51),
    ]
    assert tokens == expected_tokens

# 3. Test if the lexer skips comments while identifying the 'delay' keyword
def test_lexer_skips_comments():
    code = textwrap.dedent("""\
        // This is a comment
        delay(expensive_computation())
        """)
    tokens = tokenize(code)
    # print(tokens)  # Remove or comment out after verification

    expected_tokens = [
        ('KEYWORD', 'delay', 2, 1),
        ('PUNCTUATION', '(', 2, 6),
        ('IDENTIFIER', 'expensive_computation', 2, 7),
        ('PUNCTUATION', '(', 2, 28),
        ('PUNCTUATION', ')', 2, 29),
        ('PUNCTUATION', ')', 2, 30),
    ]
    assert tokens == expected_tokens

# 4. Test if the lexer handles nested delay expressions
def test_lexer_handles_nested_delay():
    code = "delay(delay(expensive_computation()))"
    tokens = tokenize(code)
    # print(tokens)  # Remove or comment out after verification

    expected_tokens = [
        ('KEYWORD', 'delay', 1, 1),
        ('PUNCTUATION', '(', 1, 6),
        ('KEYWORD', 'delay', 1, 7),
        ('PUNCTUATION', '(', 1, 12),
        ('IDENTIFIER', 'expensive_computation', 1, 13),
        ('PUNCTUATION', '(', 1, 34),
        ('PUNCTUATION', ')', 1, 35),
        ('PUNCTUATION', ')', 1, 36),
        ('PUNCTUATION', ')', 1, 37),
    ]
    assert tokens == expected_tokens

def test_identifiers_with_special_characters():
    code = textwrap.dedent("""\
    $var* = 123;
    compute+/ = $var* + 456;
    result-? = compute+/ / 2;
    """)
    tokens = tokenize(code)
    expected_tokens = [
        ('IDENTIFIER', '$var*', 1, 1),
        ('OPERATOR', '=', 1, 7),
        ('NUMBER', '123', 1, 9),
        ('PUNCTUATION', ';', 1, 12),
        ('IDENTIFIER', 'compute+/', 2, 1),
        ('OPERATOR', '=', 2, 11),
        ('IDENTIFIER', '$var*', 2, 13),
        ('OPERATOR', '+', 2, 19),
        ('NUMBER', '456', 2, 21),
        ('PUNCTUATION', ';', 2, 24),
        ('IDENTIFIER', 'result-?', 3, 1),
        ('OPERATOR', '=', 3, 10),
        ('IDENTIFIER', 'compute+/', 3, 12),
        ('OPERATOR', '/', 3, 22),
        ('NUMBER', '2', 3, 24),
        ('PUNCTUATION', ';', 3, 25),
    ]
    assert tokens == expected_tokens

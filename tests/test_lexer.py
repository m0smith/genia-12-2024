import pytest
import sys
from pathlib import Path

# Add the parent directory to the system path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from genia.lexer import Lexer


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
        ('IDENTIFIER', 'fn', 1, 1),
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
        ('IDENTIFIER', 'fn', 1, 5), 
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

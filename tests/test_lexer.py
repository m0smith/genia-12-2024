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
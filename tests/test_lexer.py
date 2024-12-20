import pytest
import sys
from pathlib import Path

# Add the parent directory to the system path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from genia.interpreter import Lexer, Parser, GENIAInterpreter

@pytest.fixture
def interpreter():
    from genia.interpreter import GENIAInterpreter
    return GENIAInterpreter()

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

    
def test_expression_parsing():
    code = "1 + 2 * 3"
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = [
        {
            'type': 'operator',
            'operator': '+',
            'left': {'type': 'number', 'value': '1', 'line': 1, 'column': 1},
            'right': {
                'type': 'operator',
                'operator': '*',
                'left': {'type': 'number', 'value': '2', 'line': 1, 'column': 5},
                'right': {'type': 'number', 'value': '3', 'line': 1, 'column': 9}
            }
        }
    ]

    assert ast == expected_ast
    
def test_function_call_in_expression():
    code = "n * fact(n - 1)"
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = [
        {
            'type': 'operator',
            'operator': '*',
            'left': {'type': 'identifier', 'value': 'n', 'line': 1, 'column': 1},
            'right': {
                'type': 'function_call',
                'name': 'fact',
                'arguments': [
                    {
                        'type': 'operator',
                        'operator': '-',
                        'left': {'type': 'identifier', 'value': 'n', 'line': 1, 'column': 10},
                        'right': {'type': 'number', 'value': '1', 'line': 1, 'column': 14}
                    }
                ],
                'line': 1,
                'column': 5
            }
        }
    ]

    assert ast == expected_ast


def test_custom_function_call():
    code = "custom_function(42, 'hello', another_var);"
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = [
        {
            'type': 'function_call',
            'name': 'custom_function',
            'arguments': [
                {'type': 'number', 'value': '42', 'line': 1, 'column': 17},
                {'type': 'string', 'value': "'hello'", 'line': 1, 'column': 21},
                {'type': 'identifier', 'value': 'another_var', 'line': 1, 'column': 30}
            ],
            'line': 1,
            'column': 1
        }
    ]

    assert ast == expected_ast
    
def test_multi_arity_function_definition():
    code = """fn add() -> 0
    fn add(a) -> a
    fn add(a, b) -> a + b
    """
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = [
        {
            "type": "function_definition",
            "name": "add",
            "parameters": [],
            "guard": None,
            "body": {"type": "number", "value": "0", "line": 1, "column": 13},
            "line": 1,
            "column": 4,
        },
        {
            "type": "function_definition",
            "name": "add",
            "parameters": [{"type": "identifier", "value": "a"}],
            "guard": None,
            "body": {"type": "identifier", "value": "a", "line": 2, "column": 18},
            "line": 2,
            "column": 8,
        },
        {
            "type": "function_definition",
            "name": "add",
            "parameters": [
                {"type": "identifier", "value": "a"},
                {"type": "identifier", "value": "b"},
            ],
            "guard": None,
            "body": {
                "type": "operator",
                "operator": "+",
                "left": {"type": "identifier", "value": "a", "line": 3, "column": 21},
                "right": {"type": "identifier", "value": "b", "line": 3, "column": 25},
            },
            "line": 3,
            "column": 8,
        },
    ]

    assert ast == expected_ast

def test_function_with_guard():
    code = "fn fact(n) when n > 1 -> n * fact(n - 1)"
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = [
        {
            "type": "function_definition",
            "name": "fact",
            "parameters": [{"type": "identifier", "value": "n"}],
            "guard": {
                "type": "comparison",
                "operator": ">",
                "left": {"type": "identifier", "value": "n", "line": 1, "column": 17},
                "right": {"type": "number", "value": "1", "line": 1, "column": 21},
            },
            "body": {
                "type": "operator",
                "operator": "*",
                "left": {"type": "identifier", "value": "n", "line": 1, "column": 26},
                "right": {
                    "type": "function_call",
                    "name": "fact",
                    "arguments": [
                        {
                            "type": "operator",
                            "operator": "-",
                            "left": {"type": "identifier", "value": "n", "line": 1, "column": 35},
                            "right": {"type": "number", "value": "1", "line": 1, "column": 39},
                        }
                    ],
                    "line": 1,
                    "column": 30,
                },
            },
            "line": 1,
            "column": 4,
        }
    ]

    assert ast == expected_ast

    
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




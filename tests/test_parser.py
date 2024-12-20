import pytest
import sys
from pathlib import Path

# Add the parent directory to the system path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))


from genia.parser import Parser
from genia.lexer import Lexer

    
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


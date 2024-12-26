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
                {'type': 'string', 'value': "hello", 'line': 1, 'column': 21},
                {'type': 'identifier', 'value': 'another_var', 'line': 1, 'column': 28}
            ],
            'line': 1,
            'column': 1
        }
    ]

    assert ast == expected_ast
    
def test_multi_arity_function_definition():
    code = """fn add  () -> 0
                    | (a) -> a
                    | (a, b) -> a + b
    """
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast =  [
        {
            "type": "function_definition",
            "name": "add",
            "definitions": [
                {
                    "foreign": False,
                    "parameters": [],
                    "guard": None,
                    "body": {"type": "number", "value": "0", "line": 1, "column": 15},
                    "line": 1,
                    "column": 4,
                },
                {
                    "foreign": False,
                    "parameters": [
                        {"type": "identifier", "value": "a", "line": 2, "column": 24}
                    ],
                    "guard": None,
                    "body": {"type": "identifier", "value": "a", "line": 2, "column": 30},
                    "line": 1,
                    "column": 4,
                },
                {
                    "foreign": False,
                    "parameters": [
                        {"type": "identifier", "value": "a", "line": 3, "column": 24},
                        {"type": "identifier", "value": "b", "line": 3, "column": 27},
                    ],
                    "guard": None,
                    "body": {
                        "type": "operator",
                        "operator": "+",
                        "left": {"type": "identifier", "value": "a", "line": 3, "column": 33},
                        "right": {"type": "identifier", "value": "b", "line": 3, "column": 37},
                    },
                    "line": 1,
                    "column": 4,
                },
            ],
            "line": 1,
            "column": 4,
        }
    ]

    assert ast == expected_ast

def test_function_with_guard():
    code = "fn fact(n) when n > 1 -> n * fact(n - 1)"
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast =  [
        {
            "type": "function_definition",
            "name": "fact",
            "definitions": [
                {
                    "foreign": False,
                    "parameters": [
                        {"type": "identifier", "value": "n", "line": 1, "column": 9},
                    ],
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
            ],
            "line": 1,
            "column": 4,
        }
    ]

    assert ast == expected_ast

def test_multiple_arities():
    code = "fn foo() -> 0 | (_) -> 1;"
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    expected_ast = [{
        "type": "function_definition",
        "name": "foo",
        "definitions": [
            {
                "parameters": [],
                "guard": None,
                "body": {"type": "number", "value": "0", "line": 1, "column": 13},
                "line": 1,
                "column": 4,
                "foreign": False,
            },
            {
                "parameters": [{"type": "identifier", "value": "_", "line": 1, "column": 18}],
                "guard": None,
                "body": {"type": "number", "value": "1", "line": 1, "column": 24},
                "line": 1,
                "column": 4,
                "foreign": False,
            }
        ],
        "line": 1,
        "column": 4
    }]
    assert ast == expected_ast
    
def test_named_function_definition():
    code = "fn foo(x) -> x + 1 | (x, y) -> x * y"
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    expected = [
        {
            "type": "function_definition",
            "name": "foo",
            "definitions": [
                {
                    "parameters": [{"type": "identifier", "value": "x", "line": 1, "column": 8}],
                    "guard": None,
                    "body": {
                        "type": "operator",
                        "operator": "+",
                        "left": {"type": "identifier", "value": "x", "line": 1, "column": 14},
                        "right": {"type": "number", "value": "1", "line": 1, "column": 18},
                        # "line": 1,
                        # "column": 14,
                    },
                    "line": 1,
                    "column": 4,
                    "foreign": False,
                },
                {
                    "parameters": [
                        {"type": "identifier", "value": "x", "line": 1, "column": 23},
                        {"type": "identifier", "value": "y", "line": 1, "column": 26},
                    ],
                    "guard": None,
                    "body": {
                        "type": "operator",
                        "operator": "*",
                        "left": {"type": "identifier", "value": "x", "line": 1, "column": 32},
                        "right": {"type": "identifier", "value": "y", "line": 1, "column": 36},
                        # "line": 1,
                        # "column": 32,
                    },
                    "line": 1,
                    "column": 4,
                    "foreign": False,
                },
            ],
            "line": 1,
            "column": 4,
        }
    ]
    assert ast == expected

def test_anonymous_function_definition():
    code = "fn () -> 0 | (_) -> 1"
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    expected = [{
        "type": "function_definition",
        "name": None,
        "definitions": [
            {
                "parameters": [],
                "guard": None,
                "body": {"type": "number", "value": "0", "line": 1, "column": 10},
                "line": 1,
                "column": 1,
                "foreign": False,
            },
            {
                "parameters": [{"type": "identifier", "value": "_", "line": 1, "column": 15}],
                "guard": None,
                "body": {"type": "number", "value": "1", "line": 1, "column": 21},
                "line": 1,
                "column": 1,
                "foreign": False,
            },
        ],
        "line": 1,
        "column": 1,
    }]
    assert ast == expected
    
def test_named_function_with_parameters_line_column():
    code = "fn foo(x, y) -> x + y"
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    expected = [{
        "type": "function_definition",
        "name": "foo",
        "definitions": [
            {
                "parameters": [
                    {"type": "identifier", "value": "x", "line": 1, "column": 8},
                    {"type": "identifier", "value": "y", "line": 1, "column": 11},
                ],
                "guard": None,
                "body": {
                    "type": "operator",
                    "operator": "+",
                    "left": {"type": "identifier", "value": "x", "line": 1, "column": 17},
                    "right": {"type": "identifier", "value": "y", "line": 1, "column": 21}
                },
                "line": 1,
                "column": 4,
                "foreign": False,
            }
        ],
        "line": 1,
        "column": 4
    }]

    assert ast == expected
    
def test_anonymous_function_with_parameters_line_column():
    code = "fn (_) -> 1"
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    expected = [{
        "type": "function_definition",
        "name": None,
        "definitions": [
            {
                "parameters": [{"type": "identifier", "value": "_", "line": 1, "column": 5}],
                "guard": None,
                "body": {"type": "number", "value": "1", "line": 1, "column": 11},
                "line": 1,
                "column": 1,
                "foreign": False,
            }
        ],
        "line": 1,
        "column": 1
    }]

    assert ast == expected

def test_named_function_with_guard():
    code = "fn foo(x) when x > 1 -> x * 2"
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    expected = [{
        "type": "function_definition",
        "name": "foo",
        "definitions": [
            {
                "parameters": [{"type": "identifier", "value": "x", "line": 1, "column": 8}],
                "guard": {
                    "type": "comparison",
                    "operator": ">",
                    "left": {"type": "identifier", "value": "x", "line": 1, "column": 16},
                    "right": {"type": "number", "value": "1", "line": 1, "column": 20},
                },
                "body": {
                    "type": "operator",
                    "operator": "*",
                    "left": {"type": "identifier", "value": "x", "line": 1, "column": 25},
                    "right": {"type": "number", "value": "2", "line": 1, "column": 29},
                },
                "line": 1,
                "column": 4,
                "foreign": False,
            }
        ],
        "line": 1,
        "column": 4,
    }]
    
    assert ast == expected

def test_ffi_simple():
    code = 'fn foreign rem(x,y) -> "math.remainder"'
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    import math
    expected = [{
        'column': 12, 
        'definitions': 
            [{'body': math.remainder , 
                'parameters': [
                    {'column': 16, 'line': 1, 'type': 'identifier', 'value': 'x'},
                    {'column': 18, 'line': 1, 'type': 'identifier', 'value': 'y'},
                ],
                'column': 12, 
                'guard': None, 
                'line': 1, 
                'foreign': True,
                'column': 12}], 
        'line': 1, 
        'name': 'rem',
        'type': 'function_definition', 
    }]
    assert ast == expected
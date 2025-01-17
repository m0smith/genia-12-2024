
import pytest
import sys
from pathlib import Path

# Add the parent directory to the system path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from genia.lexer import Lexer
from genia.parser import Parser

def strip_metadata(ast):
    """
    Recursively remove 'line' and 'column' keys from the AST.
    """
    if isinstance(ast, dict):
        return {k: strip_metadata(v) for k, v in ast.items() if k not in {'line', 'column'}}
    elif isinstance(ast, list):
        return [strip_metadata(item) for item in ast]
    else:
        return ast


def parse(code):
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()
    return ast

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
                'right': {'type': 'number', 'value': '3', 'line': 1, 'column': 9},
                'line': 1,
                'column': 7  # Included in expected AST
            },
            'line': 1,
            'column': 3
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
                        'right': {'type': 'number', 'value': '1', 'line': 1, 'column': 14},
                        'line': 1,
                        'column': 12
                    }
                ],
                'line': 1,
                'column': 5
            },
            'line': 1,
            'column': 3
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
                {'type': 'string', 'value': "hello", 'line': 1, 'column': 26},
                {'type': 'identifier', 'value': 'another_var', 'line': 1, 'column': 33}
            ],
            'line': 1,
            'column': 1
        }
    ]

    assert strip_metadata(ast) == strip_metadata(expected_ast)

def test_multi_arity_function_definition():
    code = """fn add() -> 0
                | (a) -> a
                | (a, b) -> a + b
    """
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = [
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
                        "line": 3,
                        "column": 35
                    },
                    "line": 1,
                    "column": 4,
                },
            ],
            "line": 1,
            "column": 4,
        }
    ]

    assert strip_metadata(ast) == strip_metadata(expected_ast)

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
            "definitions": [
                {
                    "parameters": [{"type": "identifier", "value": "n", "line": 1, "column": 9}],
                    "guard": {
                        "type": "comparison",
                        "operator": ">",
                        "left": {"type": "identifier", "value": "n", "line": 1, "column": 17},
                        "right": {"type": "number", "value": "1", "line": 1, "column": 21},
                        "line": 1,
                        "column": 19
                    },
                    "body": {
                        "type": "operator",
                        "operator": "*",
                        "left": {"type": "identifier", "value": "n", "line": 1, "column": 25},
                        "right": {
                            "type": "function_call",
                            "name": "fact",
                            "arguments": [
                                {
                                    "type": "operator",
                                    "operator": "-",
                                    "left": {"type": "identifier", "value": "n", "line": 1, "column": 35},
                                    "right": {"type": "number", "value": "1", "line": 1, "column": 39},
                                    "line": 1,
                                    "column": 37
                                }
                            ],
                            "line": 1,
                            "column": 30
                        },
                        "line": 1,
                        "column": 25
                    },
                    "foreign": False,
                    "line": 1,
                    "column": 4,
                }
            ],
            "line": 1,
            "column": 4,
        }
    ]

    assert strip_metadata(ast) == strip_metadata(expected_ast)

def test_ffi_simple():
    code = 'fn rem(x,y) -> foreign "math.remainder"'
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    import math
    expected = [
        {
            'type': 'function_definition',
            'name': 'rem',
            'definitions': [
                {
                    'parameters': [
                        {'type': 'identifier', 'value': 'x', 'line': 1, 'column': 8},
                        {'type': 'identifier', 'value': 'y', 'line': 1, 'column': 10},
                    ],
                    'guard': None,
                    'body': math.remainder,
                    'foreign': True,
                    'line': 1,
                    'column': 4,
                }
            ],
            'line': 1,
            'column': 4
        }
    ]
    assert ast == expected

def test_range():
    code = "1..10"
    result = parse(code)
    expected = [{
        'type': 'range',
        'start': {'type': 'number', 'value': '1', 'line': 1, 'column': 1},
        'end': {'type': 'number', 'value': '10', 'line': 1, 'column': 4}
    }]
    assert result == expected

def test_list_destructuring():
    code = "[first, ..rest]"
    result = parse(code)
    expected = [{
        'type': 'list_pattern',
        'elements': [
            {'type': 'identifier', 'value': 'first', 'line': 1, 'column': 2},
            {'type': 'rest', 'value': 'rest', 'line': 1, 'column': 9}
        ]
    }]
    assert strip_metadata(result) == strip_metadata(expected)

def test_list_with_start_and_end():
    code = "[first, ..rest, last]"
    result = parse(code)
    expected = [{
        'type': 'list_pattern',
        'elements': [
            {'type': 'identifier', 'value': 'first', 'line': 1, 'column': 2},
            {'type': 'rest', 'value': 'rest', 'line': 1, 'column': 9},
            {'type': 'identifier', 'value': 'last', 'line': 1, 'column': 17}
        ]
    }]
    assert strip_metadata(result) == strip_metadata(expected)

def test_parser_dynamic_range():
    code = """
start = 10
end = 15
start..end
"""
    result = parse(code)
    expected = [
        {
            'type': 'assignment',
            'identifier': 'start',
            'value': {'type': 'number', 'value': '10', 'line': 2, 'column': 5},
            'line': 2,
            'column': 1
        },
        {
            'type': 'assignment',
            'identifier': 'end',
            'value': {'type': 'number', 'value': '15', 'line': 3, 'column': 11},
            'line': 3,
            'column': 1
        },
        {
            'type': 'range',
            'start': {'type': 'identifier', 'value': 'start', 'line': 4, 'column': 5},
            'end': {'type': 'identifier', 'value': 'end', 'line': 4, 'column': 12}
        },
    ]
    assert strip_metadata(result) == strip_metadata(expected)

def test_parser_list_pattern_ast():
    code = "fn foo([_, ..r]) -> [99, ..r]"
    ast = parse(code)

    expected_ast = [{
        "type": "function_definition",
        "name": "foo",
        "definitions": [
            {
                "parameters": [
                    {
                        "type": "list_pattern",
                        "elements": [
                            {"type": "identifier", "value": "_", "line": 1, "column": 9},
                            {"type": "rest", "value": "r", "line": 1, "column": 12}
                        ]
                    }
                ],
                "guard": None,
                "body": {
                    "type": 'list_pattern',
                    "elements": [
                        {'type': 'number', 'value': '99', 'line': 1, 'column': 22},
                        {'type': 'rest', 'value': 'r', 'line': 1, 'column': 26}
                    ]
                },
                "foreign": False,
                "line": 1,
                "column": 4
            }
        ],
        "line": 1,
        "column": 4
    }]
    assert strip_metadata(ast) == strip_metadata(expected_ast)

def test_parser_grouped_expression():
    code = "fn foo() -> (a + b);"
    ast = parse(code)

    expected_ast = [
        {
            "type": "function_definition",
            "name": "foo",
            "definitions": [
                {
                    "parameters": [],
                    "guard": None,
                    "body": {
                        "type": "operator",
                        "operator": "+",
                        "left": {"type": "identifier", "value": "a", "line": 1, "column": 14},
                        "right": {"type": "identifier", "value": "b", "line": 1, "column": 18},
                        "line": 1,
                        "column": 16
                    },
                    "foreign": False,
                    "line": 1,
                    "column": 4
                }
            ],
            "line": 1,
            "column": 4
        }
    ]

    assert ast == expected_ast

def test_parser_grouped_statements():
    code = "fn bar() -> (a = 1; b = 2; a + b);"
    ast = parse(code)

    expected_ast = [
        {
            'type': 'function_definition',
            'name': 'bar',
            'definitions': [
                {
                    'parameters': [],
                    'guard': None,
                    'foreign': False,
                    'body': {
                        'type': 'group',
                        'statements': [
                            {
                                'type': 'assignment',
                                'identifier': 'a',
                                'value': {'type': 'number', 'value': '1', 'line': 1, 'column': 14},
                                'line': 1,
                                'column': 4
                            },
                            {
                                'type': 'assignment',
                                'identifier': 'b',
                                'value': {'type': 'number', 'value': '2', 'line': 1, 'column': 21},
                                'line': 1,
                                'column': 14
                            },
                            {
                                'type': 'operator',
                                'operator': '+',
                                'left': {'type': 'identifier', 'value': 'a', 'line': 1, 'column': 28},
                                'right': {'type': 'identifier', 'value': 'b', 'line': 1, 'column': 32},
                                'line': 1,
                                'column': 30
                            }
                        ]
                    },
                    'line': 1,
                    'column': 4
                }
            ],
            'line': 1,
            'column': 4
        }
    ]

    assert strip_metadata(ast) == strip_metadata(expected_ast)

def test_parser_raw_string():
    code = r'r"[A-Z]+\n"'
    ast = parse(code)
    expected_ast = [{
        'type': 'raw_string',
        'value': '[A-Z]+\\n',
        'line': 1,
        'column': 7
    }]
    assert strip_metadata(ast) == strip_metadata(expected_ast)

def test_parser_regular_and_raw_strings():
    code = '''r"[A-Z]+" "regular"'''
    ast = parse(code)
    expected_ast = [
        {'type': 'raw_string', 'value': '[A-Z]+', 'line': 1, 'column': 7},
        {'type': 'string', 'value': 'regular', 'line': 1, 'column': 21},
    ]
    assert strip_metadata(ast) == strip_metadata(expected_ast)

# 1. Test if the parser correctly parses a simple delay expression
def test_parser_simple_delay():
    code = "delay(42)"
    ast = parse(code)
    assert ast == [
        {
            'type': 'delay',
            'line': 1,
            'column': 1,
            'expression': {'type': 'number', 'value': '42', 'line': 1, 'column': 7}
        }
    ]

# 2. Test if the parser handles a delay expression with an identifier
def test_parser_delay_with_identifier():
    code = "delay(expensive_computation)"
    ast = parse(code)
    assert ast == [
        {
            'type': 'delay',
            'line': 1,
            'column': 1,
            'expression': {'type': 'identifier', 'value': 'expensive_computation', 'line': 1, 'column': 7}
        }
    ]

# 3. Test if the parser throws an error for missing parentheses in delay
def test_parser_missing_parentheses():
    code = "delay 42"
    with pytest.raises(SyntaxError, match="Expected '\(' after 'delay'"):
        parse(code)

# 4. Test if the parser handles nested delay expressions
def test_parser_nested_delay():
    code = "delay(delay(42))"
    ast = parse(code)
    assert ast == [
        {
            'type': 'delay',
            'line': 1,
            'column': 1,
            'expression': {
                'type': 'delay',
                'line': 1,
                'column': 7,
                'expression': {'type': 'number', 'value': '42', 'line': 1, 'column': 13}
            }
        }
    ]

# 5. Test if the parser handles a delay expression within a function call
def test_parser_delay_in_function_call():
    code = "fn compute() -> delay(expensive_computation())"
    ast = parse(code)
    expected_ast = [
        {
            'type': 'function_definition',
            'name': 'compute',
            'definitions': [
                {
                    'parameters': [],
                    'guard': None,
                    'foreign': False,
                    'body': {
                        'type': 'delay',
                        'line': 1,
                        'column': 17,
                        'expression': {
                            'type': 'function_call',
                            'name': 'expensive_computation',
                            'arguments': [],
                            'line': 1,
                            'column': 23
                        }
                    },
                    'line': 1,
                    'column': 4
                }
            ],
            'line': 1,
            'column': 4
        }
    ]
    assert ast == expected_ast

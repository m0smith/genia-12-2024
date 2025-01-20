

import pytest
import sys
from pathlib import Path

# Add the parent directory to the system path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from genia.parser import Parser
from genia.lexer import Lexer

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
            'type': 'expression_statement',
            'expression': {
                'type': 'operator',
                'operator': '+',
                'left': {'type': 'number', 'value': '1', 'line': 1, 'column': 1},
                'right': {
                    'type': 'operator',
                    'operator': '*',
                    'left': {'type': 'number', 'value': '2', 'line': 1, 'column': 5},
                    'right': {'type': 'number', 'value': '3', 'line': 1, 'column': 9},
                    'line': 1,
                    'column': 7
                },
                'line': 1,
                'column': 3
            },
            'line': 1,
            'column': 1
        }
    ]

    assert strip_metadata(ast) == strip_metadata(expected_ast)


def test_function_call_in_expression():
    code = "n * fact(n - 1)"
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = [
        {
            'type': 'expression_statement',
            'expression': {
                'type': 'operator',
                'operator': '*',
                'left': {'type': 'identifier', 'value': 'n'},
                'right': {
                    'type': 'function_call',
                    'name': 'fact',
                    'arguments': [
                        {
                            'type': 'operator',
                            'operator': '-',
                            'left': {'type': 'identifier', 'value': 'n'},
                            'right': {'type': 'number', 'value': '1'}
                        }
                    ]
                }
            }
        }
    ]

    assert strip_metadata(ast) == strip_metadata(expected_ast)


def test_another_expression():
    code = "a + b"
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = [
        {
            'type': 'expression_statement',
            'expression': {
                'type': 'operator',
                'operator': '+',
                'left': {'type': 'identifier', 'value': 'a'},
                'right': {'type': 'identifier', 'value': 'b'}
            }
        }
    ]

    assert strip_metadata(ast) == strip_metadata(expected_ast)


def test_custom_function_call():
    code = "custom_function(42, 'hello', another_var);"
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    expected_ast = [
        {
            'type': 'expression_statement',
            'expression': {
                'type': 'function_call',
                'name': 'custom_function',
                'arguments': [
                    {'type': 'number', 'value': '42'},
                    {'type': 'string', 'value': 'hello'},
                    {'type': 'identifier', 'value': 'another_var'}
                ]
            }
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
                    "parameters": [],
                    "guard": None,
                    "body": {"type": "number", "value": "0"},
                    "foreign": False
                },
                {
                    "parameters": [
                        {"type": "identifier", "value": "a"}
                    ],
                    "guard": None,
                    "body": {"type": "identifier", "value": "a"},
                    "foreign": False
                },
                {
                    "parameters": [
                        {"type": "identifier", "value": "a"},
                        {"type": "identifier", "value": "b"},
                    ],
                    "guard": None,
                    "body": {
                        "type": "operator",
                        "operator": "+",
                        "left": {"type": "identifier", "value": "a"},
                        "right": {"type": "identifier", "value": "b"}
                    },
                    "foreign": False
                },
            ]
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
                    "parameters": [{"type": "identifier", "value": "n"}],
                    "guard": {
                        "type": "comparator",
                        "operator": ">",
                        "left": {"type": "identifier", "value": "n"},
                        "right": {"type": "number", "value": "1"}
                    },
                    "body": {
                        "type": "operator",
                        "operator": "*",
                        "left": {"type": "identifier", "value": "n"},
                        "right": {
                            "type": "function_call",
                            "name": "fact",
                            "arguments": [
                                {
                                    "type": "operator",
                                    "operator": "-",
                                    "left": {"type": "identifier", "value": "n"},
                                    "right": {"type": "number", "value": "1"}
                                }
                            ]
                        }
                    },
                    "foreign": False
                }
            ]
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
                        {'type': 'identifier', 'value': 'y',
                            'line': 1, 'column': 10},
                    ],
                    'guard': None,
                    'body': 'math.remainder',
                    'foreign': True,
                    'line': 1,
                    'column': 4,
                }
            ],
            'line': 1,
            'column': 4
        }
    ]
    assert strip_metadata(ast) == strip_metadata(expected)


def test_range():
    code = "1..10"
    result = parse(code)
    expected = [{
        'type': 'expression_statement',
        'expression':
            {'type': 'operator', 'operator': '..',
             'left': {'type': 'number', 'value': '1', 'line': 1, 'column': 1},
             'right': {'type': 'number', 'value': '10', 'line': 1, 'column': 4},
             'line': 1, 'column': 2}
    }
    ]
    assert result == expected


def test_list_destructuring():
    code = "[first, ..rest]"
    result = parse(code)
    expected = [{
        'type': 'expression_statement',
        'expression': {
            'type': 'list',
            'elements': [
                {'type': 'identifier', 'value': 'first', 'line': 1, 'column': 2},
                {'type': 'unary_operator', 'operator': '..', 'line': 1,
                    'column': 9, 'operand': {'value': 'rest', 'type': "identifier"}}
            ]
        }
    }]
    assert strip_metadata(result) == strip_metadata(expected)


def test_list_with_start_and_end():
    code = "[first, ..rest, last]"
    result = parse(code)
    expected = [{
        'type': 'expression_statement',
        'expression': {
                'type': 'list',
                'elements': [
                    {'type': 'identifier', 'value': 'first', 'line': 1, 'column': 2},
                    {'type': 'unary_operator', 'operator': '..', 'operand': {
                        'value': 'rest', 'type': "identifier"}, 'line': 1, 'column': 9},
                    {'type': 'identifier', 'value': 'last', 'line': 1, 'column': 17}
                ]
        }
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
            'value': {'type': 'number', 'value': '10'},
        },
        {
            'type': 'assignment',
            'identifier': 'end',
            'value': {'type': 'number', 'value': '15'},
        },
        {
            'type': 'expression_statement',
            'expression': {
                'type': 'operator', 'operator': '..',
                'left': {'type': 'identifier', 'value': 'start'},
                'right': {'type': 'identifier', 'value': 'end'}}},
    ]
    assert strip_metadata(result) == strip_metadata(expected)


def test_parser_list_pattern_ast():
    code = "fn foo([_, ..r]) -> [99, ..r]"
    ast = parse(code)
    expected_ast = [
        {
            'type': 'function_definition', 'name': 'foo',
            'definitions': [
                {'parameters': [
                    {
                        'type': 'list_pattern',
                        'elements':
                        [
                            {'type': 'wildcard'},
                            {
                                'type': 'unary_operator', 'operator': '..',
                                'operand': {'type': 'identifier', 'value': 'r'}
                            }
                        ]
                    }],
                 'guard': None,
                 'body': {
                     'type': 'list',
                     'elements': [
                         {'type': 'number', 'value': '99'},
                         {
                             'type': 'unary_operator',
                             'operator': '..',
                             'operand': {'type': 'identifier', 'value': 'r'}}]},
                 'foreign': False}]}
    ]
    assert strip_metadata(ast) == strip_metadata(expected_ast)

# tests/test_parser.py


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
                        "left": {"type": "identifier", "value": "a"},
                        "right": {"type": "identifier", "value": "b"},
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
    assert strip_metadata(ast) == strip_metadata(expected_ast)


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
                        'type': 'grouped_statements',
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
        'type': 'expression_statement',
        'expression': {
                'type': 'raw_string',
                'value': '[A-Z]+\\n',
                'line': 1,
                'column': 7
        }
    }]
    assert strip_metadata(ast) == strip_metadata(expected_ast)


def test_parser_unary():
    code = r'-1'
    ast = parse(code)
    expected_ast = [{
        'type': 'expression_statement',
        'expression': {
            'type': 'unary_operator',
            'operator': '-',
            'operand':  {'type': 'number', 'value': '1'},
            'line': 1,
            'column': 1
        }
    }]
    assert strip_metadata(ast) == strip_metadata(expected_ast)


def test_parser_regular_and_raw_strings():
    code = '''r"[A-Z]+" "regular"'''
    ast = parse(code)
    expected_ast = [
        {
            'type': 'expression_statement',
            'expression': {
                'type': 'raw_string',
                'value': '[A-Z]+'
            }
        },
        {
            'type': 'expression_statement',
            'expression': {
                'type': 'string',
                'value': 'regular'
            }
        },
    ]
    assert strip_metadata(ast) == strip_metadata(expected_ast)


# 1. Test if the parser correctly parses a simple delay expression
def test_parser_simple_delay():
    code = "delay(42)"
    ast = parse(code)
    expected_ast = [
        {
            'type': 'expression_statement',
            'expression': {
                'type': 'delay',
                'line': 1,
                'column': 1,
                'expression': {'type': 'number', 'value': '42', 'line': 1, 'column': 7}
            }
        }
    ]
    assert strip_metadata(ast) == strip_metadata(expected_ast)

# 2. Test if the parser handles a delay expression with an identifier


def test_parser_delay_with_identifier():
    code = "delay(expensive_computation)"
    ast = parse(code)
    expected_ast = [
        {
            'type': 'expression_statement',
            'expression': {
                'type': 'delay',
                'line': 1,
                'column': 1,
                'expression': {'type': 'identifier', 'value': 'expensive_computation', 'line': 1, 'column': 7}
            }
        }
    ]
    assert strip_metadata(ast) == strip_metadata(expected_ast)

# 3. Test if the parser throws an error for missing parentheses in delay


def test_parser_missing_parentheses():
    code = "delay 42"
    with pytest.raises(Parser.SyntaxError, match="Expected '\(' after 'delay'"):
        parse(code)

# 4. Test if the parser handles nested delay expressions


def test_parser_nested_delay():
    code = "delay(delay(42))"
    ast = parse(code)
    expected_ast = [
        {
            'type': 'expression_statement',
            'expression': {
                'type': 'delay',
                'expression': {
                    'type': 'delay',
                    'expression': {'type': 'number', 'value': '42'}
                }
            }
        },
    ]
    assert strip_metadata(ast) == strip_metadata(expected_ast)

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
    assert strip_metadata(ast) == strip_metadata(expected_ast)


def test_parser_named_function_with_literal():
    code = "fn fact(0) -> 1;"
    lexer = Lexer(code)
    tokens = list(lexer.tokenize())
    parser = Parser(tokens)
    ast = parser.parse()
    expected_ast = [
        {
            'type': 'function_definition',
            'name': 'fact',
            'definitions': [
                {
                    'parameters': [{'type': 'number_literal', 'value': 0, 'line': 1, 'column': 10}],
                    'guard': None,
                    'body': {'type': 'number', 'value': '1', 'line': 1, 'column': 15},
                    'foreign': False,
                    'line': 1,
                    'column': 15
                }
            ],
            'line': 1,
            'column': 5
        }
    ]
    assert strip_metadata(ast) == strip_metadata(expected_ast)


def test_parser_anonymous_function():
    code = "fn (y) -> y + 1;"
    lexer = Lexer(code)
    tokens = list(lexer.tokenize())
    parser = Parser(tokens)
    ast = parser.parse()
    expected_ast = [
        {
            'type': 'function_definition',
            'name': None,
            'definitions': [
                {
                    'parameters': [{'type': 'identifier', 'value': 'y', 'line': 1, 'column': 5}],
                    'guard': None,
                    'body': {
                        'type': 'operator',
                        'operator': '+',
                        'left': {'type': 'identifier', 'value': 'y', 'line': 1, 'column': 10},
                        'right': {'type': 'number', 'value': '1', 'line': 1, 'column': 14},
                        'line': 1,
                        'column': 12
                    },
                    'foreign': False,
                    'line': 1,
                    'column': 12
                }
            ],
            'line': 1,
            'column': 1
        }
    ]
    assert strip_metadata(ast) == strip_metadata(expected_ast)


def test_parser_multiple_spread_operators():
    """
    Test parsing of a function definition with multiple spread operators in list patterns.

    Function Definition:
        fn process([..a, ..b]) -> [..a, ..b]


    """
    code = "fn process([..a, ..b]) -> [..a, ..b]"
    ast = parse(code)

    expected_ast = [
        {'type': 'function_definition', 'name': 'process', 'definitions': [{'parameters': [{'type': 'list_pattern', 'elements': [{'type': 'unary_operator', 'operator': '..', 'operand': {'type': 'identifier', 'value': 'a', 'line': 1, 'column': 15}, 'line': 1, 'column': 13}, {'type': 'unary_operator', 'operator': '..', 'operand': {'type': 'identifier', 'value': 'b', 'line': 1, 'column': 20}, 'line': 1,
                                                                                                                                                                                                                                                                                   'column': 18}], 'line': 1, 'column': 12}], 'guard': None, 'body': {'type': 'list', 'elements': [{'type': 'unary_operator', 'operator': '..', 'operand': {'type': 'identifier', 'value': 'a', 'line': 1, 'column': 30}, 'line': 1, 'column': 28}, {'type': 'unary_operator', 'operator': '..', 'operand': {'type': 'identifier', 'value': 'b', 'line': 1, 'column': 35}, 'line': 1, 'column': 33}]}, 'foreign': False}]}]

    assert strip_metadata(ast) == strip_metadata(
        expected_ast), f"Expected AST does not match actual AST.\nExpected: {expected_ast}\nActual: {ast}"

from genia.lexer import Lexer
from genia.parser import Parser
import pytest
import sys
from pathlib import Path

# Add the parent directory to the system path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))


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
                        {"type": "identifier", "value": "a",
                            "line": 3, "column": 24},
                        {"type": "identifier", "value": "b",
                            "line": 3, "column": 27},
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

    expected_ast = [
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
                        {"type": "identifier", "value": "x",
                            "line": 1, "column": 23},
                        {"type": "identifier", "value": "y",
                            "line": 1, "column": 26},
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
    code = 'fn rem(x,y) -> foreign "math.remainder"'
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    import math
    expected = [{
        'column': 4,
        'definitions':
            [{'body': math.remainder,
                'parameters': [
                    {'column': 8, 'line': 1, 'type': 'identifier', 'value': 'x'},
                    {'column': 10, 'line': 1, 'type': 'identifier', 'value': 'y'},
                ],
                'column': 4,
                'guard': None,
                'line': 1,
                'foreign': True,
                'column': 4}],
        'line': 1,
        'name': 'rem',
        'type': 'function_definition',
    }]
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
            {'type': 'rest', 'value': 'rest', 'line': 1, 'column': 9},
            {
                'column': 11,
                'line': 1,
                'type': 'identifier',
                'value': 'rest',
            },
        ]
    }]
    assert result == expected


def test_list_with_start_and_end():
    code = "[first, ..rest, last]"
    result = parse(code)
    expected = [{
        'type': 'list_pattern',
        'elements': [
            {'type': 'identifier', 'value': 'first', 'line': 1, 'column': 2},
            {'type': 'rest', 'value': 'rest', 'line': 1, 'column': 9},
            {'type': 'identifier', 'value': 'rest', 'line': 1, 'column': 11},
            {'type': 'identifier', 'value': 'last', 'line': 1, 'column': 17}
        ]
    }]
    assert result == expected


def test_parser_dynamic_range():
    code = """
    start = 10
    end = 15
    start..end
    """
    result = parse(code)
    expected = [
        {
            'column': 5,
            'identifier': 'start',
            'line': 2,
            'type': 'assignment',
            'value': {
                'column': 13,
                'line': 2,
                'type': 'number',
                'value': '10',
            },
        },
        {
            'column': 5,
            'identifier': 'end',
            'line': 3,
            'type': 'assignment',
            'value': {
                'column': 11,
                'line': 3,
                'type': 'number',
                'value': '15',
            },
        },
        {
            'end': {
                'column': 12,
                'line': 4,
                'type': 'identifier',
                'value': 'end',
            },
            'start': {
                'column': 5,
                'line': 4,
                'type': 'identifier',
                'value': 'start',
            },
            'type': 'range',
        },
    ]
    assert result == expected


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
                            {"type": "identifier", "value": "_",
                                "line": 1, "column": 9},
                            {"type": "rest", "value": "r"}
                        ]
                    }
                ],
                "body": {
                    "type": "list_pattern",
                    "elements": [
                        {"type": "number", "value": "99", "line": 1, "column": 22},
                        {"type": "rest", "value": "rest", "line": 1, "column": 26},
                        {"type": "identifier", "value": "r", "line": 1, "column": 28}
                    ]
                },
                "guard": None,
                'foreign': False,
                "line": 1,
                "column": 4
            }
        ],
        "line": 1,
        "column": 4
    }]

    assert ast == expected_ast


def test_parser_grouped_expression():
    code = "fn foo() -> (a + b);"
    # tokens = [
    #     ('KEYWORD', 'fn', 1, 1),
    #     ('IDENTIFIER', 'foo', 1, 4),
    #     ('PUNCTUATION', '(', 1, 7),
    #     ('PUNCTUATION', ')', 1, 8),
    #     ('ARROW', '->', 1, 10),
    #     ('PUNCTUATION', '(', 1, 13),
    #     ('IDENTIFIER', 'a', 1, 14),
    #     ('OPERATOR', '+', 1, 16),
    #     ('IDENTIFIER', 'b', 1, 18),
    #     ('PUNCTUATION', ')', 1, 19),
    #     ('PUNCTUATION', ';', 1, 20),
    # ]

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
                    },
                    "line": 1,
                    "column": 4,
                    'foreign': False,
                }
            ],
            "line": 1,
            "column": 4
        }
    ]

    assert ast == expected_ast


def test_parser_grouped_statements():
    code = "fn bar() -> (a = 1; b = 2; a + b);"
    # tokens = [
    #     ('KEYWORD', 'fn', 1, 1),
    #     ('IDENTIFIER', 'bar', 1, 4),
    #     ('PUNCTUATION', '(', 1, 7),
    #     ('PUNCTUATION', ')', 1, 8),
    #     ('ARROW', '->', 1, 10),
    #     ('PUNCTUATION', '(', 1, 13),
    #     ('IDENTIFIER', 'a', 1, 14),
    #     ('OPERATOR', '=', 1, 16),
    #     ('NUMBER', '1', 1, 18),
    #     ('PUNCTUATION', ';', 1, 19),
    #     ('IDENTIFIER', 'b', 1, 21),
    #     ('OPERATOR', '=', 1, 23),
    #     ('NUMBER', '2', 1, 25),
    #     ('PUNCTUATION', ';', 1, 26),
    #     ('IDENTIFIER', 'a', 1, 28),
    #     ('OPERATOR', '+', 1, 30),
    #     ('IDENTIFIER', 'b', 1, 32),
    #     ('PUNCTUATION', ')', 1, 33),
    #     ('PUNCTUATION', ';', 1, 34),
    # ]

    ast = parse(code)

    expected_ast = [
        {'type': 'function_definition', 
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
                                'type': 'operator', 
                                'operator': '=', 
                                
                                'left': {'type': 'identifier', 'value': 'a', 'line': 1, 'column': 14}, 
                                'right': {'type': 'number', 'value': '1', 'line': 1, 'column': 18}}, 
                            {
                                'type': 'operator', 'operator': '=', 
                                'left': {'type': 'identifier', 'value': 'b', 'line': 1, 'column': 21}, 
                                'right': {'type': 'number', 'value': '2', 'line': 1, 'column': 25}
                            }, 
                            {
                                'type': 'operator', 'operator': '+', 
                                'left': {'type': 'identifier', 'value': 'a', 'line': 1, 'column': 28}, 
                                'right': {'type': 'identifier', 'value': 'b', 'line': 1, 'column': 32}}]}, 
                    'line': 1, 
                    'column': 4}], 
            'line': 1, 
            'column': 4}
    ]

    assert ast == expected_ast

def test_parser_nested_grouped_statements():
    code = "fn baz() -> (x = (y = 1; z = 2; y * z); x + 5);"
    # tokens = [
    #     ('KEYWORD', 'fn', 1, 1),
    #     ('IDENTIFIER', 'baz', 1, 4),
    #     ('PUNCTUATION', '(', 1, 7),
    #     ('PUNCTUATION', ')', 1, 8),
    #     ('ARROW', '->', 1, 10),
    #     ('PUNCTUATION', '(', 1, 13),
    #     ('IDENTIFIER', 'x', 1, 14),
    #     ('OPERATOR', '=', 1, 16),
    #     ('PUNCTUATION', '(', 1, 18),
    #     ('IDENTIFIER', 'y', 1, 19),
    #     ('OPERATOR', '=', 1, 21),
    #     ('NUMBER', '1', 1, 23),
    #     ('PUNCTUATION', ';', 1, 24),
    #     ('IDENTIFIER', 'z', 1, 26),
    #     ('OPERATOR', '=', 1, 28),
    #     ('NUMBER', '2', 1, 30),
    #     ('PUNCTUATION', ';', 1, 31),
    #     ('IDENTIFIER', 'y', 1, 33),
    #     ('OPERATOR', '*', 1, 35),
    #     ('IDENTIFIER', 'z', 1, 37),
    #     ('PUNCTUATION', ')', 1, 38),
    #     ('PUNCTUATION', ';', 1, 39),
    #     ('IDENTIFIER', 'x', 1, 41),
    #     ('OPERATOR', '+', 1, 43),
    #     ('NUMBER', '5', 1, 45),
    #     ('PUNCTUATION', ')', 1, 46),
    #     ('PUNCTUATION', ';', 1, 47),
    # ]

    ast = parse(code)

    expected_ast = [
        {
            'type': 'function_definition', 
            'name': 'baz', 
            'definitions': [
                {
                    'parameters': [], 
                    'guard': None, 
                    'foreign': False, 
                    'body': {
                        'type': 'group', 
                        'statements': [
                            {
                                'type': 'operator', 
                                'operator': '=', 
                                'left': {'type': 'identifier', 'value': 'x', 'line': 1, 'column': 14}, 
                                'right': {
                                    'type': 'group', 
                                    'statements': [
                                        {
                                            'type': 'operator', 'operator': '=', 
                                            'left': {'type': 'identifier', 'value': 'y', 'line': 1, 'column': 19}, 
                                            'right': {'type': 'number', 'value': '1', 'line': 1, 'column': 23}
                                        }, 
                                        {
                                            'type': 'operator', 'operator': '=', 
                                            'left': {'type': 'identifier', 'value': 'z', 'line': 1, 'column': 26}, 
                                            'right': {'type': 'number', 'value': '2', 'line': 1, 'column': 30}
                                        }, 
                                        {
                                            'type': 'operator', 'operator': '*', 
                                            'left': {'type': 'identifier', 'value': 'y', 'line': 1, 'column': 33}, 
                                            'right': {'type': 'identifier', 'value': 'z', 'line': 1, 'column': 37}
                                        }
                                    ]
                                }
                            }, 
                            {
                                'type': 'operator', 'operator': '+', 
                                'left': {'type': 'identifier', 'value': 'x', 'line': 1, 'column': 41}, 
                                'right': {'type': 'number', 'value': '5', 'line': 1, 'column': 45}
                            }
                        ]
                    }, 
                    'line': 1, 'column': 4
                }
            ], 
            'line': 1, 'column': 4
        }
    ]

    assert ast == expected_ast

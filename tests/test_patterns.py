import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from genia.patterns import bind_list_pattern


def test_bind_head_tail():
    pattern = {
        'type': 'list_pattern',
        'elements': [
            {'type': 'identifier', 'value': 'head'},
            {
                'type': 'unary_operator',
                'operator': '..',
                'operand': {'type': 'identifier', 'value': 'tail'}
            }
        ]
    }
    env = {}
    bind_list_pattern(pattern, [1, 2, 3], env)
    assert env == {'head': 1, 'tail': [2, 3]}


def test_bind_pre_mid_post():
    pattern = {
        'type': 'list_pattern',
        'elements': [
            {
                'type': 'unary_operator',
                'operator': '..',
                'operand': {'type': 'identifier', 'value': 'pre'}
            },
            {'type': 'identifier', 'value': 'mid'},
            {
                'type': 'unary_operator',
                'operator': '..',
                'operand': {'type': 'identifier', 'value': 'post'}
            }
        ]
    }
    env = {}
    bind_list_pattern(pattern, [1, 2, 3], env)
    assert env == {'pre': [], 'mid': 1, 'post': [2, 3]}

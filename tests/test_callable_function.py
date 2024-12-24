import pytest
import sys
from pathlib import Path

# Add the parent directory to the system path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from genia.callable_function import CallableFunction

class MockInterpreter:
    """A mock interpreter to simulate environment and evaluation for testing."""
    def __init__(self):
        self.environment = {}
        self.trace = False

    def evaluate(self, node):
        # Simplified evaluation logic for testing
        if node['type'] == 'identifier':
            return self.environment.get(node['value'])
        elif node['type'] == 'number':
            return int(node['value'])
        elif node['type'] == 'comparison':
            left = self.evaluate(node['left'])
            right = self.evaluate(node['right'])
            op = node['operator']
            return eval(f"{left} {op} {right}")  # Safe eval in controlled testing
        elif node['type'] == 'operator':
            left = self.evaluate(node['left'])
            right = self.evaluate(node['right'])
            op = node['operator']
            if op == '+':
                return left + right
            if op == '-':
                return left - right
            if op == '*':
                return left * right
            if op == '/':
                return left // right
        return None

def test_add_definition():
    func = CallableFunction("test_func")
    definition = {"parameters": [], "body": {"type": "number", "value": "42"}}
    func.add_definition(definition)

    assert len(func.definitions) == 1
    assert func.definitions[0] == definition

def test_call_simple_function():
    func = CallableFunction("test_func")
    definition = {"parameters": [], "guard": None, "body": {"type": "number", "value": "42"}}
    func.add_definition(definition)

    interpreter = MockInterpreter()
    result = func(interpreter, [], None)

    assert result == 42

def test_call_function_with_parameters():
    func = CallableFunction("test_func")
    definition = {
        "parameters": [{"type": "identifier", "value": "x"}],
        "body": {"type": "identifier", "value": "x"},
        "guard": None,
    }
    func.add_definition(definition)

    interpreter = MockInterpreter()
    result = func(interpreter, [99], None)

    assert result == 99

def test_call_function_with_guard():
    func = CallableFunction("test_func")
    definition = {
        "parameters": [{"type": "identifier", "value": "x"}],
        "guard": {
            "type": "comparison",
            "operator": ">",
            "left": {"type": "identifier", "value": "x"},
            "right": {"type": "number", "value": "10"},
        },
        "body": {"type": "identifier", "value": "x"},
    }
    func.add_definition(definition)

    interpreter = MockInterpreter()
    result = func(interpreter, [15], None)

    assert result == 15

    with pytest.raises(RuntimeError, match="No matching function"):
        func(interpreter, [5], None)

def test_call_with_multiple_definitions():
    func = CallableFunction("test_func")
    definition1 = {
        "parameters": [{"type": "number", "value": "0"}],
        "body": {"type": "number", "value": "1"},
    }
    definition2 = {
        "parameters": [{"type": "identifier", "value": "x"}],
        "body": {"type": "identifier", "value": "x"},
    }
    func.add_definition(definition1)
    func.add_definition(definition2)

    interpreter = MockInterpreter()

    result1 = func(interpreter, [0], None)
    result2 = func(interpreter, [99], None)

    assert result1 == 1
    assert result2 == 99

    with pytest.raises(RuntimeError, match="No matching function"):
        func(interpreter, ["non_matching", "too many"], None)

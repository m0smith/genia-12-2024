# genia/interpreter.py

from genia.lazy_seq import LazySeq
from collections import deque
from itertools import islice
from functools import reduce
import sys
import re
import copy
import threading

# from genia.callable_function import CallableFunction
# from genia.delay import Delay
import genia
from genia.lazy_seq import lazyseq
from genia.lexer import Lexer
from genia.parser import Parser
from genia.seq import delay_seq, Sequence, count_seq, nth_seq
from genia.hosted.os import files_in_paths
import importlib

def bind_list_pattern(pattern, arg, local_env):
    elements = pattern['elements']
    if len(elements) == 0:
        return
    for i, element in enumerate(elements):
        if element['type'] == 'unary_operator' and element['operator'] == "..":
            if isinstance(arg, list):
                local_env[element['operand']['value']] = arg[i:]
            elif isinstance(arg, LazySeq):
                local_env[element['operand']['value']] = list(islice(arg, i, None))
            elif isinstance(arg, Sequence):
                local_env[element['operand']['value']] = arg.rest()
            else:
                raise ValueError(f"Unsupported type for spread binding: {type(arg).__name__}")
        else:
            if isinstance(arg, list):
                if i < len(arg):
                    if element['type'] == 'wildcard':
                        pass
                    else:
                        local_env[element['value']] = arg[i]
                else:
                    raise RuntimeError(f"Not enough elements to bind parameter '{element['value']}'")
            elif isinstance(arg, LazySeq):
                try:
                    
                    if element['type'] == 'wildcard':
                        pass
                    else:
                        v = next(islice(arg, i, i + 1))
                        local_env[element['value']] = v
                except StopIteration:
                    raise RuntimeError(f"Not enough elements to bind parameter '{element['value']}'")
            elif isinstance(arg, Sequence):
                try:
                    
                    if element['type'] == 'wildcard':
                        pass
                    else:
                        local_env[element['value']] = nth_seq(i, arg)
                except StopIteration:
                    raise RuntimeError(f"Not enough elements to bind parameter '{element['value']}'")
            else:
                raise ValueError(f"Unsupported type for binding: {type(arg).__name__}")


class TailCall:
    """
    Represents a tail call to be optimized via TCO.
    """
    def __init__(self, func, args, node_context):
        self.func = func
        self.args = args
        self.node_context = node_context


class CallableFunction:
    def __init__(self, name, closure_context=None):
        self.name = name
        self.definitions = []
        self.closure_context = closure_context or {}  # Captured variables

    def add_definition(self, definition):
        if 'guard' not in definition:
            definition['guard'] = None
        self.definitions.append(definition)
        return self

    def matches(self, definition, args, interpreter):
        if len(definition['parameters']) != len(args):
            return False
        for param, arg in zip(definition['parameters'], args):
            if not self.match_parameter(param, arg):
                return False
        if definition['guard']:
            # Bind parameters and push a new environment
            bound_env = self.bind_parameters(definition, args)
            combined_env = {**self.closure_context, **bound_env}
            interpreter.push_env(combined_env)
            try:
                guard_result = interpreter.evaluate(definition['guard'])
                if not guard_result:
                    return False
            finally:
                interpreter.pop_env()
        return True
    
    
    
    def match_parameter(self, param, arg):
        match param.get('type'):
            case 'list_pattern':
                return self.match_list_pattern(param, arg)
            case 'constructor_pattern':
                return self.match_constructor_pattern(param, arg)
            case 'identifier':
                return True  # Identifiers always match
            case 'string':
                return param['value'] == arg
            case 'string_literal':
                return param['value'] == arg
            case 'number':
                return int(param['value']) == arg
            case 'number_literal':
                return int(param['value']) == arg
            case 'wildcard':
                return True  # Wildcards match any value
            case _:
                raise ValueError(f"Unsupported parameter type: {param['type']}")

    def match_list_pattern(self, pattern, arg):
        if not isinstance(arg, (list, LazySeq, Sequence)):
            return False
        if isinstance(arg, list):
            return self.match_list_pattern_list(pattern, arg)
        elif isinstance(arg, LazySeq):
            return self.match_list_pattern_lazy_seq(pattern, arg)
        elif isinstance(arg, Sequence):
            return self.match_list_pattern_sequence(pattern, arg)
        else:
            raise ValueError(f"Unsupported type: {type(arg).__name__}")

    def match_list_pattern_list(self, pattern, lst):
        elements = pattern['elements']
        if len(elements) == 0:  # Match an empty list
            return len(lst) == 0
        if len(elements) >= 2 and elements[-1]['type'] == 'unary_operator' and elements[-1]['operator'] == "..":
            # Match `[first, ..rest]`
            return len(lst) >= len(elements) - 1
        return len(lst) == len(elements)  # Exact length match

    def match_list_pattern_lazy_seq(self, pattern, lazy_seq):
        elements = pattern['elements']
        try:
            len_it = len(list(islice(lazy_seq, len(elements) + 1)))
        except TypeError:
            len_it = 0  # If not iterable
        if len(elements) >= 2 and elements[-1]['type'] == 'unary_operator' and elements[-1]['operator'] == "..":
            # Match `[first, ..rest]`
            return len_it >= len(elements) - 1
        return len_it == len(elements)  # Exact length match
    
    def match_list_pattern_sequence(self, pattern, sequence):
        elements = pattern['elements']
        try:
            len_it = count_seq(len(elements) + 1, sequence)
        except TypeError:
            len_it = 0  # If not iterable
        if len(elements) >= 2 and elements[-1]['type'] == 'unary_operator' and elements[-1]['operator'] == "..":
            # Match `[first, ..rest]`
            return len_it >= len(elements) - 1
        return len_it == len(elements)  # Exact length match

    def match_constructor_pattern(self, pattern, arg):
        if not isinstance(arg, dict):
            return False
        if arg.get('ctor') != pattern['name']:
            return False
        values = arg.get('values', [])
        if len(values) != len(pattern['parameters']):
            return False
        for subp, val in zip(pattern['parameters'], values):
            if not self.match_parameter(subp, val):
                return False
        return True

    def bind_constructor_pattern(self, pattern, arg, local_env):
        if not isinstance(arg, dict) or arg.get('ctor') != pattern['name']:
            raise RuntimeError(f"Constructor mismatch: expected {pattern['name']}")
        values = arg.get('values', [])
        if len(values) != len(pattern['parameters']):
            raise RuntimeError(f"{pattern['name']} expects {len(pattern['parameters'])} arguments")
        for subp, val in zip(pattern['parameters'], values):
            match subp.get('type'):
                case 'identifier':
                    local_env[subp['value']] = val
                case 'wildcard':
                    pass
                case 'list_pattern':
                    bind_list_pattern(subp, val, local_env)
                case 'constructor_pattern':
                    self.bind_constructor_pattern(subp, val, local_env)
                case 'string_literal':
                    if subp['value'] != val:
                        raise RuntimeError("Pattern mismatch")
                case 'number_literal':
                    if int(subp['value']) != val:
                        raise RuntimeError("Pattern mismatch")
                case _:
                    pass

    def bind_parameters(self, definition, args):
        local_env = {}
        for param, arg in zip(definition['parameters'], args):
            match param.get('type'):
                case 'list_pattern':
                    bind_list_pattern(param, arg, local_env)
                case 'constructor_pattern':
                    self.bind_constructor_pattern(param, arg, local_env)
                case 'identifier':
                    local_env[param['value']] = arg
                case 'wildcard':
                    pass  # Wildcards do not bind to any variable
                case 'string':
                    pass  # Strings are literals; no binding needed
                case 'number':
                    pass  # Numbers are literals; no binding needed
                case 'string_literal':
                    pass  # Strings are literals; no binding needed
                case 'number_literal':
                    pass  # Numbers are literals; no binding needed
                case _:
                    raise ValueError(f"Unsupported parameter type: {param['type']}")
        return local_env

    

    def __repr__(self):
        import json
        return f"CallableFunction('{self.name}', {self.definitions})"

    def __call__(self, interpreter, args, node_context):
        matching_function = None
        local_env = {}

        for definition in self.definitions:
            if self.matches(definition, args, interpreter):
                local_env = self.bind_parameters(definition, args)
                matching_function = definition
                break

        if not matching_function:
            raise RuntimeError(f"No matching function for '{self.name}' with arguments {args} at {node_context}")

        # Merge closure context with local environment
        combined_env = {**self.closure_context, **local_env}
        interpreter.push_env(combined_env)

        try:
            body = matching_function['body']
            if matching_function.get("foreign", False):
                # Foreign function: directly call the Python callable
                if callable(body):
                    result = body(*args)
                else:
                    module_name, func_name = body.rsplit('.', 1)
                    module = importlib.import_module(module_name)
                    body_fn = getattr(module, func_name)
                    if not callable(body_fn):
                        raise ValueError(f"Target '{body}' is not callable.")
                    result = body_fn(*args)
            else:
                # Native function: evaluate the AST body
                result = interpreter.evaluate(body)
            return result
        finally:
            interpreter.pop_env()

    def append(self, ast_node):
        """
        Append a new function definition to the CallableFunction.
        """
        if not isinstance(ast_node, dict) or 'parameters' not in ast_node or 'body' not in ast_node:
            raise ValueError("Invalid AST node: must contain 'parameters' and 'body'.")
        self.add_definition(ast_node)

   
class Delay:
    def __init__(self, expression):
        self.expression = expression
        self._value = None
        self._evaluated = False
        self._lock = threading.Lock()

    def value(self, interpreter=None):
        """
        Evaluates the delayed expression if it hasn't been evaluated yet.
        Returns the cached result on subsequent accesses.
        If an exception occurs, it is raised every time the value is accessed until a successful evaluation.
        """
        if not self._evaluated:
            with self._lock:
                if not self._evaluated:
                    try:
                        if isinstance(self.expression, dict):
                            # The expression is an AST node
                            self._value = interpreter.evaluate(self.expression)
                        elif callable(self.expression):
                            self._value = self.expression()
                        else:
                            self._value = self.expression
                        self._evaluated = True
                    except Exception as e:
                        self._evaluated = False
                        raise e
        return self._value

class Interpreter:
    def __init__(self):
        self.env_stack = [dict()]  # Stack of environments for variable scopes
        self.functions = {}         # Stores function definitions
        self.call_stack = deque()   # For TCO
        self.data_types = {}

        self.stdin = None
        self.stdout = None
        self.stderr = None

        self.add_hosted_functions()
        self.reset_awk_variables()

    @property
    def environment(self):
        return self.env_stack[-1]

    def push_env(self, new_env):
        self.env_stack.append(new_env)

    def pop_env(self):
        if len(self.env_stack) <= 1:
            raise RuntimeError("Cannot pop the global environment.")
        self.env_stack.pop()

    def evaluate_in_env(self, expr, env):
        self.push_env(env.copy())
        try:
            return self.evaluate(expr)
        finally:
            self.pop_env()

    def add_hosted_functions(self):
        # Register foreign functions with varying arities
        self.register_foreign_function("find_files", files_in_paths, parameters=["path"])
        self.register_foreign_function("delayseq", delay_seq, parameters=["head", "tail"])
        self.register_foreign_function("lazyseq", lazyseq, parameters=["seq"])
        for i in range(1, 8):
            params = [f"msg{j}" for j in range(1, i + 1)]
            self.register_foreign_function("print", self.write_to_stdout, parameters=params)
        self.register_foreign_function("printenv", lambda: self.write_to_stderr(str(self.environment)))
        self.register_foreign_function("printenv", lambda name: self.write_to_stderr(str(self.environment.get(name, f"{name} not found"))),
                                       parameters=["name"])
        self.register_foreign_function("trace", self.do_trace)

    def register_foreign_function(self, name, function, parameters=None, guard=None, line=0, column=0):
        """
        Register a foreign function using the same structure as native functions
        but with a 'foreign: True' flag.
        """
        if name in self.functions:
            func = self.functions[name]
        else:
            func = CallableFunction(name, closure_context=self.create_closure_context())
            self.functions[name] = func

        func.add_definition({
            "parameters": [{"type": "identifier", "value": param} for param in (parameters or [])],
            "guard": guard,
            "body": function,  # Directly store the callable function
            "line": line,
            "column": column,
            "foreign": True,  # Flag indicating this is a foreign function
        })

    def do_trace(self):
        genia.trace = True
        return genia.trace

    def write_to_stdout(self, *args):
        """
        Prints arguments to the provided stdout stream.
        """
        if self.stdout:
            print(*args, sep=self.environment.get('FS', ' '), file=self.stdout)
        else:
            print(*args, sep=self.environment.get('FS', ' '))

    def write_to_stderr(self, *args):
        """
        Prints arguments to the provided stderr stream.
        """
        if self.stderr:
            print(*args, file=self.stderr)
        else:
            print(*args, file=sys.stderr)

    def reset_awk_variables(self):
        """
        Resets AWK-specific variables to their initial state.
        """
        self.environment.update({
            "NR": 0,          # Record number
            "NF": 0,          # Number of fields
            "FS": " ",        # Field separator
            "$0": "",         # Entire record
            "$ARGS": [],      # Arguments passed to the script
        })

    def update_awk_variables(self, record, line_number, split_mode="whitespace"):
        """
        Updates AWK-specific variables based on the current record.
        """
        if split_mode == "csv":
            import csv
            fields = next(csv.reader([record]))
        elif split_mode == "whitespace":
            fields = record.split()
        else:
            raise ValueError(f"Unsupported split mode: {split_mode}")

        # Clear any extra field variables from previous records
        for i in range(len(fields) + 1, self.environment.get("NF", 0) + 1):
            self.environment.pop(f"${i}", None)

        self.environment["NR"] = line_number
        self.environment["$0"] = record
        self.environment["NF"] = len(fields)
        for i, field in enumerate(fields, start=1):
            self.environment[f"${i}"] = field
        self.environment["$NF"] = fields[-1] if fields else ""

    def execute(self, ast, args=None, awk_mode=None, stdin=None, stdout=None, stderr=None):
        """
        Executes the given AST.

        Parameters:
        - ast: The abstract syntax tree to execute.
        - args: Command-line arguments.
        - awk_mode: Whether to run in AWK mode.
        - stdin, stdout, stderr: File-like streams for I/O.
        """
        self.stdin = stdin or sys.stdin
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr

        result = None
        if awk_mode:
            result = self.execute_awk_mode(ast, stdin=self.stdin, split_mode=awk_mode)
        else:
            result = self.execute_regular_mode(ast, args=args)

        return result

    def execute_awk_mode(self, ast, stdin, split_mode="whitespace"):
        """
        Executes the AST in AWK mode, reading input from stdin and updating AWK variables.
        """
        self.reset_awk_variables()
        result = None
        line_number = 0  # Line counter for NR

        body = []
        for statement in ast:
            if statement['type'] == "function_definition":
                self.evaluate(statement)
            else:
                body.append(statement)

        begin_func = self.functions.get("begin")
        if begin_func:
            result = self.call_function(begin_func, [], node_context=(0, 0))

        for line in stdin:
            line_number += 1
            self.update_awk_variables(line.strip(), line_number, split_mode)
            if body:
                for statement in body:
                    result = self.evaluate(statement)
            else:
                body_func = self.functions.get("body")
                if body_func:
                    result = self.call_function(body_func, [], node_context=(0, 0))

        end_func = self.functions.get("end")
        if end_func:
            result = self.call_function(end_func, [], node_context=(0, 0))

        return result

    def execute_regular_mode(self, ast, args=None):
        """
        Executes the AST in regular mode, setting up arguments as special variables.
        """
        self.environment["$ARGS"] = args if args else []
        for i, field in enumerate(self.environment["$ARGS"], start=1):
            self.environment[f"${i}"] = field
        self.environment["NF"] = len(self.environment["$ARGS"])
        self.environment["$NF"] = self.environment.get(f"${self.environment['NF']}", None)
        self.environment["NR"] = 0  # Not applicable in regular mode but consistent with AWK.

        result = None
        for statement in ast:
            result = self.evaluate(statement)

        return result

    def evaluate(self, node):
        """
        Evaluate an AST node.
        """
        # Dispatch based on node type
        method_name = f"eval_{node['type']}"
        method = getattr(self, method_name, None)
        if not method:
            raise RuntimeError(f"Unsupported node type: {node['type']} at line {node.get('line')}, column {node.get('column')}")
        if genia.trace:
            self.write_to_stderr(f"TRACE: Applying {method_name} to {node}")
        return method(node)
    def eval_number_literal(self, node):
        """
        Evaluate a number literal pattern node.
        """
        return node['value']

    def eval_string_literal(self, node):
        """
        Evaluate a string literal pattern node.
        """
        return node['value']
    
    def eval_number(self, node):
        """
        Evaluate a number node.
        """
        return int(node['value'])

    def eval_string(self, node):
        """
        Evaluate a string node.
        """
        return node['value']

    def eval_raw_string(self, node):
        """
        Evaluate a raw string node. The value is returned as-is without interpreting escape sequences.
        """
        return node['value']

    def eval_identifier(self, node):
        """
        Evaluate an identifier node.
        """
        name = node['value']
        if name in self.environment:
            value = self.environment[name]
        elif name in self.functions:
            value = self.functions[name]
        else:
            raise RuntimeError(f"Undefined identifier '{name}' at line {node.get('line')}, column {node.get('column')}")
        # Handle Delay instances
        while isinstance(value, Delay):
            value = value.value(self)
        return value

    def eval_assignment(self, node):
        """
        Evaluate an assignment node.
        """
        pattern = node['pattern']
        pattern_type = pattern['type']
        value = self.evaluate(node['value'])
        if pattern_type == 'list_pattern':
            bind_list_pattern(pattern, value, self.environment)
        else:
            self.environment[pattern['value']] = value
        if genia.trace:
            self.write_to_stderr(f"TRACE: {pattern} = {value}")
        return value

    def eval_data_definition(self, node):
        type_name = node['name']
        constructors = {}

        for ctor in node['constructors']:
            ctor_name = ctor['name']
            param_count = len(ctor['parameters'])

            def make_ctor(n, c):
                def _ctor(*args):
                    if len(args) != c:
                        raise RuntimeError(f"{n} expects {c} arguments")
                    return {'type': type_name, 'ctor': n, 'values': list(args)}
                return _ctor

            constructors[ctor_name] = make_ctor(ctor_name, param_count)
            self.environment[ctor_name] = constructors[ctor_name]

        self.data_types[type_name] = constructors
        return None
    
    def eval_unary_operator(self, node):
        """
        Evaluate a unary operator node.
        Currently supports the '-' operator for negation.
        """
        operator = node['operator']
        operand = self.evaluate(node['operand'])
        if operator == '-':
            if isinstance(operand, int):
                return -operand
            else:
                print(type(operand))
                raise RuntimeError(f"Unary '-' operator can only be applied to integers at line {node.get('line')}, column {node.get('column')}")
        elif operator == '+':
            if isinstance(operand, int):
                return +operand
            else:
                raise RuntimeError(f"Unary '-' operator can only be applied to integers at line {node.get('line')}, column {node.get('column')}")
        elif operator == '..':
            if isinstance(operand, list):
                return operand
            else:
                raise RuntimeError(f"Unary '..' operator can only be applied to list at line {node.get('line')}, column {node.get('column')}")
        else:
            raise RuntimeError(f"Unsupported unary operator: {operator} at line {node.get('line')}, column {node.get('column')}")

    def eval_operator(self, node):
        """
        Evaluate an operator node.
        """
        op = node['operator']
        if op in ('+', '-', '*', '/', '..'):
            right = self.evaluate(node['right'])
            left = self.evaluate(node['left'])

            if op == '+':
                return left + right
            elif op == '-':
                return left - right
            elif op == '*':
                return left * right
            elif op == '/':
                return left // right  # Integer division
            elif op == '..':
                if isinstance(left, int) or isinstance(right, int):
                    if left <= right:
                        return list(range(left, right + 1))
                    else:
                        return list(range(left, right - 1, -1))
                if isinstance(left, (list, range)) and isinstance(right, (list, range)):
                    return list(left) + list(right)
                else:
                    raise RuntimeError(f"`..` operator can only be used between lists or ranges at line {node.get('line')}, column {node.get('column')}")
        elif op == '~':
            left = self.evaluate(node['left'])
            right = self.evaluate(node['right'])
            if not isinstance(left, str):
                raise RuntimeError(f"Left operand of '~' must be a string at line {node.get('line')}, column {node.get('column')}")
            if not isinstance(right, str):
                raise RuntimeError(f"Right operand of '~' must be a string (regex pattern) at line {node.get('line')}, column {node.get('column')}")
            
            result = re.match(right, left)
            return bool(result)
        elif op == '=':
            # Assignment is handled separately; '=' should not appear here
            raise RuntimeError("Unexpected '=' operator in eval_operator")
        else:
            raise RuntimeError(f"Unsupported operator: {op} at line {node.get('line')}, column {node.get('column')}")

    def eval_comparator(self, node):
        """
        Evaluate a comparison node.
        """
        left = self.evaluate(node["left"])
        right = self.evaluate(node["right"])
        operator = node["operator"]

        if operator == ">":
            rtnval = left > right
        elif operator == "<":
            rtnval = left < right
        elif operator == ">=":
            rtnval = left >= right
        elif operator == "<=":
            rtnval = left <= right
        elif operator == "==":
            rtnval = left == right
        elif operator == "!=":
            rtnval = left != right
        elif operator == "~":
            if not isinstance(left, str):
                raise RuntimeError(f"Left operand of '~' must be a string at line {node.get('line')}, column {node.get('column')}")
            if not isinstance(right, str):
                raise RuntimeError(f"Right operand of '~' must be a string (regex pattern) at line {node.get('line')}, column {node.get('column')}")
            rtnval = bool(re.match(right, left))
        else:
            raise RuntimeError(f"Unsupported comparison operator: {operator} at line {node.get('line')}, column {node.get('column')}")

        if genia.trace:
            self.write_to_stderr(f"TRACE: {left} {operator} {right} -> {rtnval}")
        return rtnval

    def eval_range(self, node):
        """
        Evaluate a range expression.
        """
        start = self.evaluate(node['start'])
        end = self.evaluate(node['end'])
        if not isinstance(start, int) or not isinstance(end, int):
            raise RuntimeError("Range boundaries must be integers")
        if start <= end:
            return list(range(start, end + 1))
        else:
            return list(range(start, end - 1, -1))

    def eval_list(self, node):
        """
        Evaluate a list expression.
        """
        rtnval = []
        for element in node["elements"]:
            el = self.evaluate(element)
            if element['type'] == 'unary_operator' and element['operator'] == '..':
                rtnval += el
            else:
                rtnval.append(el)
        return rtnval

    def eval_function_definition(self, node):
        """
        Store function definitions with support for multiple arities.
        """
        # Named functions
        if node.get("name"):
            name = node['name']
            func = self.functions.get(name, CallableFunction(name, closure_context=self.create_closure_context()))
            self.functions[name] = func
        else:
            # Anonymous functions (if needed)
            name = f"anon_{id(node)}"
            func = CallableFunction(name, closure_context=self.create_closure_context())
            self.functions[name] = func

        for definition in node['definitions']:
            func.add_definition(definition)

        if genia.trace:
            self.write_to_stderr(f"TRACE: Function '{name}' defined with definitions: {func.definitions}")
        return func

    def eval_function_call(self, node):
        """
        Evaluate a function call node.
        """
        name = node['name']
        if name in self.functions:
            func = self.functions[name]
        elif name in self.environment and callable(self.environment[name]):
            func = self.environment[name]
        else:
            raise RuntimeError(f"Undefined function: '{name}' at line {node.get('line')}, column {node.get('column')}")
        args = [self.evaluate(arg) for arg in node['arguments']]
        if node.get('is_tail_call', False):
            # Return a TailCall instance to enable TCO
            return TailCall(func=func, args=args, node_context=(node.get('line'), node.get('column')))
        else:
            # Normal function call
            return self.call_function(func, args, node_context=(node.get('line'), node.get('column')))

    def call_function(self, func, args, node_context):
        """
        Calls a function with the given arguments, implementing TCO.
        """
        while True:
            if isinstance(func, CallableFunction):
                result = func(self, args, node_context)
                if isinstance(result, TailCall):
                    func, args, node_context = result.func, result.args, result.node_context
                    continue  # Tail call: reuse the current frame
                else:
                    return result
            elif callable(func):
                # Foreign function
                return func(*args)
            else:
                raise RuntimeError(f"Cannot call non-function '{func}' at {node_context}")

    def eval_delay_expression(self, node):
        """
        Evaluate a delay expression (alias for eval_delay).
        """
        return self.eval_delay(node)

    def eval_delay(self, node):
        """
        Evaluate a delay expression node.
        """
        expression = node['expression']
        if isinstance(expression, dict):
            captured_env = self.environment.copy()
            return Delay(lambda: self.evaluate_in_env(expression, captured_env))
        else:
            return Delay(expression)

    def eval_grouped_statements(self, node):
        """
        Evaluate a grouped statement block, executing each statement in order.
        Return the result of the last statement.
        """
        result = None
        for statement in node["statements"]:
            result = self.evaluate(statement)
        return result

    def eval_expression_statement(self, node):
        """
        Evaluate an expression statement node.
        """
        return self.evaluate(node['expression'])

    def create_closure_context(self):
        """
        Create a closure context by copying the current environment, excluding special variables.
        """
        keys_to_exclude = {"NF", "NR", "$0", "$ARGS", "$NF"}
        return {k: v for k, v in self.environment.items() if k not in keys_to_exclude}


class GENIAInterpreter:
    def __init__(self):
        self.lexer = None
        self.parser = None
        self.interpreter = Interpreter()

    def run(self, code, args=None, awk_mode=None, stdin=None, stdout=None, stderr=None):
        """
        Execute the given code.

        Parameters:
        - code (str): The script to execute.
        - args (list): The command-line arguments.
        - awk_mode (str): The split mode ("whitespace" or "csv").
        - stdin (file-like): Input stream (default: sys.stdin).
        - stdout (file-like): Output stream (default: sys.stdout).
        - stderr (file-like): Error stream (default: sys.stderr).

        Returns:
        - The result of the last expression executed or the result of END in AWK mode.
        """
        self.lexer = Lexer(code)
        try:
            tokens = list(self.lexer.tokenize())
        except Lexer.SyntaxError as e:
            raise RuntimeError(str(e))
        # print(tokens)
        self.parser = Parser(tokens)
        try:
            ast = self.parser.parse()
        except Parser.SyntaxError as e:
            raise RuntimeError(str(e))
        return self.interpreter.execute(ast, args=args, awk_mode=awk_mode, stdin=stdin, stdout=stdout, stderr=stderr)


# Tail Call Optimization Support (Optional)
def trampoline(interpreter, ast):
    """
    Executes the AST using a trampoline to handle TCO.
    """
    result = interpreter.interpreter.execute(ast)
    while isinstance(result, TailCall):
        func, args, node_context = result.func, result.args, result.node_context
        result = interpreter.interpreter.call_function(func, args, node_context)
    return result


# Example Usage with TCO and Regex Support
def main():
    # Initialize the interpreter
    interpreter = GENIAInterpreter()

    # Example GENIA code with regex matching
    code = """
    fn foo(a) when a ~ r"[a-z]" -> 42 | (_) -> -1
    foo("aa")
    """
    # Execute the code
    try:
        result = interpreter.run(code)
        print(f"Result: {result}")  # Expected Output: Result: 42
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()



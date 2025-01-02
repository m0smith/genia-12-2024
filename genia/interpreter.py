
from functools import reduce
import sys
import re

from genia.callable_function import CallableFunction
from genia.lexer import Lexer
from genia.parser import Parser


class Interpreter:
    def __init__(self):
        self.environment = {}  # Stores variables and their values
        self.functions = {}    # Stores function definitions
        self.trace = False

        self.stdin = None
        self.stdout = None
        self.stderr = None
        
        self.add_hosted_functions()
        self.reset_awk_variables()

    def add_hosted_functions(self):
        
        self.register_foreign_function( "print", self.write_to_stdout)
        self.register_foreign_function( "print", self.write_to_stdout, parameters=["msg"])
        self.register_foreign_function( "print", self.write_to_stdout, parameters=["msg", "msg2"])
        self.register_foreign_function( "print", self.write_to_stdout, parameters=["msg", "msg2", "msg3"])
        self.register_foreign_function( "print", self.write_to_stdout, parameters=["msg", "msg2", "msg3", "msg4"])
        self.register_foreign_function( "print", self.write_to_stdout, parameters=["msg", "msg2", "msg3", "msg4", "msg5"])
        self.register_foreign_function( "printenv", lambda : self.write_to_stderr(self.environment))
        self.register_foreign_function( "printenv", lambda name: self.write_to_stderr(self.environment.get(name, self.functions.get(name, f"{name} not found"))), parameters=["name"])
        self.register_foreign_function( "trace", self.do_trace)
        

    def register_foreign_function(self, name, function, parameters=None, guard=None, line=0, column=0):
        """
        Register a foreign function using the same structure as native functions
        but with a 'foreign: True' flag.
        """
        if name in self.environment:
            raise ValueError(f"Function '{name}' is already defined.")
        
        # Register the function as a foreign function definition
        return self.eval_function_definition({
            "type": "function_definition",
            "name": name,
            "definitions": [
                {
                    "parameters": [{"type": "identifier", "value": param} for param in (parameters or [])],
                    "guard": guard,
                    "body": function,  # Directly store the callable function
                    "line": line,
                    "column": column,
                    "foreign": True,  # Flag indicating this is a foreign function
                }
            ],
            
        })

    def do_trace(self):
        self.trace = True
        return self.trace
    
    def write_to_stdout(self, *args):
        """
        Prints arguments to the provided stdout stream.
        """
        if self.stdout:
            print(*args, file=self.stdout)
        else:
            print(*args)
            
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
        self.environment.update(  # The block of code you provided is initializing and defining AWK-specific variables in the `Interpreter` class. Here's what each variable represents:
            {
                "NR": 0,  # Record number
                "NF": 0,  # Number of fields
                "$0": "",  # Entire record
                "$ARGS": [],  # Arguments passed to the script
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
        if self.trace:
            self.write_to_stderr(f"TRACE AWK: Split Mode: {split_mode} Record: {record}, Fields: {fields}, Line Number: {line_number}")
            
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
        # self.trace = True
        result = None
        line_number = 0  # Line counter for NR
        
        body = []
        for statement in ast:
            if self.trace:
                self.write_to_stderr(f"TRACE: AWK Statement {statement}")
            if(statement['type'] == "function_definition") :
                self.evaluate(statement)
            else:
                body.append(statement)

        begin_func = self.functions.get("begin")
        if begin_func:
            result = begin_func(self, [], node_context=(0,0))

        for line in stdin:
            line_number += 1
            self.update_awk_variables(line, line_number, split_mode)
            for statement in body:
                result = self.evaluate(statement)
                
        end_func = self.functions.get("end")
        if end_func:
            result = end_func(self, [], node_context=(0,0))

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
        return method(node)

    def eval_comparison(self, node):
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
        else:
            raise RuntimeError(f"Unsupported comparison operator: {operator} at line {node.get('line')}, column {node.get('column')}")
        if self.trace:
            self.write_to_stderr(f"TRACE: {left} {operator} {right} -> {rtnval}")
        return rtnval
    
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

    def eval_list_pattern(self, node):
        """
        Evaluate a list pattern. Handle `rest` nodes explicitly.
        """
        rtnval = []
        iterator = iter(node['elements'])
        for element in iterator:
            if element['type'] == 'rest':
                # Evaluate the next element dynamically for `rest`
                next_element = next(iterator, None)
                if not next_element:
                    raise RuntimeError("Expected an expression after `..` in list pattern.")
                rest_value = self.evaluate(next_element)
                if not isinstance(rest_value, list):
                    raise RuntimeError(f"Expected a list for `rest` but got {type(rest_value).__name__}")
                rtnval.extend(rest_value)  # Expand the `rest` elements
                if self.trace:
                    self.write_to_stderr(f"TRACE: LIST_PATTERN REST: {rest_value} -> {rtnval}")
            else:
                val = self.evaluate(element)
                rtnval.append(val)
                if self.trace:
                    self.write_to_stderr(f"TRACE: LIST_PATTERN: {val} -> {rtnval}")
        return rtnval
        # return [self.evaluate(element) for element in node['elements']]
    
    def eval_identifier(self, node):
        """
        Evaluate an identifier node.
        """
        name = node['value']
        if name not in self.environment and name not in self.functions:
            # raise RuntimeError(f"Undefined variable: {name} at line {node['line']}, column {node['column']}")
            self.environment[name] = 0
        return self.environment.get(name, self.functions.get(name))

    def eval_assignment(self, node):
        """
        Evaluate an assignment node.
        """
        name = node['identifier']
        value = self.evaluate(node['value'])
        self.environment[name] = value
        if self.trace:
            self.write_to_stderr(f"TRACE: {name} = {value}")
        return value

    def eval_group(self, node):
        """
        Evaluate a grouped statement block, executing each statement in order.
        Return the result of the last statement.
        """
        result = None
        for statement in node["statements"]:
            result = self.evaluate(statement)
        return result

    def eval_operator(self, node):
        """
        Evaluate an operator node.
        """
        op = node['operator']
        right = self.evaluate(node['right'])
        left_node = node['left']
        if op == '=':
            if left_node['type'] == 'list_pattern':
                self.handle_list_pattern_assignment(left_node, right)
                rtnval = right
            else:
                # Direct assignment
                self.environment[left_node['value']] = right
                rtnval = right
        else:        
            left = self.evaluate(left_node)
            
            if node['operator'] == '..':
                # Handle list concatenation
                if isinstance(left, (list, range)) and isinstance(right, (list, range)):
                    rtnval = list(left) + list(right)  # Convert ranges to lists if necessary
                else:
                    raise RuntimeError("`..` operator can only be used between lists or ranges")
            elif op == '+':
                rtnval =  int(left) + int(right)
            elif op == '-':
                rtnval =  left - right
            elif op == '*':
                rtnval =  left * right
            elif op == '/':
                rtnval =  left // right  # Integer division
            elif op == '~':
                rtnval = re.match(right, left)
            else:
                raise RuntimeError(f"Unsupported operator: {op} at line {node['line']}, column {node['column']}") 
        if self.trace:
            self.write_to_stderr(f"TRACE: OPERATOR {left} {op} {right} => {rtnval}")
        return rtnval
        
    
    def handle_list_pattern_assignment(self, pattern, value):
        """
        Handle destructuring assignment for list patterns.
        """
        if not isinstance(value, (list, range)):
            raise RuntimeError("Right-hand side of destructuring assignment must be a list or range.")
        value = list(value)  # Convert range to list if necessary

        elements = pattern['elements']
        if len(elements) > len(value):
            raise RuntimeError("Not enough elements in the value to match the pattern.")

        for i, element in enumerate(elements):
            if element['type'] == 'rest':
                self.environment[element['value']] = value[i:]
            else:
                self.environment[element['value']] = value[i]
                
    def eval_range(self, node):
        start = int(self.evaluate(node['start']))
        end = int(self.evaluate(node['end']))
        if start <= end:
            return list(range(start, end + 1))
        else:
            return list(range(start, end - 1, -1))
        
    def create_closure_context(self):
        keys_to_remove = ["NF", "NR", "$0", "$ARGS", "$NF"]
        closure_context = self.environment.copy()
        rtnval = {k: v for k, v in closure_context.items() if k not in keys_to_remove}
        return rtnval
    
    def eval_function_definition(self, node):
        """
        Store function definitions with support for multiple arities.
        """
        # Ensure foreign functions have valid callable bodies
        for definition in node.get("definitions", []):
            if definition.get("foreign", False) and not callable(definition["body"]):
                raise ValueError(f"Foreign function definition '{name}' must have callable bodies.")  

        # Named functions
        if ('name' in node and node['name']):
            name = node['name']
            func = self.functions[name] if name in self.functions else  CallableFunction(name, closure_context=self.create_closure_context())
            self.functions[name] = func
        else:
            # Anonymous functions
            name = f"anon_{id(node)}"
            func = CallableFunction(name=name, closure_context=self.create_closure_context())
        for definition in node['definitions']:
            func.add_definition(definition)
        if self.trace:
            self.write_to_stderr(f"TRACE: Function {name} defined")
        return func
    
    def eval_function_call(self, node):
        name = node['name']
                
        if name not in self.functions and name not in self.environment:
            raise RuntimeError(f"Undefined function: {name} at line {node['line']}, column {node['column']}")
        func = self.functions[name] if not (name in self.environment and callable(self.environment[name])) else self.environment[name]
        args = [self.evaluate(arg) for arg in node['arguments']]
        if self.trace:
            self.write_to_stderr(f"TRACE: Calling {name}")
        rtnval =  func(self, args, node_context=(node['line'], node['column']))
        if self.trace:
            self.write_to_stderr(f"TRACE: {name}({args}) => {rtnval}")
        return rtnval
    
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
        - awk_mode (bool): Whether to run in AWK mode.
        - stdin (file-like): Input stream (default: sys.stdin).
        - stdout (file-like): Output stream (default: sys.stdout).
        - stderr (file-like): Error stream (default: sys.stderr).

        Returns:
        - The result of the last expression executed or the result of END in AWK mode.
        """
        import sys
        stdin = stdin or sys.stdin
        stdout = stdout or sys.stdout
        stderr = stderr or sys.stderr

        self.lexer = Lexer(code)
        tokens = self.lexer.tokenize()
        # print("Tokens:", tokens, file=stderr)  # Debug output to stderr
        self.parser = Parser(tokens)
        ast = self.parser.parse()
        return self.interpreter.execute(ast, args=args, awk_mode=awk_mode, stdin=stdin, stdout=stdout, stderr=stderr)


from functools import reduce
import sys

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
        
        self.eval_function_definition( {
            "type": "function_definition",
            "name": "print",
            "definitions" :[
                {
                    "parameters": [],
                    "guard": None,
                    "body": self.write_to_stdout,
                    "line": 0,
                    "column": 0,
                },
                {
                    "parameters": [{"type": "identifier", "value": "a", "line":0,"column": 0}],
                    "guard": None,
                    "body": self.write_to_stdout,
                    "line": 0,
                    "column": 0,
                },
                {
                    "parameters": [
                                {"type": "identifier", "value": "a", "line":0,"column": 0},
                                {"type": "identifier", "value": "b", "line":0,"column": 0},
                                ],
                    "guard": None,
                    "body": self.write_to_stdout,
                    "line": 0,
                    "column": 0,
                }
                
            ]
        })
        
        self.eval_function_definition( {
            "type": "function_definition",
            "name": "printenv",
            "definitions": [
                {
                    "parameters": [],
                    "guard": None,
                    "body": lambda : self.write_to_stderr(self.environment),
                    "line": 0,
                    "column": 0,
                },
            ]
        })
        self.eval_function_definition( {
            "type": "function_definition",
            "name": "trace",
            "definitions": [
                {
                    "parameters": [],
                    "guard": None,
                    "body": self.do_trace,
                    "line": 0,
                    "column": 0,
                },
            ]
        })

    def do_trace(self):
        self.trace = True
    
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

    def update_awk_variables(self, record, line_number):
        """
        Updates AWK-specific variables based on the current record.
        """
        self.environment["NR"] = line_number
        self.environment["$0"] = record
        fields = record.split()  # Split record into fields by whitespace
        self.environment["NF"] = len(fields)
        for i, field in enumerate(fields, start=1):
            self.environment[f"${i}"] = field
            self.environment['$NF'] = field
        # Clear any extra field variables from previous records
        for i in range(len(fields) + 1, self.environment.get("NF", 0) + 1):
            self.environment.pop(f"${i}", None)

    def execute(self, ast, args=None, awk_mode=False, stdin=None, stdout=None, stderr=None):
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
            result = self.execute_awk_mode(ast, stdin=self.stdin)
        else:
            result = self.execute_regular_mode(ast, args=args)
            
        return result
    
    def execute_awk_mode(self, ast, stdin):
        """
        Executes the AST in AWK mode, reading input from stdin and updating AWK variables.
        """
        self.reset_awk_variables()
        result = None
        line_number = 0  # Line counter for NR

        for line in stdin:
            line_number += 1
            self.update_awk_variables(line, line_number)
            for statement in ast:
                result = self.evaluate(statement)

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

    def eval_identifier(self, node):
        """
        Evaluate an identifier node.
        """
        name = node['value']
        if name not in self.environment and name not in self.functions:
            raise RuntimeError(f"Undefined variable: {name} at line {node['line']}, column {node['column']}")
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

    def eval_operator(self, node):
        """
        Evaluate an operator node.
        """
        left = self.evaluate(node['left'])
        right = self.evaluate(node['right'])
        op = node['operator']
        if op == '+':
            rtnval =  left + right
        elif op == '-':
            rtnval =  left - right
        elif op == '*':
            rtnval =  left * right
        elif op == '/':
            rtnval =  left // right  # Integer division
        if self.trace:
            self.write_to_stderr(f"TRACE: {left} {op} {right} => {rtnval}")
        return rtnval
        raise RuntimeError(f"Unsupported operator: {op} at line {node['line']}, column {node['column']}")

    def eval_function_definition(self, node):
        """
        Store function definitions with support for multiple arities.
        """
        # Named functions
        if ('name' in node and node['name']):
            name = node['name']
            func = self.functions[name] if name in self.functions else  CallableFunction(name, closure_context=self.environment.copy())
            self.functions[name] = func
        else:
            # Anonymous functions
            name = f"anon_{id(node)}"
            func = CallableFunction(name=name, closure_context=self.environment.copy())
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
    
    # def eval_function_call_old(self, node):
    #     """
    #     Evaluate a function call with support for pattern matching, multiple arities, and guards.
    #     """
    #     name = node['name']
    #     if name not in self.functions:
    #         raise RuntimeError(f"Undefined function: {name} at line {node['line']}, column {node['column']}")

    #     # Evaluate arguments
    #     args = [self.evaluate(arg) for arg in node['arguments']]
    #     matching_function = None

    #     for func in self.functions[name]:
    #         # Check arity
    #         if len(func['parameters']) != len(args):
    #             continue

    #         # Check parameter patterns
    #         match = True
    #         local_env = self.environment.copy()
    #         for param, arg in zip(func['parameters'], args):
    #             if param['type'] == 'identifier':
    #                 local_env[param['value']] = arg  # Bind identifier
    #             elif param['type'] == 'number' and arg != int(param['value']):
    #                 match = False  # Pattern mismatch
    #                 break
    #             elif param['type'] == 'string' and arg != param['value']:
    #                 match = False  # Pattern mismatch
    #                 break
    #         if not match:
    #             continue

    #         # Check guard
    #         if func['guard']:
    #             self.environment = local_env
    #             try:
    #                 if not self.evaluate(func['guard']):
    #                     continue  # Guard condition failed
    #             finally:
    #                 self.environment = {
    #                     key: val for key, val in self.environment.items() if key not in local_env}

    #         # Found a matching function
    #         matching_function = func
    #         break

    #     if not matching_function:
    #         raise RuntimeError(f"No matching function for {name}({', '.join(
    #             map(str, args))}) at line {node['line']}, column {node['column']}")

    #     # Execute the function body
    #     self.environment = local_env
    #     try:
    #         result = None
    #         body = matching_function['body']
    #         if not isinstance(body, list):
    #             body = [body]  # Wrap single expression in a list
    #         for stmt in body:
    #             # Functions return the last evaluated expression
    #             result = self.evaluate(stmt)
    #         return result
    #     finally:
    #         # Restore environment
    #         self.environment = {
    #             key: val for key, val in self.environment.items() if key not in local_env}


class GENIAInterpreter:
    def __init__(self):
        self.lexer = None
        self.parser = None
        self.interpreter = Interpreter()

    def run(self, code, args=None, awk_mode=False, stdin=None, stdout=None, stderr=None):
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

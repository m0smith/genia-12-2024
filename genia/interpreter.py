
from functools import reduce

from genia.lexer import Lexer
from genia.parser import Parser

class Interpreter:
    def __init__(self):
        self.environment = {}  # Stores variables and their values
        self.functions = {}    # Stores function definitions
        self.reset_awk_variables()

    def reset_awk_variables(self):
        """
        Resets AWK-specific variables to their initial state.
        """
        self.environment.update({
            "NR": 0,  # Record number
            "NF": 0,  # Number of fields
            "$0": "",  # Entire record
            "$ARGS": [],  # Arguments passed to the script
        })
        
    def update_awk_variables(self, record):
        """
        Updates AWK-specific variables based on the current record.
        """
        self.environment["NR"] += 1
        self.environment["$0"] = record
        fields = record.split()  # Split record into fields by whitespace
        self.environment["NF"] = len(fields)
        for i, field in enumerate(fields, start=1):
            self.environment[f"${i}"] = field
        # Clear any extra field variables from previous records
        for i in range(len(fields) + 1, self.environment.get("NF", 0) + 1):
            self.environment.pop(f"${i}", None)
            
    def execute(self, ast, args=None, awk_mode=False):
        """
        Executes the given AST. Supports regular and AWK modes.
        """
        result = None
        self.environment["$ARGS"] = args if args else []

        if awk_mode:
            self.reset_awk_variables()
            # Simulate reading records from input (replace with actual file/stdin in production)
            for record in args:  # Assuming `args` contains lines of input
                self.update_awk_variables(record)
                for statement in ast:
                    result = self.evaluate(statement)
        else:
            # Regular mode execution
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
            return left > right
        elif operator == "<":
            return left < right
        elif operator == ">=":
            return left >= right
        elif operator == "<=":
            return left <= right
        elif operator == "==":
            return left == right
        elif operator == "!=":
            return left != right
        else:
            raise RuntimeError(f"Unsupported comparison operator: {operator} at line {node.get('line')}, column {node.get('column')}")

    def eval_number(self, node):
        """
        Evaluate a number node.
        """
        return int(node['value'])

    def eval_identifier(self, node):
        """
        Evaluate an identifier node.
        """
        name = node['value']
        if name not in self.environment:
            raise RuntimeError(f"Undefined variable: {name} at line {node['line']}, column {node['column']}")
        return self.environment[name]

    def eval_assignment(self, node):
        """
        Evaluate an assignment node.
        """
        name = node['identifier']
        value = self.evaluate(node['value'])
        self.environment[name] = value
        return value

    def eval_operator(self, node):
        """
        Evaluate an operator node.
        """
        left = self.evaluate(node['left'])
        right = self.evaluate(node['right'])
        op = node['operator']
        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            return left // right  # Integer division
        raise RuntimeError(f"Unsupported operator: {op} at line {node['line']}, column {node['column']}")

    def eval_function_definition(self, node):
        """
        Store function definitions with support for multiple arities.
        """
        name = node['name']
        if name not in self.functions:
            self.functions[name] = []
        self.functions[name].append(node)
        return None
    
    def eval_function_call(self, node):
        """
        Evaluate a function call with support for pattern matching, multiple arities, and guards.
        """
        name = node['name']
        if name not in self.functions:
            raise RuntimeError(f"Undefined function: {name} at line {node['line']}, column {node['column']}")

        # Evaluate arguments
        args = [self.evaluate(arg) for arg in node['arguments']]
        matching_function = None

        for func in self.functions[name]:
            # Check arity
            if len(func['parameters']) != len(args):
                continue

            # Check parameter patterns
            match = True
            local_env = self.environment.copy()
            for param, arg in zip(func['parameters'], args):
                if param['type'] == 'identifier':
                    local_env[param['value']] = arg  # Bind identifier
                elif param['type'] == 'number' and arg != int(param['value']):
                    match = False  # Pattern mismatch
                    break
                elif param['type'] == 'string' and arg != param['value']:
                    match = False  # Pattern mismatch
                    break
            if not match:
                continue

            # Check guard
            if func['guard']:
                self.environment = local_env
                try:
                    if not self.evaluate(func['guard']):
                        continue  # Guard condition failed
                finally:
                    self.environment = {key: val for key, val in self.environment.items() if key not in local_env}

            # Found a matching function
            matching_function = func
            break

        if not matching_function:
            raise RuntimeError(f"No matching function for {name}({', '.join(map(str, args))}) at line {node['line']}, column {node['column']}")

        # Execute the function body
        self.environment = local_env
        try:
            result = None
            body = matching_function['body']
            if not isinstance(body, list):
                body = [body]  # Wrap single expression in a list
            for stmt in body:
                result = self.evaluate(stmt)  # Functions return the last evaluated expression
            return result
        finally:
            # Restore environment
            self.environment = {key: val for key, val in self.environment.items() if key not in local_env}

class GENIAInterpreter:
    def __init__(self):
        self.lexer = None
        self.parser = None
        self.interpreter = Interpreter()

    def run(self, code, args=None, awk_mode=False):
        self.lexer = Lexer(code)
        tokens = self.lexer.tokenize()
        print("Tokens:", tokens)
        self.parser = Parser(tokens)
        ast = self.parser.parse()
        return self.interpreter.execute(ast, args=args, awk_mode=awk_mode)

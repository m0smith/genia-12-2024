import re
from collections import deque
from functools import reduce


class Lexer:
    TOKENS = [
        (r'//.*', 'COMMENT'),                         # Single-line comments
        # Single-line hash comments
        (r'#.*', 'COMMENT'),
        (r'/\*.*?\*/', 'BLOCK_COMMENT'),              # Block comments
        (r'\d+', 'NUMBER'),                           # Numbers
        # Special identifiers like $ARGS, $NF
        (r'\$[A-Z]+', 'SPECIAL_IDENTIFIER'),
        # General identifiers and keywords
        (r'[a-zA-Z_]\w*', 'IDENTIFIER'),
        (r'->', 'ARROW'),                             # Function arrow
        (r'when', 'WHEN'),                            # 'when' keyword
        (r'[<>]=?|==|!=', 'COMPARATOR'),              # Comparison operators
        (r'[+\-*/=]', 'OPERATOR'),                    # Arithmetic operators
        (r'[(){};,]', 'PUNCTUATION'),                 # Punctuation
        (r'\".*?\"|\'.*?\'', 'STRING'),               # Strings
        (r'\s+', None),                               # Skip whitespace
    ]

    def __init__(self, code):
        self.code = code
        self.line = 1
        self.column = 1

    def tokenize(self):
        tokens = []
        pos = 0
        while pos < len(self.code):
            match = None
            for pattern, token_type in self.TOKENS:
                regex = re.compile(pattern)
                match = regex.match(self.code, pos)
                if match:
                    match_text = match.group(0)
                    # Skip comments and whitespace
                    if token_type not in ('COMMENT', 'BLOCK_COMMENT', None):
                        tokens.append(
                            (token_type, match_text, self.line, self.column))
                    # Update line and column
                    newlines = match_text.count('\n')
                    if newlines > 0:
                        self.line += newlines
                        self.column = len(match_text.split('\n')[-1]) + 1
                    else:
                        self.column += len(match_text)
                    pos = match.end()
                    break
            if not match:
                raise SyntaxError(f"Unexpected character at line {self.line}, column {self.column}: '{self.code[pos]}'")
        return tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = deque(tokens)

    def parse(self):
        return self.program()

    def program(self):
        statements = []
        while self.tokens:
            statement = self.statement()
            if statement:
                statements.append(statement)
            # Consume a semicolon if present
            if self.tokens and self.tokens[0][1] == ';':
                self.tokens.popleft()
        return statements


    def statement(self):
        if not self.tokens:
            return None

        token_type, value, line, column = self.tokens[0]

        # Handle function definitions
        if token_type == 'IDENTIFIER' and value == 'fn':
            return self.function_definition()

        # Handle assignments or expressions
        if  token_type in {'IDENTIFIER', 'NUMBER', 'STRING', 'SPECIAL_IDENTIFIER'}:
            return self.expression()

        # Error for unknown statements
        context = ' '.join(token[1] for token in list(self.tokens)[:5])
        raise SyntaxError(f"Unknown statement at line {line}, column {column}: {value}. Context: {context}")


    def assignment_or_expression(self):
        token_type, value, line, column = self.tokens.popleft()

        if self.tokens and self.tokens[0][1] == '=':  # Assignment detected
            self.tokens.popleft()  # Remove '=' token
            expression = self.expression()
            return {'type': 'assignment', 'identifier': value, 'value': expression, 'line': line, 'column': column}

        elif self.tokens and self.tokens[0][1] == '(':  # Function call detected
            return self.function_call(value, line, column)

        else:
            raise SyntaxError(f"Unexpected token at line {line}, column {column}: {value}")

    def function_definition(self):
        token_type, fn_keyword, line, column = self.tokens.popleft()
        if fn_keyword != "fn":
            raise SyntaxError(f"Expected 'fn', found {fn_keyword} at line {line}, column {column}.")

        token_type, name, line, column = self.tokens.popleft()
        if token_type != "IDENTIFIER":
            raise SyntaxError(f"Expected function name, found {name} at line {line}, column {column}.")

        # Parse parameters
        if not self.tokens or self.tokens[0][1] != "(":
            raise SyntaxError(f"Expected '(' after function name at line {line}, column {column}.")
        self.tokens.popleft()  # Consume '('

        parameters = []
        while self.tokens and self.tokens[0][1] != ")":
            token_type, param, param_line, param_col = self.tokens.popleft()
            if token_type not in {"IDENTIFIER", "NUMBER", "STRING"} and param != ",":
                raise SyntaxError(f"Expected parameter name, pattern, or ',', found {param} at line {param_line}, column {param_col}.")
            if token_type != "PUNCTUATION":  # Add valid patterns
                parameters.append({"type": token_type.lower(), "value": param})
        if not self.tokens or self.tokens[0][1] != ")":
            raise SyntaxError(f"Unmatched '(' in function definition at line {line}, column {column}.")
        self.tokens.popleft()  # Consume ')'

        # Parse optional guard (when clause)
        guard = None
        if self.tokens and self.tokens[0][1] == "when":
            self.tokens.popleft()  # Consume 'when'
            guard = self.expression()  # Parse the guard expression fully

        # Parse return arrow and expression
        if not self.tokens or self.tokens[0][1] != "->":
            raise SyntaxError(f"Expected '->' in function definition at line {line}, column {column}.")
        self.tokens.popleft()  # Consume '->'
        body = self.expression()

        return {
            "type": "function_definition",
            "name": name,
            "parameters": parameters,
            "guard": guard,
            "body": body,
            "line": line,
            "column": column,
        }


    def function_call(self, function_name, line, column):
        self.tokens.popleft()  # Consume '('
        arguments = []
        while self.tokens and self.tokens[0][1] != ')':
            arguments.append(self.expression())
            if self.tokens and self.tokens[0][1] == ',':
                self.tokens.popleft()  # Consume ','
        if not self.tokens or self.tokens[0][1] != ')':
            raise SyntaxError(f"Unmatched parenthesis in function call at line {line}, column {column}")
        self.tokens.popleft()  # Consume ')'
        return {'type': 'function_call', 'name': function_name, 'arguments': arguments, 'line': line, 'column': column}

    def expression(self, precedence=0):
        left = self.primary_expression()
        # print(f"DEBUG: expression {self.tokens[0]}")
        while self.tokens and self.tokens[0][0] in {'OPERATOR', 'COMPARATOR'}:
            operator_token = self.tokens[0]
            operator_precedence = self.get_precedence(operator_token[1])
            print(f"DEBUG: expression operator_precedence={operator_precedence} precedence={precedence}")
            if operator_precedence <= precedence:
                break

            self.tokens.popleft()  # Consume operator
            right = self.expression(operator_precedence)
            left = {
                'type': 'operator' if operator_token[0] == 'OPERATOR' else 'comparison',
                'operator': operator_token[1],
                'left': left,
                'right': right
            }

        return left


    def primary_expression(self):
        """
        Parse primary expressions such as numbers, identifiers, strings, or parenthesized expressions.
        """
        if not self.tokens:
            raise SyntaxError("Unexpected end of input")

        token_type, value, line, column = self.tokens.popleft()

        if token_type == 'NUMBER':
            return {'type': 'number', 'value': value, 'line': line, 'column': column}

        if token_type == 'STRING':
            return {'type': 'string', 'value': value, 'line': line, 'column': column}

        if token_type == 'IDENTIFIER':
            # Check if this is a function call
            if self.tokens and self.tokens[0][1] == '(':
                self.tokens.popleft()  # Consume '('
                arguments = []

                # Parse arguments separated by commas
                while self.tokens and self.tokens[0][1] != ')':
                    arguments.append(self.expression())
                    if self.tokens and self.tokens[0][1] == ',':
                        self.tokens.popleft()  # Consume ','

                if not self.tokens or self.tokens[0][1] != ')':
                    raise SyntaxError(f"Unmatched '(' in function call at line {line}, column {column}.")
                self.tokens.popleft()  # Consume ')'

                return {
                    'type': 'function_call',
                    'name': value,
                    'arguments': arguments,
                    'line': line,
                    'column': column
                }

            # Otherwise, it's a plain identifier
            return {'type': 'identifier', 'value': value, 'line': line, 'column': column}

        if token_type == 'PUNCTUATION' and value == '(':
            expr = self.expression()
            if not self.tokens or self.tokens[0][1] != ')':
                raise SyntaxError(f"Unmatched '(' at line {line}, column {column}.")
            self.tokens.popleft()  # Consume ')'
            return expr

        raise SyntaxError(f"Unexpected token {value} at line {line}, column {column}")



    def get_precedence(self, operator):
        """
        Return the precedence of an operator. Higher values indicate higher precedence.
        """
        precedences = {
            '+': 3,
            '-': 3,
            '*': 4,
            '/': 4,
            '>': 2,
            '<': 2,
            '>=': 2,
            '<=': 2,
            '==': 2,
            '!=': 2
        }
        return precedences.get(operator, 1)  # Default precedence is 1




class Interpreter:
    def __init__(self):
        self.environment = {}  # Stores variables and their values
        self.functions = {}    # Stores function definitions

    def execute(self, ast, args=None, awk_mode=False):
        """
        Executes the given AST.
        """
        result = None
        for statement in ast:
            result = self.evaluate(statement)
            print(f"execute result={result}")
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

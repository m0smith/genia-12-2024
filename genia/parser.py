from collections import deque

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

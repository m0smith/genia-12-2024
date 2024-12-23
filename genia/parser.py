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
            if isinstance(statement, list):
                statements.extend(statement)
            elif statement:
                statements.append(statement)
            # Consume a semicolon if present
            if self.tokens and self.tokens[0][1] == ';':
                self.tokens.popleft()
        return statements


    def statement(self):
        if not self.tokens:
            return None

        token_type, value, line, column = self.tokens[0]

        # Handle named function definitions
        if token_type == 'IDENTIFIER' and value == 'fn':
            # Peek the next token to determine if it's a named or anonymous function
            next_token_type = self.peek_next_token_type()
            if next_token_type == 'IDENTIFIER':
                return self.named_function_definition()
            elif next_token_type == 'PUNCTUATION' and self.tokens[1][1] == '(':
                return self.anonymous_function_definition()

        # Handle assignments or expressions
        if token_type in {'IDENTIFIER', 'NUMBER', 'STRING', 'SPECIAL_IDENTIFIER'}:
            return self.assignment_or_expression()

        # Error for unknown statements
        context = ' '.join(token[1] for token in list(self.tokens)[:5])
        raise SyntaxError(f"Unknown statement at line {line}, column {column}: {value}. Context: {context}")



    def assignment_or_expression(self):
        token_type, identifier, line, column = self.tokens.popleft()

        if self.tokens and self.tokens[0][1] == '=':  # Assignment detected
            self.tokens.popleft()  # Remove '=' token'
            if self.tokens and self.tokens[0][1] == "fn":
                value = self.anonymous_function_definition()
            else:
                value = expression = self.expression()
            return {'type': 'assignment', 'identifier': identifier, 'value': value, 'line': line, 'column': column}

        elif self.tokens and self.tokens[0][1] == '(':  # Function call detected
            return self.function_call(identifier, line, column)

        else:
             # Reinsert the token and parse as an expression
            self.tokens.appendleft((token_type, identifier, line, column))
            return self.expression()

    def named_function_definition(self):
        token_type, fn_keyword, line, column = self.tokens.popleft()
        if fn_keyword != "fn":
            raise SyntaxError(f"Expected 'fn', found {fn_keyword} at line {line}, column {column}.")

        # Parse the function name
        token_type, name, line, column = self.tokens.popleft()
        if token_type != "IDENTIFIER":
            raise SyntaxError(f"Expected function name, found {name} at line {line}, column {column}.")

        # Reuse existing function parsing logic (e.g., parameters, guard, body)
        return self.function_definition_body(name, line, column)

    def anonymous_function_definition(self):
        token_type, fn_keyword, line, column = self.tokens.popleft()
        if fn_keyword != "fn":
            raise SyntaxError(f"Expected 'fn', found {fn_keyword} at line {line}, column {column}.")

        return self.function_definition_body(None, line, column)  # Pass `None` for the function name

    def function_definition_body(self, name, line, column):
        definitions = []
        while True:  # Parse each definition until no more `|`
            # Parse parameters
            if not self.tokens or self.tokens[0][1] != "(":
                raise SyntaxError(f"Expected '(' after 'fn' at line {line}, column {column}.")
            self.tokens.popleft()  # Consume '('

            parameters = []
            while self.tokens and self.tokens[0][1] != ")":
                token_type, param, param_line, param_col = self.tokens.popleft()
                if token_type not in {"IDENTIFIER", "NUMBER", "STRING"} and param != ",":
                    raise SyntaxError(f"Expected parameter name, pattern, or ',', found {param} at line {param_line}, column {param_col}.")
                if token_type != "PUNCTUATION":  # Add valid patterns
                    parameters.append({"type": token_type.lower(), "value": param, "line": param_line, "column": param_col})
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

            # Append the definition
            definitions.append({
                "parameters": parameters,
                "guard": guard,
                "body": body,
                "line": line,
                "column": column,
            })

            # Check for the `|` operator
            if not self.tokens or self.tokens[0][1] != "|":
                break
            self.tokens.popleft()  # Consume '|'

        # Return a function definition
        return {
            "type": "function_definition", # if name else "anonymous_function",
            "name": name,
            "definitions": definitions,
            "line": line,
            "column": column,
        }


    def function_definition_old(self):
        token_type, fn_keyword, line, column = self.tokens.popleft()
        if fn_keyword != "fn":
            raise SyntaxError(f"Expected 'fn', found {fn_keyword} at line {line}, column {column}.")

        token_type, name, line, column = self.tokens.popleft()
        if token_type != "IDENTIFIER":
            raise SyntaxError(f"Expected function name, found {name} at line {line}, column {column}.")

        definitions = []

        while True:
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

            # Add this definition
            definitions.append({
                "type": "function_definition",
                "name": name,
                "parameters": parameters,
                "guard": guard,
                "body": body,
                "line": line,
                "column": column,
            })

            # Check if there is a pipe for another definition
            if not self.tokens or self.tokens[0][1] != "|":
                break
            self.tokens.popleft()  # Consume '|'

        return definitions


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

    def peek_next_token_type(self):
        """
        Peek at the type of the next token without consuming it.
        Returns None if no tokens are left.
        """
        if self.tokens:
            return self.tokens[1][0]  # Return the type of the next token
        return None
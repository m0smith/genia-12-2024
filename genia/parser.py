# genia/parser.py

from collections import deque

class Parser:
    class SyntaxError(Exception):
        pass

    def __init__(self, tokens):
        self.tokens = deque(tokens)
        self.PRECEDENCE = {
            'OR': 1,
            'AND': 2,
            'NOT': 3,
            'EQUAL': 4,      # ==, !=
            'COMPARE': 5,    # <, >, <=, >=, ~
            'RANGE': 6,      # .. (assigned higher precedence)
            'ADD': 7,        # +, -
            'MULTIPLY': 8,   # *, /, %
            'UNARY': 9,
            'CALL': 10,
            'PRIMARY': 11
        }

    def parse(self):
        return self.program()

    def program(self):
        statements = []
        while self.tokens:
            statement = self.statement()
            statements.append(statement)
            # Consume optional semicolon
            if self.tokens and ((self.tokens[0][0] == 'SEMICOLON') or (self.tokens[0][0] == 'PUNCTUATION' and self.tokens[0][1] == ';')):
                self.tokens.popleft()
        return statements

    def statement(self):
        if not self.tokens:
            raise self.SyntaxError("Unexpected end of input")

        # Peek at the first token to decide the statement type
        token_type, value, line, column = self.tokens[0]

        if token_type == 'KEYWORD' and value == 'fn':
            return self.named_function_definition()
        elif token_type == 'IDENTIFIER':
            # Lookahead to check if it's an assignment
            if len(self.tokens) > 1 and self.tokens[1][0] == 'OPERATOR' and self.tokens[1][1] == '=':
                return self.assignment()
            else:
                return self.expression_statement()
        else:
            return self.expression_statement()

    def named_function_definition(self):
        if not self.tokens:
            raise self.SyntaxError("Unexpected end of input")

        # Consume 'fn'
        token_type, value, line, column = self.tokens.popleft()
        if token_type != 'KEYWORD' or value != 'fn':
            raise self.SyntaxError(f"Expected 'fn' keyword at line {line}, column {column}")

        # Consume function name
        if not self.tokens:
            raise self.SyntaxError("Unexpected end of input after 'fn'")
        token_type, func_name, line, column = self.tokens.popleft()
        if token_type != 'IDENTIFIER':
            raise self.SyntaxError(f"Expected function name after 'fn' at line {line}, column {column}")

        # Expect '(' for parameters
        if not self.tokens:
            raise self.SyntaxError("Unexpected end of input after function name")
        token_type, value, line, column = self.tokens.popleft()
        if token_type != 'PUNCTUATION' or value != '(':
            raise self.SyntaxError(f"Expected '(' after function name at line {line}, column {column}")

        # Parse parameters
        parameters = []
        while self.tokens:
            token_type, value, line, column = self.tokens[0]  # Peek without consuming
            if token_type == 'PUNCTUATION' and value == ')':
                self.tokens.popleft()  # Consume ')'
                break
            else:
                pattern = self.parse_pattern()
                parameters.append(pattern)
                # After a pattern, expect either ',' or ')'
                if self.tokens and self.tokens[0][0] == 'PUNCTUATION' and self.tokens[0][1] == ',':
                    self.tokens.popleft()  # Consume ','
                elif self.tokens and self.tokens[0][0] == 'PUNCTUATION' and self.tokens[0][1] == ')':
                    continue
                else:
                    raise self.SyntaxError(f"Expected ',' or ')' after parameter at line {line}, column {column}")

        # Check for 'when' guard
        guard = None
        if self.tokens and self.tokens[0][0] == 'KEYWORD' and self.tokens[0][1] == 'when':
            self.tokens.popleft()  # consume 'when'
            guard = self.expression()

        # Expect '->'
        if not self.tokens:
            raise self.SyntaxError("Unexpected end of input after function guard")
        token_type, value, line, column = self.tokens.popleft()
        if token_type != 'ARROW':
            raise self.SyntaxError(f"Expected '->' after function guard at line {line}, column {column}")

        # Parse body
        body = self.expression()

        definitions = [{
            'parameters': parameters,
            'guard': guard,
            'body': body.get('value') if body.get('type') == 'foreign' else body,
            'foreign': body.get('type') == 'foreign',
        }]

        # Handle multiple definitions separated by '|'
        while self.tokens:
            # Peek at the next token
            token_type, value, line, column = self.tokens[0]
            if token_type == 'PUNCTUATION' and value == '|':
                self.tokens.popleft()  # consume '|'

                # Expect '(' for parameters of the alternative definition
                if not self.tokens:
                    raise self.SyntaxError("Unexpected end of input after '|'")
                token_type, value, line, column = self.tokens.popleft()
                if token_type != 'PUNCTUATION' or value != '(':
                    raise self.SyntaxError(f"Expected '(' after '|' at line {line}, column {column}")

                # Parse parameters
                parameters = []
                while self.tokens:
                    token_type, value, line, column = self.tokens[0]  # Peek
                    if token_type == 'PUNCTUATION' and value == ')':
                        self.tokens.popleft()  # Consume ')'
                        break
                    else:
                        pattern = self.parse_pattern()
                        parameters.append(pattern)
                        # After a pattern, expect either ',' or ')'
                        if self.tokens and self.tokens[0][0] == 'PUNCTUATION' and self.tokens[0][1] == ',':
                            self.tokens.popleft()  # Consume ','
                        elif self.tokens and self.tokens[0][0] == 'PUNCTUATION' and self.tokens[0][1] == ')':
                            continue
                        else:
                            raise self.SyntaxError(f"Expected ',' or ')' after parameter at line {line}, column {column}")

                # Expect '->'
                if not self.tokens:
                    raise self.SyntaxError("Unexpected end of input after alternative parameters")
                token_type, value, line, column = self.tokens.popleft()
                if token_type != 'ARROW':
                    raise self.SyntaxError(f"Expected '->' after alternative parameters at line {line}, column {column}")

                # Parse body
                body = self.expression()

                definitions.append({
                    'parameters': parameters,
                    'guard': None,  # Guards are only allowed in the first definition
                    'body': body.get('value') if body.get('type') == 'foreign' else body,
                    'foreign': body.get('type') == 'foreign',
                })
            else:
                break

        return {
            'type': 'function_definition',
            'name': func_name,
            'definitions': definitions
        }
    def parse_pattern(self):
        """
        Parses a pattern in the parameter list.
        Currently handles list patterns.
        """
        token_type, value, line, column = self.tokens.popleft()
        if token_type == 'PUNCTUATION' and value == '[':
            # Start of a list pattern
            elements = []
            while self.tokens:
                token_type, value, line, column = self.tokens[0]  # Peek
                if token_type == 'PUNCTUATION' and value == ']':
                    self.tokens.popleft()  # Consume ']'
                    break
                elif token_type == 'PUNCTUATION' and value == ',':
                    self.tokens.popleft()  # Consume ','
                    continue
                elif token_type == 'IDENTIFIER' and value == '_':
                    # Wildcard
                    self.tokens.popleft()  # Consume '_'
                    elements.append({'type': 'wildcard'})
                elif token_type == 'DOT_DOT':
                    self.tokens.popleft()  # Consume '..'
                    # Expect an IDENTIFIER after '..'
                    if not self.tokens:
                        raise self.SyntaxError(f"Unexpected end of input after '..' in list pattern at line {line}, column {column}")
                    next_token_type, next_value, next_line, next_column = self.tokens.popleft()
                    if next_token_type != 'IDENTIFIER':
                        raise self.SyntaxError(f"Expected identifier after '..' in list pattern at line {next_line}, column {next_column}, but found {next_token_type} '{next_value}'")
                    elements.append({'type': 'spread', 'value': next_value})
                else:
                    # For simplicity, assume only wildcards and spread operators are allowed
                    raise self.SyntaxError(f"Unexpected token {token_type} {value} in list pattern at line {line}, column {column}")

            return {'type': 'list_pattern', 'elements': elements}
        elif token_type == 'IDENTIFIER':
            # Simple identifier pattern
            return {'type': 'identifier', 'value': value}
        else:
            raise self.SyntaxError(f"Unexpected token {token_type} {value} in parameter pattern at line {line}, column {column}")

    def assignment(self):
        if not self.tokens:
            raise self.SyntaxError("Unexpected end of input in assignment")

        token_type, var_name, line, column = self.tokens.popleft()

        if token_type != 'IDENTIFIER':
            raise self.SyntaxError(f"Expected identifier in assignment at line {line}, column {column}")

        # Expect '=' operator
        if not self.tokens:
            raise self.SyntaxError("Unexpected end of input after identifier in assignment")

        token_type, op, line, column = self.tokens.popleft()

        if token_type != 'OPERATOR' or op != '=':
            raise self.SyntaxError(f"Expected '=' in assignment at line {line}, column {column}")

        # Parse the expression on the right-hand side
        value = self.expression()

        return {
            'type': 'assignment',
            'identifier': var_name,
            'value': value,
            'line': line,
            'column': column
        }

    def expression_statement(self):
        expr = self.expression()
        return {
            'type': 'expression_statement',
            'expression': expr
        }

    def expression(self, precedence=0):
        """
        Pratt parser implementation for expressions.
        """
        if not self.tokens:
            raise self.SyntaxError("Unexpected end of input in expression")

        token_type, value, line, column = self.tokens.popleft()
        left = self.nud(token_type, value, line, column)

        while self.tokens:
            next_token_type, next_value, next_line, next_column = self.tokens[0]
            if next_token_type in {'OPERATOR', 'COMPARATOR', 'DOT_DOT'}:
                if next_token_type == 'DOT_DOT':
                    op_precedence = self.PRECEDENCE['RANGE']
                else:
                    op_precedence = self.PRECEDENCE.get(self.get_precedence_name(next_token_type, next_value), -1)
                if op_precedence < precedence:
                    break
                self.tokens.popleft()  # Consume operator
                left = self.led(next_token_type, next_value, left, op_precedence, next_line, next_column)
            else:
                op_precedence = -1
                
            if op_precedence < precedence:
                break

        return left

    def get_precedence_name(self, token_type, value):
        """
        Maps token to precedence category.
        """
        if token_type == 'OPERATOR':
            if value in ['+', '-']:
                return 'ADD'
            elif value in ['*', '/', '%']:
                return 'MULTIPLY'
            elif value == '~':
                return 'COMPARE'
            elif value == '=':
                return 'EQUAL'
            else:
                return 'UNKNOWN'
        elif token_type == 'COMPARATOR':
            if value in ['==', '!=']:
                return 'EQUAL'
            elif value in ['<', '>', '<=', '>=']:
                return 'COMPARE'
            else:
                return 'UNKNOWN'
        elif token_type == 'DOT_DOT':
            return 'RANGE'
        else:
            return 'UNKNOWN'

    def nud(self, token_type, value, line, column):
        """
        Null denotation for tokens that start expressions.
        """
        if token_type == 'NUMBER':
            return {'type': 'number', 'value': value, 'line': line, 'column': column}
        elif token_type in {'STRING', 'RAW_STRING'}:
            return {'type': token_type.lower(), 'value': value, 'line': line, 'column': column}
        elif token_type == 'IDENTIFIER':
            # Check if this is a function call
            if self.tokens and self.tokens[0][0] == 'PUNCTUATION' and self.tokens[0][1] == '(':
                self.tokens.popleft()  # Consume '('
                arguments = []
                # Parse arguments separated by commas
                while self.tokens and not (self.tokens[0][0] == 'PUNCTUATION' and self.tokens[0][1] == ')'):
                    arguments.append(self.expression())
                    if self.tokens and self.tokens[0][0] == 'PUNCTUATION' and self.tokens[0][1] == ',':
                        self.tokens.popleft()  # Consume ','
                if not self.tokens or not (self.tokens[0][0] == 'PUNCTUATION' and self.tokens[0][1] == ')'):
                    raise self.SyntaxError(f"Unmatched '(' in function call at line {line}, column {column}.")
                self.tokens.popleft()  # Consume ')'
                return {
                    'type': 'function_call',
                    'name': value,
                    'arguments': arguments,
                    'line': line,
                    'column': column
                }
            else:
                # Otherwise, it's a plain identifier
                return {'type': 'identifier', 'value': value, 'line': line, 'column': column}
        elif token_type == 'PUNCTUATION' and value == '[':
            # Start of a list expression
            elements = []
            while self.tokens:
                token_type, value, line, column = self.tokens[0]  # Peek
                if token_type == 'PUNCTUATION' and value == ']':
                    self.tokens.popleft()  # Consume ']'
                    break
                elif token_type == 'PUNCTUATION' and value == ',':
                    self.tokens.popleft()  # Consume ','
                    continue
                elif token_type == 'DOT_DOT':
                    self.tokens.popleft()  # Consume '..'
                    # Expect an IDENTIFIER after '..'
                    if not self.tokens:
                        raise self.SyntaxError(f"Unexpected end of input after '..' in list at line {line}, column {column}")
                    next_token_type, next_value, next_line, next_column = self.tokens.popleft()
                    if next_token_type != 'IDENTIFIER':
                        raise self.SyntaxError(f"Expected identifier after '..' in list at line {next_line}, column {next_column}, but found {next_token_type} '{next_value}'")
                    elements.append({'type': 'spread', 'value': next_value})
                elif token_type == 'NUMBER':
                    self.tokens.popleft()  # Consume number
                    elements.append({'type': 'number', 'value': value})
                elif token_type in {'STRING', 'RAW_STRING'}:
                    self.tokens.popleft()  # Consume string
                    elements.append({'type': token_type.lower(), 'value': value})
                else:
                    # Handle other expression types as needed
                    expr = self.expression()
                    elements.append(expr)
            return {'type': 'list', 'elements': elements}
        elif token_type == 'PUNCTUATION' and value == '(':
            # Parse grouped statements
            statements = []
            while self.tokens:
                token_type, value, line, column = self.tokens[0]
                if token_type == 'PUNCTUATION' and value == ')':
                    self.tokens.popleft()  # Consume ')'
                    break
                else:
                    # Parse a statement within the group
                    statement = self.group_statement()
                    statements.append(statement)
                    # After a statement, expect ';' or ')'
                    if self.tokens and self.tokens[0][0] == 'PUNCTUATION' and self.tokens[0][1] == ';':
                        self.tokens.popleft()  # Consume ';'
                    elif self.tokens and self.tokens[0][0] == 'PUNCTUATION' and self.tokens[0][1] == ')':
                        continue
                    else:
                        raise self.SyntaxError(f"Expected ';' or ')' after statement at line {line}, column {column}")
            else:
                raise self.SyntaxError(f"Unmatched '(' at line {line}, column {column}.")
            if len(statements) == 1:
                # If only one statement, return it directly
                return statements[0]
            else:
                # Multiple statements, wrap in grouped_statements
                return {'type': 'grouped_statements', 'statements': statements}
        elif token_type == 'KEYWORD' and value == 'fn':
            return self.anonymous_function_definition()
        elif token_type == 'KEYWORD' and value == 'delay':
            return self.delay_expression()
        elif token_type == 'KEYWORD' and value == 'foreign':
            return self.foreign_expression()
        else:
            raise self.SyntaxError(f"Unexpected token {token_type} {value} at line {line}, column {column}")

    def group_statement(self):
        """
        Parses a statement within a grouped context, such as inside ().
        Does not wrap expressions in 'expression_statement'.
        """
        if not self.tokens:
            raise self.SyntaxError("Unexpected end of input in grouped statements")
        
        token_type, value, line, column = self.tokens[0]
        
        if token_type == 'KEYWORD' and value == 'fn':
            return self.named_function_definition()
        elif token_type == 'IDENTIFIER':
            # Lookahead to check if it's an assignment
            if len(self.tokens) > 1 and self.tokens[1][0] == 'OPERATOR' and self.tokens[1][1] == '=':
                return self.assignment()
            else:
                expr = self.expression()
                return expr
        else:
            expr = self.expression()
            return expr

    def led(self, token_type, value, left, precedence, line, column):
        """
        Left denotation for tokens that appear in infix positions.
        """
        if token_type == 'OPERATOR' or token_type == 'COMPARATOR':
            right = self.expression(precedence)
            return {
                'type': 'operator',
                'operator': value,
                'left': left,
                'right': right,
                'line': line,
                'column': column
            }
        elif token_type == 'DOT_DOT':
            # Range operator handling
            right = self.expression(precedence)
            return {
                'type': 'range',
                'start': left,
                'end': right
            }
        else:
            raise self.SyntaxError(f"Unexpected operator {value} at line {line}, column {column}")

    def anonymous_function_definition(self):
        """
        Parse an anonymous function definition.
        """
        if not self.tokens:
            raise self.SyntaxError("Unexpected end of input after 'fn' keyword.")

        # Expect parameters in parentheses
        token_type, value, line, column = self.tokens.popleft()

        if token_type != 'PUNCTUATION' or value != '(':
            raise self.SyntaxError(f"Expected '(' after 'fn' at line {line}, column {column}")

        # Parse parameters
        parameters = []
        while self.tokens:
            token_type, value, line, column = self.tokens.popleft()
            if token_type == 'PUNCTUATION' and value == ')':
                break
            elif token_type == 'IDENTIFIER':
                parameters.append({'type': 'identifier', 'value': value})
            elif token_type == 'PUNCTUATION' and value == ',':
                continue
            else:
                raise self.SyntaxError(f"Unexpected token {token_type} {value} in parameter list at line {line}, column {column}")

        # Expect '->'
        if not self.tokens:
            raise self.SyntaxError("Unexpected end of input after anonymous function parameters.")

        token_type, value, line, column = self.tokens.popleft()

        if token_type != 'ARROW':
            raise self.SyntaxError(f"Expected '->' after anonymous function parameters at line {line}, column {column}")

        # Parse function body
        body = self.expression()

        return {
            'type': 'anonymous_function',
            'parameters': parameters,
            'body': body,
            'line': line,
            'column': column
        }

    def foreign_expression(self):
        """
        Parse a foreign function expression.
        """
        if not self.tokens:
            raise self.SyntaxError("Unexpected end of input after 'foreign'")
        token_type, value, line, column = self.tokens.popleft()
        if token_type != 'STRING':
            raise self.SyntaxError(f"Expected string after 'foreign' at line {line}, column {column}")
        return {'type': 'foreign', 'value': value}

    def delay_expression(self):
        """
        Parse a delay expression.
        Enforces that 'delay' is followed by '(' and parses the expression within.
        """
        # Expect '(' after 'delay'
        if not self.tokens or not (self.tokens[0][0] == 'PUNCTUATION' and self.tokens[0][1] == '('):
            raise self.SyntaxError(f"Expected '(' after 'delay' at current token location.")
        
        self.tokens.popleft()  # Consume '('
        
        # Parse the expression inside the parentheses
        expr = self.expression()
        
        # Expect ')' after the expression
        if not self.tokens or not (self.tokens[0][0] == 'PUNCTUATION' and self.tokens[0][1] == ')'):
            raise self.SyntaxError(f"Expected ')' after expression in 'delay' at line {expr.get('line', 'unknown')}, column {expr.get('column', 'unknown')}.")
        
        self.tokens.popleft()  # Consume ')'
        
        return {
            'type': 'delay',
            'expression': expr
        }

    def parse_list(self):
        """
        Parse a list expression.
        """
        elements = []
        while self.tokens:
            token_type, value, line, column = self.tokens[0]
            if token_type == 'PUNCTUATION' and value == ']':
                self.tokens.popleft()  # Consume ']'
                break
            elements.append(self.expression())
            if self.tokens and self.tokens[0][0] == 'PUNCTUATION' and self.tokens[0][1] == ',':
                self.tokens.popleft()  # Consume ','
        return {
            'type': 'list',
            'elements': elements,
            'line': line,
            'column': column
        }

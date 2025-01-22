# genia/lexer.py

import re
from collections import namedtuple

# Define a simple Token structure
Token = namedtuple('Token', ['type', 'value', 'line', 'column'])

class Lexer:
    # Define token specifications as regex patterns
    token_specification = [
        ('RAW_STRING', r'r"([^"\\]|\\.)*?"|r\'([^\'\\]|\\.)*?\''),  # Non-greedy matching
        ('STRING', r'"([^"\\]|\\.)*"|\'([^\'\\]|\\.)*\''),        # Regular strings
        ('COMMENT', r'//.*|#.*'),                               # Single line comments
        ('WHITESPACE', r'[ \t]+'),                              # Whitespace
        ('NEWLINE', r'\n'),                                     # Newlines
        ('ARROW', r'->'),                                       # Arrow operator
        # ('DOT_DOT', r'\.\.'),                                   # Double dot
        ('COMPARATOR', r'[<>!]=?|=='),                             # <, >, <=, >=, !=
        ('OPERATOR', r'\.\.|[+\-*/%=~]'),                            # +, -, *, /, %, =, ~
        ('PUNCTUATION', r'[()\[\]{},;|]'),                       # Punctuation
        ('NUMBER', r'\d+'),                                     # Integer numbers
        ('IDENTIFIER', r'\$?[\w*+\-/?]+'),                      # Identifiers with *, +, -, /, ?
        ('KEYWORD', r'\bfn\b|\bdelay\b|\bforeign\b|\bwhen\b'),  # Keywords
        ('MISMATCH', r'.'),                                      # Any other character
    ]

    # Compile the regex patterns into a master pattern
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    master_pat = re.compile(tok_regex)

    class SyntaxError(Exception):
        pass

    def __init__(self, code):
        self.code = code

    def tokenize(self):
        line_num = 1
        line_start = 0
        for mo in self.master_pat.finditer(self.code):
            kind = mo.lastgroup
            value = mo.group(kind)
            column = mo.start() - line_start + 1
            if kind == 'NEWLINE':
                line_start = mo.end()
                line_num += 1
                continue
            elif kind == 'WHITESPACE' or kind == 'COMMENT':
                continue
            elif kind == 'IDENTIFIER' and value in ['fn', 'delay', 'foreign', 'when']:
                kind = 'KEYWORD'
            elif kind == 'MISMATCH':
                raise self.SyntaxError(f"Unexpected character '{value}' at line {line_num}, column {column}")
            elif kind == 'RAW_STRING':
                # Remove 'r' and surrounding quotes
                value = value[2:-1]
            elif kind == 'STRING':
                # Remove surrounding quotes
                value = value[1:-1]
                # Handle escape sequences
                value = bytes(value, "utf-8").decode("unicode_escape")
            yield Token(kind, value, line_num, column)

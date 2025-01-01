import re

class Lexer:
    TOKENS = [
        (r'//.*', 'COMMENT'),                         # Single-line comments
        (r'#.*', 'COMMENT'),                          # Single-line hash comments
        (r'/\*.*?\*/', 'BLOCK_COMMENT'),              # Block comments

        (r'\.\.', 'DOT_DOT'),                         # `..` operator
        (r'-?\d+', 'NUMBER'),                           # Numbers
        (r'\b(?:fn|when|foreign)\b', 'KEYWORD'),      # Reserved keywords
        (r'[$a-zA-Z_?][\w*?]*', 'IDENTIFIER'),        # General identifiers and keywords
        (r'->', 'ARROW'),                             # Function arrow
        (r'when', 'WHEN'),                            # 'when' keyword
        (r'[<>]=?|==|!=', 'COMPARATOR'),              # Comparison operators
        (r'(?<![\w*?])([+\-*/=<>!])(?![\w*?])', 'OPERATOR'),  # Arithmetic operators
        # Punctuation tokens include:
        # - Parentheses `()` for grouping expressions or multi-statement function bodies
        # - Semicolon `;` for separating multiple statements within a block
        # - Curly braces `{}` for code blocks or scopes
        # - Square brackets `[]` for lists or indexing
        # - Comma `,` for separating function parameters or list elements
        (r'[(){};,[\]]', 'PUNCTUATION'),                 # Punctuation
        (r'\|', 'PIPE'),                              # Add token for the `|` operator
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
                regex = re.compile(pattern, re.UNICODE)
                match = regex.match(self.code, pos)
                if match:
                    match_text = match.group(0)
                    if token_type == 'STRING':
                        # Remove surrounding quotes from strings
                        match_text = match_text[1:-1]

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


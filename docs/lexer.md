# GENIA Lexer Specification (SPC)

## **Table of Contents**

1. [Overview](#1-overview)
2. [Lexical Grammar](#2-lexical-grammar)
   - [2.1. Token Types](#21-token-types)
     - [2.1.1. Keywords](#211-keywords)
     - [2.1.2. Identifiers](#212-identifiers)
     - [2.1.3. Literals](#213-literals)
       - [2.1.3.1. Numbers](#2131-numbers)
       - [2.1.3.2. Strings](#2132-strings)
         - [2.1.3.2.1. Regular Strings](#21321-regular-strings)
         - [2.1.3.2.2. Raw Strings](#21322-raw-strings)
     - [2.1.4. Operators](#214-operators)
     - [2.1.5. Punctuation](#215-punctuation)
     - [2.1.6. Comments](#216-comments)
     - [2.1.7. Whitespace](#217-whitespace)
     - [2.1.8. Special Tokens](#218-special-tokens)
   - [2.2. Token Patterns](#22-token-patterns)
3. [Lexing Rules](#3-lexing-rules)
   - [3.1. Token Matching Order](#31-token-matching-order)
   - [3.2. Handling Whitespace and Comments](#32-handling-whitespace-and-comments)
   - [3.3. Position Tracking](#33-position-tracking)
   - [3.4. Error Handling](#34-error-handling)
4. [Examples](#4-examples)
   - [4.1. Identifiers with Special Characters](#41-identifiers-with-special-characters)
   - [4.2. Raw and Regular Strings](#42-raw-and-regular-strings)
   - [4.3. Complex Expressions](#43-complex-expressions)
5. [Implementation Considerations](#5-implementation-considerations)
   - [5.1. Regular Expressions](#51-regular-expressions)
   - [5.2. Lexer Architecture](#52-lexer-architecture)
6. [Appendix](#6-appendix)
   - [6.1. Full Token List](#61-full-token-list)
   - [6.2. Regex Patterns](#62-regex-patterns)

---

## **1. Overview**

The GENIA Lexer is a lexical analyzer designed to tokenize source code written in the GENIA programming language. Its primary role is to convert a sequence of characters into a sequence of tokens, each representing meaningful syntactic elements such as keywords, identifiers, literals, operators, and punctuation.

This specification document (SPC) outlines the comprehensive details of the GENIA Lexer, including its token types, patterns, lexing rules, examples, and implementation considerations. Adhering to this specification ensures consistency, correctness, and maintainability of the lexer.

---

## **2. Lexical Grammar**

The lexical grammar defines the structure and patterns of tokens that the lexer recognizes. Each token type corresponds to a specific pattern, typically expressed using regular expressions.

### **2.1. Token Types**

GENIA Lexer categorizes its input into the following token types:

1. **Keywords**
2. **Identifiers**
3. **Literals**
   - Numbers
   - Strings
     - Regular Strings
     - Raw Strings
4. **Operators**
5. **Punctuation**
6. **Comments**
7. **Whitespace**
8. **Special Tokens**
   - Arrow (`->`)
   - Double Dot (`..`)
   - Pipe (`|`)

#### **2.1.1. Keywords**

**Definition:**

Reserved words that have special meaning in GENIA's syntax and cannot be used as identifiers.

**List of Keywords:**

- `define`
- `delay`
- `foreign`

**Pattern:**

Each keyword is recognized as a distinct token type (`KEYWORD`) to differentiate it from identifiers.

#### **2.1.2. Identifiers**

**Definition:**

Names given to variables, functions, or other user-defined entities in the code.

**Characteristics:**

- May start with an optional dollar sign (`$`).
- Can include letters (both uppercase and lowercase), digits, underscores (`_`), and special characters: `*`, `+`, `-`, `/`, `?`.
- Must not collide with reserved keywords.

**Examples:**

- `$var`
- `compute+/`
- `result-?`
- `xαβγ?`

**Pattern:**

```regex
\$?[\w*+\-/?]+
```

- `\$?` : Optional dollar sign at the beginning.
- `[\w*+\-/?]+` : One or more characters that are either word characters (`\w`), `*`, `+`, `-`, `/`, or `?`.

**Notes:**

- The inclusion of special characters allows for flexible and expressive naming conventions.
- Ensures that identifiers like `$var*` or `compute+/` are valid.

#### **2.1.3. Literals**

Literals represent fixed values in the code, such as numbers and strings.

##### **2.1.3.1. Numbers**

**Definition:**

Integer literals representing numerical values.

**Examples:**

- `123`
- `0`
- `456`
- `10`

**Pattern:**

```regex
\d+
```

- `\d+` : One or more digits.

##### **2.1.3.2. Strings**

Strings are sequences of characters enclosed in quotes. GENIA supports both regular and raw strings.

###### **2.1.3.2.1. Regular Strings**

**Definition:**

Strings that support escape sequences, allowing for special characters like newlines (`\n`), tabs (`\t`), etc.

**Syntax:**

- Enclosed in double quotes (`"..."`) or single quotes (`'...'`).

**Examples:**

- `"Hello, World!\n"`
- `'Regular\nString'`

**Pattern:**

```regex
"([^"\\]|\\.)*" | '([^'\\]|\\.)*'
```

- `"([^"\\]|\\.)*"` : Double-quoted strings allowing escaped characters.
- `'([^'\\]|\\.)*'` : Single-quoted strings allowing escaped characters.

**Notes:**

- Escape sequences like `\n`, `\t`, `\"`, `\'`, etc., are processed and converted to their respective representations.

###### **2.1.3.2.2. Raw Strings**

**Definition:**

Strings that treat backslashes (`\`) as literal characters, preserving them without interpreting as escape sequences.

**Syntax:**

- Prefixed with `r` or `R`, followed by single (`'...'`) or double (`"..."`) quotes.

**Examples:**

- `r"[A-Z]+\n"`
- `R'[a-z]+\\t'`

**Pattern:**

```regex
r"([^"\\]|\\.)*?" | r'([^\'\\]|\\.)*?'
```

- `r"([^"\\]|\\.)*?"` : Raw double-quoted strings with non-greedy matching.
- `r'([^\'\\]|\\.)*?'` : Raw single-quoted strings with non-greedy matching.

**Notes:**

- Non-greedy quantifiers (`*?`) ensure that the lexer correctly identifies the closing quote without over-consuming characters.
- The `r` or `R` prefix distinguishes raw strings from regular strings.
- In raw strings, sequences like `\n` are treated as literal backslash and 'n', not as a newline character.

#### **2.1.4. Operators**

**Definition:**

Symbols that represent operations such as arithmetic, assignment, and logical operations.

**List of Operators:**

- Arithmetic and Assignment: `+`, `-`, `*`, `/`, `%`, `=`
- Comparison: `<`, `>`, `<=`, `>=`, `!=`

**Pattern:**

```regex
[+\-*/%=] | [<>!]=?
```

- `[+\-*/%=]` : Single-character operators.
- `[<>!]=?` : Comparison operators, allowing for one or two characters (`<`, `>`, `<=`, `>=`, `!=`).

**Notes:**

- The order in which these patterns are defined can affect tokenization precedence.
- Ensure that multi-character operators (`<=`, `>=`, `!=`) are recognized before their single-character counterparts to prevent partial matches.

#### **2.1.5. Punctuation**

**Definition:**

Symbols that structure the code, such as parentheses, brackets, commas, and semicolons.

**List of Punctuation Symbols:**

- Parentheses: `(`, `)`
- Brackets: `[`, `]`
- Braces: `{`, `}`
- Others: `,`, `;`

**Pattern:**

```regex
[()\[\]{},;]
```

- Each symbol is matched as a distinct `PUNCTUATION` token.

#### **2.1.6. Comments**

**Definition:**

Annotations in the code that are ignored by the lexer and compiler, used for documentation or explanation.

**Types of Comments:**

- **Single-Line Comments:**
  - Start with `//` or `#` and continue until the end of the line.

**Examples:**

- `// This is a comment`
- `# Another comment`

**Pattern:**

```regex
//.* | #.*
```

- `//.*` : Matches `//` followed by any characters until the end of the line.
- `#.*` : Matches `#` followed by any characters until the end of the line.

**Notes:**

- Comments are skipped by the lexer and do not produce tokens.
- Ensure that comment patterns are checked before more general patterns to prevent accidental tokenization of comment content.

#### **2.1.7. Whitespace**

**Definition:**

Non-printable characters that separate tokens but do not carry semantic meaning.

**Types:**

- Spaces (` `)
- Tabs (`\t`)

**Pattern:**

```regex
[ \t]+
```

- Matches one or more spaces or tabs.

**Notes:**

- Whitespace is skipped by the lexer and does not produce tokens.
- It is essential for separating tokens but is otherwise ignored.

#### **2.1.8. Special Tokens**

**Definition:**

Tokens that represent specific multi-character symbols or operators.

**List of Special Tokens:**

- **Arrow (`->`):**
  - Represents an arrow operator, often used in function definitions or mappings.

- **Double Dot (`..`):**
  - Represents a range operator or spread syntax.

- **Pipe (`|`):**
  - Represents a pipe operator, commonly used in chaining functions or transformations.

**Patterns:**

- **Arrow (`->`):**

  ```regex
  ->
  ```

- **Double Dot (`..`):**

  ```regex
  \.\.
  ```

- **Pipe (`|`):**

  ```regex
  \|
  ```

**Notes:**

- These patterns are matched as distinct token types (`ARROW`, `DOT_DOT`, `PIPE`).
- Ensure that multi-character tokens are prioritized over single-character tokens to prevent partial matches.

### **2.2. Token Patterns**

Below is a summary of all token patterns used by the GENIA Lexer:

| Token Type               | Pattern                                                                                           | Description                                               |
|--------------------------|---------------------------------------------------------------------------------------------------|-----------------------------------------------------------|
| **RAW_STRING**           | `r"([^"\\]|\\.)*?" | r'([^\'\\]|\\.)*?'`                                                           | Raw strings with `r` prefix and non-greedy matching       |
| **STRING**               | `"([^"\\]|\\.)*" | '([^\'\\]|\\.)*'`                                                                   | Regular strings with escape sequence processing           |
| **COMMENT**              | `//.* | #.*`                                                                                       | Single-line comments                                     |
| **WHITESPACE**           | `[ \t]+`                                                                                           | Spaces and tabs                                          |
| **NEWLINE**              | `\n`                                                                                                | Line breaks                                               |
| **ARROW**                | `->`                                                                                                | Arrow operator                                           |
| **DOT_DOT**              | `\.\.`                                                                                              | Double dot operator                                      |
| **PIPE**                 | `\|`                                                                                                 | Pipe operator                                            |
| **COMPARATOR**           | `[<>!]=?`                                                                                           | Comparison operators (`<`, `>`, `<=`, `>=`, `!=`)       |
| **OPERATOR**             | `[+\-*/%=]`                                                                                         | Arithmetic and assignment operators                      |
| **PUNCTUATION**          | `[()\[\]{},;]`                                                                                      | Parentheses, brackets, braces, commas, semicolons         |
| **NUMBER**               | `\d+`                                                                                                | Integer numbers                                          |
| **IDENTIFIER**           | `\$?[\w*+\-/?]+`                                                                                     | Identifiers with optional `$` and special characters      |
| **KEYWORD**              | `\bdefine\b|\bdelay\b|\bforeign\b`                                                                       | Reserved keywords                                        |
| **MISMATCH**             | `.`                                                                                                  | Any other character; triggers a syntax error             |

---

## **3. Lexing Rules**

Lexing rules govern how the lexer processes input and assigns tokens based on the defined patterns.

### **3.1. Token Matching Order**

The order in which token patterns are defined is crucial, as it determines precedence during tokenization. The GENIA Lexer follows these general rules:

1. **Longest Match First:**
   - The lexer attempts to match the longest possible string for a token before considering shorter matches.
   
2. **Specificity:**
   - More specific patterns (e.g., multi-character operators like `->`, `..`) are placed before more general ones (e.g., single-character operators like `-`).

3. **Priority:**
   - Patterns are ordered from highest to lowest priority based on their specificity and potential overlaps.

**Example Order:**

1. **Special Tokens:**
   - `ARROW`, `DOT_DOT`, `PIPE`
   
2. **Keywords:**
   - `KEYWORD`
   
3. **Identifiers:**
   - `IDENTIFIER`
   
4. **Operators:**
   - `COMPARATOR`, `OPERATOR`
   
5. **Literals:**
   - `RAW_STRING`, `STRING`, `NUMBER`
   
6. **Punctuation:**
   - `PUNCTUATION`
   
7. **Comments and Whitespace:**
   - `COMMENT`, `WHITESPACE`
   
8. **Error Handling:**
   - `MISMATCH`

### **3.2. Handling Whitespace and Comments**

- **Whitespace (`WHITESPACE`):**
  - Consists of spaces and tabs.
  - Skipped by the lexer and does not produce tokens.
  
- **Comments (`COMMENT`):**
  - Single-line comments starting with `//` or `#`.
  - Skipped by the lexer and do not produce tokens.

**Rationale:**

- Whitespace and comments are non-essential for the syntactic structure and are ignored to streamline the tokenization process.

### **3.3. Position Tracking**

Accurate tracking of line and column numbers is vital for:

- **Error Reporting:**
  - Providing meaningful feedback when syntax errors occur.
  
- **Debugging:**
  - Assisting developers in locating issues within the source code.

**Mechanism:**

1. **Initialization:**
   - `line_num` starts at `1`.
   - `line_start` tracks the character index where the current line begins.
   
2. **Processing Tokens:**
   - For each matched token:
     - `line_num` and `column` are calculated based on the match's start position.
   
3. **Handling Newlines:**
   - When a `NEWLINE` token is encountered:
     - Increment `line_num`.
     - Update `line_start` to the position after the newline.
   
4. **Column Calculation:**
   - `column = mo.start() - line_start + 1`
   
**Example:**

Given the code:

```genia
define add(a, b) ->
  a + b;
```

- **First Line (`define add(a, b) ->`):**
  - `define` at line `1`, column `1`.
  - `add` at line `1`, column `4`.
  
- **Second Line (`  a + b;`):**
  - `a` at line `2`, column `3`.
  - `+` at line `2`, column `5`.
  - `b` at line `2`, column `7`.

### **3.4. Error Handling**

Proper error handling ensures that the lexer can gracefully handle unexpected or invalid input.

**Mechanism:**

1. **Mismatch Detection:**
   - Any character or sequence that does not match any defined token patterns is considered a `MISMATCH`.
   
2. **Syntax Error:**
   - Upon encountering a `MISMATCH`, the lexer raises a `SyntaxError`, providing the unexpected character along with its line and column number.

**Example:**

Given the code:

```genia
define invalid @
```

- The lexer recognizes `define` and `invalid` as valid tokens.
- The `@` character does not match any token patterns, resulting in a `SyntaxError`:

```
SyntaxError: Unexpected character '@' at line 1, column 12
```

**Rationale:**

- Immediate error reporting helps developers identify and correct syntax issues promptly.

---

## **4. Examples**

This section provides illustrative examples demonstrating how the GENIA Lexer tokenizes various code snippets.

### **4.1. Identifiers with Special Characters**

**Code:**

```genia
$var* = 123;
compute+/ = $var* + 456;
result-? = compute+/ / 2;
```

**Tokenization:**

| Token Type   | Value              | Line | Column |
|--------------|--------------------|------|--------|
| IDENTIFIER   | `$var*`            | 1    | 1      |
| OPERATOR     | `=`                | 1    | 7      |
| NUMBER       | `123`              | 1    | 9      |
| PUNCTUATION  | `;`                | 1    | 12     |
| IDENTIFIER   | `compute+/`        | 2    | 1      |
| OPERATOR     | `=`                | 2    | 11     |
| IDENTIFIER   | `$var*`            | 2    | 13     |
| OPERATOR     | `+`                | 2    | 19     |
| NUMBER       | `456`              | 2    | 21     |
| PUNCTUATION  | `;`                | 2    | 24     |
| IDENTIFIER   | `result-?`         | 3    | 1      |
| OPERATOR     | `=`                | 3    | 10     |
| IDENTIFIER   | `compute+/`        | 3    | 12     |
| OPERATOR     | `/`                | 3    | 22     |
| NUMBER       | `2`                | 3    | 24     |
| PUNCTUATION  | `;`                | 3    | 25     |

**Explanation:**

- Identifiers like `$var*`, `compute+/`, and `result-?` include special characters (`*`, `+`, `/`, `-`, `?`) and are correctly tokenized as `IDENTIFIER` tokens.

### **4.2. Raw and Regular Strings**

**Code:**

```genia
r"[A-Z]+\n" "regular\nstring"
```

**Tokenization:**

| Token Type  | Value          | Line | Column |
|-------------|----------------|------|--------|
| RAW_STRING  | `[A-Z]+\n`     | 1    | 1      |
| STRING      | `regular\nstring` | 1    | 13     |

**Explanation:**

- **Raw String (`r"[A-Z]+\n"`):**
  - Preserves the backslash and `n` as literal characters.
  - Tokenized as `RAW_STRING` with value `[A-Z]+\n`.

- **Regular String (`"regular\nstring"`):**
  - Processes the escape sequence `\n` as an actual newline character.
  - Tokenized as `STRING` with value `regular\nstring`.

### **4.3. Complex Expressions**

**Code:**

```genia
define foo() -> 0 | (_) -> 1
```

**Tokenization:**

| Token Type     | Value   | Line | Column |
|----------------|---------|------|--------|
| KEYWORD        | `define`    | 1    | 1      |
| IDENTIFIER     | `foo`   | 1    | 4      |
| PUNCTUATION    | `(`     | 1    | 7      |
| PUNCTUATION    | `)`     | 1    | 8      |
| ARROW          | `->`    | 1    | 10     |
| NUMBER         | `0`     | 1    | 13     |
| PIPE           | `|`     | 1    | 15     |
| PUNCTUATION    | `(`     | 1    | 17     |
| IDENTIFIER     | `_`     | 1    | 18     |
| PUNCTUATION    | `)`     | 1    | 19     |
| ARROW          | `->`    | 1    | 21     |
| NUMBER         | `1`     | 1    | 24     |
| PUNCTUATION    | `;`     | 1    | 25     |

**Explanation:**

- **Function Definition (`define foo() -> 0`):**
  - `define` is a keyword.
  - `foo` is an identifier.
  - `()` denotes an empty parameter list.
  - `->` represents the arrow operator.
  - `0` is a number.

- **Pipe Operator and Anonymous Function (`| (_) -> 1`):**
  - `|` is a pipe operator.
  - `(_)` represents an anonymous function with `_` as its parameter.
  - `->` represents the arrow operator.
  - `1` is a number.

---

## **5. Implementation Considerations**

Implementing the GENIA Lexer effectively requires careful attention to regular expressions, token matching order, and performance optimization.

### **5.1. Regular Expressions**

**Usage:**

- The lexer utilizes Python's `re` module with named groups to define and match token patterns.

**Master Pattern:**

The master regular expression pattern combines all token patterns using the `|` (OR) operator and named groups.

**Example:**

```python
tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
master_pat = re.compile(tok_regex)
```

**Optimization Tips:**

1. **Order Matters:**
   - Place more specific patterns before general ones to ensure correct token matching.
   
2. **Non-Greedy Matching:**
   - Use non-greedy quantifiers (`*?`) for patterns like `RAW_STRING` to prevent over-consuming characters.
   
3. **Escaping Special Characters:**
   - Ensure that special regex characters within patterns are properly escaped to avoid unintended matches.

4. **Unicode Support:**
   - Utilize Python 3's Unicode capabilities (`\w` includes Unicode word characters) to handle identifiers with non-ASCII characters.

### **5.2. Lexer Architecture**

**Components:**

1. **Token Specification:**
   - A list of tuples defining token types and their corresponding regex patterns.

2. **Master Pattern:**
   - A compiled regex that combines all token patterns for efficient matching.

3. **Lexer Class:**
   - Encapsulates the tokenization process, including pattern matching, token generation, and error handling.

**Example Structure:**

```python
import re
from collections import namedtuple

# Define a simple Token structure
Token = namedtuple('Token', ['type', 'value', 'line', 'column'])

class Lexer:
    token_specification = [
        # (Token Type, Pattern)
        ('RAW_STRING', r'r"([^"\\]|\\.)*?"|r\'([^\'\\]|\\.)*?\''),
        # ... other tokens ...
        ('MISMATCH', r'.'),
    ]
    
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
            elif kind in ('WHITESPACE', 'COMMENT'):
                continue
            elif kind == 'IDENTIFIER' and value in ['define', 'delay', 'foreign']:
                kind = 'KEYWORD'
            elif kind == 'MISMATCH':
                raise self.SyntaxError(f"Unexpected character '{value}' at line {line_num}, column {column}")
            elif kind == 'RAW_STRING':
                value = value[2:-1]  # Remove 'r' and surrounding quotes
            elif kind == 'STRING':
                value = value[1:-1]  # Remove surrounding quotes
                value = bytes(value, "utf-8").decode("unicode_escape")  # Handle escape sequences
            yield Token(kind, value, line_num, column)
```

**Key Points:**

- **Named Groups:** Facilitate easy identification of token types during pattern matching.
- **Efficient Iteration:** Using `finditer` allows for efficient, sequential processing of the input string.
- **Error Handling:** Immediate syntax error reporting for unrecognized characters ensures robustness.

### **5.3. Performance Optimization**

- **Precompilation of Patterns:**
  - Compile regex patterns once during lexer initialization to improve performance during tokenization.

- **Avoiding Backtracking:**
  - Design regex patterns to minimize backtracking, which can degrade performance, especially with complex input.

- **Streaming Input:**
  - For large files, consider processing the input in chunks or streams to manage memory usage effectively.

- **Caching:**
  - Implement caching mechanisms for frequently matched patterns to expedite the tokenization process.

---

## **6. Appendix**

### **6.1. Full Token List**

Below is the comprehensive list of tokens recognized by the GENIA Lexer, along with their patterns and descriptions.

| Token Type     | Pattern                                                                                           | Description                                               |
|----------------|---------------------------------------------------------------------------------------------------|-----------------------------------------------------------|
| **RAW_STRING** | `r"([^"\\]|\\.)*?" \| r'([^\'\\]|\\.)*?'`                                                      | Raw strings with `r` prefix and non-greedy matching       |
| **STRING**     | `"([^"\\]|\\.)*" \| '([^\'\\]|\\.)*'`                                                            | Regular strings with escape sequence processing           |
| **COMMENT**    | `//.* \| #.*`                                                                                      | Single-line comments                                     |
| **WHITESPACE** | `[ \t]+`                                                                                           | Spaces and tabs                                          |
| **NEWLINE**    | `\n`                                                                                                | Line breaks                                               |
| **ARROW**      | `->`                                                                                                | Arrow operator                                           |
| **DOT_DOT**    | `\.\.`                                                                                              | Double dot operator                                      |
| **PIPE**       | `\|`                                                                                                 | Pipe operator                                            |
| **COMPARATOR** | `[<>!]=?`                                                                                           | Comparison operators (`<`, `>`, `<=`, `>=`, `!=`)       |
| **OPERATOR**   | `[+\-*/%=]`                                                                                         | Arithmetic and assignment operators                      |
| **PUNCTUATION**| `[()\[\]{},;]`                                                                                      | Parentheses, brackets, braces, commas, semicolons         |
| **NUMBER**     | `\d+`                                                                                                | Integer numbers                                          |
| **IDENTIFIER** | `\$?[\w*+\-/?]+`                                                                                     | Identifiers with optional `$` and special characters      |
| **KEYWORD**    | `\bdefine\b|\bdelay\b|\bforeign\b`                                                                       | Reserved keywords                                        |
| **MISMATCH**   | `.`                                                                                                  | Any other character; triggers a syntax error             |

### **6.2. Regex Patterns**

Detailed explanations of each regex pattern used in the token specification.

#### **6.2.1. RAW_STRING**

```regex
r"([^"\\]|\\.)*?" | r'([^\'\\]|\\.)*?'
```

- **Explanation:**
  - **Double-Quoted Raw Strings:**  
    - `r"` : Starts with `r` and double quote.
    - `([^"\\]|\\.)*?` : Non-greedy match of any character except `"` or `\`, or an escaped character.
    - `"` : Ends with double quote.
    
  - **Single-Quoted Raw Strings:**  
    - `r'` : Starts with `r` and single quote.
    - `([^\'\\]|\\.)*?` : Non-greedy match of any character except `'` or `\`, or an escaped character.
    - `'` : Ends with single quote.

#### **6.2.2. STRING**

```regex
"([^"\\]|\\.)*" | '([^\'\\]|\\.)*'
```

- **Explanation:**
  - **Double-Quoted Strings:**  
    - `"` : Starts with double quote.
    - `([^"\\]|\\.)*` : Greedy match of any character except `"` or `\`, or an escaped character.
    - `"` : Ends with double quote.
    
  - **Single-Quoted Strings:**  
    - `'` : Starts with single quote.
    - `([^\'\\]|\\.)*` : Greedy match of any character except `'` or `\`, or an escaped character.
    - `'` : Ends with single quote.

#### **6.2.3. COMMENT**

```regex
//.* | #.*
```

- **Explanation:**
  - `//.*` : Matches `//` followed by any characters until the end of the line.
  - `#.*` : Matches `#` followed by any characters until the end of the line.

#### **6.2.4. WHITESPACE**

```regex
[ \t]+
```

- **Explanation:**
  - Matches one or more spaces or tabs.

#### **6.2.5. NEWLINE**

```regex
\n
```

- **Explanation:**
  - Matches a newline character.

#### **6.2.6. ARROW**

```regex
->
```

- **Explanation:**
  - Matches the sequence `->`.

#### **6.2.7. DOT_DOT**

```regex
\.\.
```

- **Explanation:**
  - Matches the sequence `..`.

#### **6.2.8. PIPE**

```regex
\|
```

- **Explanation:**
  - Matches the pipe character `|`.

#### **6.2.9. COMPARATOR**

```regex
[<>!]=?
```

- **Explanation:**
  - Matches comparison operators:
    - `<` or `<=`
    - `>` or `>=`
    - `!` or `!=`

#### **6.2.10. OPERATOR**

```regex
[+\-*/%=]
```

- **Explanation:**
  - Matches arithmetic and assignment operators: `+`, `-`, `*`, `/`, `%`, `=`.

#### **6.2.11. PUNCTUATION**

```regex
[()\[\]{},;]
```

- **Explanation:**
  - Matches punctuation symbols: `(`, `)`, `[`, `]`, `{`, `}`, `,`, `;`.

#### **6.2.12. NUMBER**

```regex
\d+
```

- **Explanation:**
  - Matches one or more digits.

#### **6.2.13. IDENTIFIER**

```regex
\$?[\w*+\-/?]+
```

- **Explanation:**
  - `\$?` : Optional dollar sign at the beginning.
  - `[\w*+\-/?]+` : One or more word characters (`\w`), `*`, `+`, `-`, `/`, or `?`.

#### **6.2.14. KEYWORD**

```regex
\bdefine\b|\bdelay\b|\bforeign\b
```

- **Explanation:**
  - Matches exact words `define`, `delay`, or `foreign` using word boundaries (`\b`).

#### **6.2.15. MISMATCH**

```regex
.
```

- **Explanation:**
  - Matches any single character not matched by previous patterns, triggering a syntax error.

---

## **7. Conclusion**

The GENIA Lexer Specification provides a detailed blueprint for tokenizing GENIA source code. By adhering to this specification, developers can ensure that the lexer accurately and efficiently processes code, correctly identifies all token types, and maintains robust error handling.

**Key Takeaways:**

- **Comprehensive Token Definitions:**  
  Each token type is meticulously defined with clear patterns and descriptions, ensuring precise tokenization.

- **Structured Lexing Rules:**  
  The order of token matching, handling of whitespace and comments, and position tracking are all systematically addressed to maintain lexer reliability.

- **Extensive Examples:**  
  Practical examples illustrate how various code snippets are tokenized, aiding in understanding and validation.

- **Implementation Guidance:**  
  Insights into regular expression usage, lexer architecture, and performance optimization provide a solid foundation for effective lexer implementation.

**Next Steps:**

1. **Implement the Lexer:**
   - Utilize the provided specifications to develop or refine the GENIA Lexer in your chosen programming language.

2. **Develop Comprehensive Test Suites:**
   - Expand unit tests to cover additional scenarios, ensuring that all aspects of the lexer function as intended.

3. **Integrate Continuous Integration (CI):**
   - Set up automated testing pipelines to maintain code quality and detect regressions early.

4. **Document and Maintain:**
   - Keep the specification updated alongside lexer enhancements, facilitating future development and onboarding processes.

By following this specification, the GENIA Lexer will serve as a robust foundation for further language development, enabling seamless parsing and compilation of GENIA programs.

### Specification for Lists and List Destructuring in Genia

This document specifies the syntax, behavior, and functionality of lists and list destructuring in the Genia language.

---

### **Lists**

#### Definition
- A list is an ordered collection of values, enclosed in square brackets `[]`.
- Lists can contain:
  - Constants: `[1, 2, 3]`
  - Variables: `[a, b, c]`
  - Expressions: `[x + 1, y * 2, z - 3]`
  - Nested Lists: `[[1, 2], [3, 4], [5, 6]]`

#### Examples:
```genia
nums = [1, 2, 3]
mixed = [1, "two", 3.0, true]
nested = [[1, 2], [3, 4]]
```

---

### **Syntax**

#### List Declaration
Lists are declared using square brackets `[]`:
```genia
list = [1, 2, 3]
```

#### Accessing Elements
Access list elements using zero-based indexing:
```genia
first = list[0]
last = list[-1]  // Negative indices count from the end
```

---

### **Operations**

1. **Concatenation**:
   - Combine two lists using the `..` operator.
   ```genia
   list1 = [1, 2, 3]
   list2 = [4, 5, 6]
   combined = list1..list2  // [1, 2, 3, 4, 5, 6]
   ```

2. **Length**:
   - Retrieve the length of a list using `.length`.
   ```genia
   length = list.length  // 3
   ```

3. **Membership**:
   - Check if an element exists in a list using `in`.
   ```genia
   exists = 2 in list  // true
   ```

4. **Slicing**:
   - Extract sublists using slicing.
   ```genia
   sublist = list[1:3]  // [2, 3]
   ```

---

### **List Destructuring**

#### Definition
List destructuring allows unpacking elements of a list into variables.

#### Syntax
```genia
[first, second, ..rest] = list
```

#### Examples:
1. **Basic Destructuring**:
   ```genia
   list = [1, 2, 3, 4]
   [a, b, ..rest] = list
   // a = 1, b = 2, rest = [3, 4]
   ```

2. **Nested Destructuring**:
   ```genia
   nested_list = [[1, 2], [3, 4], [5, 6]]
   [[x, y], ..rest] = nested_list
   // x = 1, y = 2, rest = [[3, 4], [5, 6]]
   ```

3. **Partial Destructuring**:
   ```genia
   list = [1, 2, 3]
   [a, ..] = list
   // a = 1
   ```

4. **Empty Lists**:
   ```genia
   [] = []  // Valid
   [x, ..rest] = []  // Error: Not enough elements
   ```

---

### **Lexer Rules**

1. **List Delimiters**:
   - `[`: Start of a list.
   - `]`: End of a list.

2. **Rest Operator (`..`)**:
   - Regular Expression: `\.\.`
   - Token: `DOT_DOT`

#### Example Tokenization:
For the code:
```genia
[a, ..rest] = list
```

Tokens:
```plaintext
PUNCTUATION: '['
IDENTIFIER: 'a'
PUNCTUATION: ','
DOT_DOT: '..'
IDENTIFIER: 'rest'
PUNCTUATION: ']'
OPERATOR: '='
IDENTIFIER: 'list'
```

---

### **Parser Rules**

#### List Declaration
```plaintext
list : '[' (expression (',' expression)*)? ']'
```

#### Destructuring Pattern
```plaintext
list_pattern : '[' (identifier (',' identifier)* (',' '..' identifier)?)? ']'
```

#### Example AST for `[a, ..rest] = list`:
```json
{
  "type": "operator",
  "operator": "=",
  "left": {
    "type": "list_pattern",
    "elements": [
      {"type": "identifier", "value": "a"},
      {"type": "rest", "value": "rest"}
    ]
  },
  "right": {
    "type": "identifier",
    "value": "list"
  }
}
```

---

### **Interpreter Behavior**

#### Evaluating Lists
- Convert lists into Python lists.

#### Destructuring Assignment
1. Bind elements to variables based on the pattern.
2. Handle `..rest` by binding the remaining elements to the variable.

#### Example Evaluation
```genia
list = [1, 2, 3, 4]
[a, b, ..rest] = list
```
Environment after evaluation:
```json
{
  "a": 1,
  "b": 2,
  "rest": [3, 4]
}
```

---

### **Error Handling**

1. **Mismatched Length**:
   - If the list has fewer elements than required by the pattern:
     ```genia
     [a, b, c] = [1, 2]
     // Error: Not enough elements in the list for destructuring
     ```

2. **Invalid Rest Assignment**:
   - Ensure `..rest` is followed by a valid identifier:
     ```genia
     [a, ..] = list  // Error: Expected identifier after `..`
     ```

---

### **Advanced Features (Future Enhancements)**

1. **Pattern Matching in Function Parameters**:
   ```genia
   define sum([first, ..rest]) -> first + sum(rest) | [] -> 0
   ```

2. **Destructuring with Defaults**:
   ```genia
   [a = 1, b = 2, ..rest] = [10]
   // a = 10, b = 2, rest = []
   ```

---

This specification defines how lists and list destructuring work in Genia, enabling powerful and expressive data manipulation. Let me know if you’d like to implement any part of this!

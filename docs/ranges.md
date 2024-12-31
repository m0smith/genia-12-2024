### Specification for Ranges in Genia

This specification outlines how ranges are parsed, evaluated, and used in the Genia language.

---

### **Definition**

A range represents a sequence of numbers defined by a start and an end value. It is denoted by the syntax:

```
start..end
```

#### Examples:
- `1..10` generates a range from `1` to `10` (inclusive).
- `10..1` generates a descending range from `10` to `1` (inclusive).

---

### **Components**

1. **Start and End Values**:
   - The `start` and `end` values of a range can be:
     - **Constants**: Literal numbers, including negative numbers.
       - Example: `-5..5`
     - **Variables**: Identifiers holding numeric values.
       - Example:
         ```
         x = 1
         y = 5
         x..y
         ```
     - **Expressions**: Any valid expression that evaluates to a numeric value.
       - Example: `(1 + 2)..(10 - 3)`

2. **Inclusivity**:
   - Ranges in Genia are inclusive at both ends. For example, `1..3` represents `[1, 2, 3]`.

---

### **Syntax**

#### Range Declaration:
```genia
start..end
```

#### Example Usage:
```genia
x = 1
y = 5
range = x..y  // Generates [1, 2, 3, 4, 5]
```

---

### **Lexer Rules**

To accept ranges with constants or variables:
- A **range operator** `..` should be a distinct token.
- **Negative numbers** should be treated as part of the `NUMBER` token.

#### Updated Lexer Rules:
1. **Negative Numbers**:
   - Regular Expression: `-?\d+`
   - Token: `NUMBER`

2. **Range Operator**:
   - Regular Expression: `\.\.`
   - Token: `DOT_DOT`

#### Example Tokenization:
For the code:
```genia
x = -5
range = x..10
```

Tokens:
```plaintext
IDENTIFIER: "x"
OPERATOR: "="
NUMBER: "-5"
IDENTIFIER: "range"
OPERATOR: "="
IDENTIFIER: "x"
DOT_DOT: ".."
NUMBER: "10"
```

---

### **Parser Rules**

The parser should recognize ranges as an `expression` node:

#### Example AST for `1..5`:
```json
{
  "type": "range",
  "start": {
    "type": "number",
    "value": "1"
  },
  "end": {
    "type": "number",
    "value": "5"
  }
}
```

#### Example AST for `x..y`:
```json
{
  "type": "range",
  "start": {
    "type": "identifier",
    "value": "x"
  },
  "end": {
    "type": "identifier",
    "value": "y"
  }
}
```

---

### **Interpreter Behavior**

1. **Evaluation of Start and End**:
   - Evaluate the `start` and `end` nodes to resolve their numeric values.

2. **Generation of Ranges**:
   - If `start <= end`, generate an ascending range.
   - If `start > end`, generate a descending range.

3. **Example Code and Output**:
```genia
x = -3
y = 2
z = x..y
print(z)  // Output: [-3, -2, -1, 0, 1, 2]
```

---

### **Error Handling**

1. **Non-Numeric Start or End**:
   - If `start` or `end` evaluates to a non-numeric type, raise a `TypeError`.

2. **Infinite Ranges**:
   - Genia does not support infinite ranges directly.
   - Example of an error:
     ```genia
     z = x..infinity  // Raises: "TypeError: Unsupported range endpoint."
     ```

3. **Undefined Variables**:
   - If a variable used in a range is undefined, raise a `NameError`.

---

### **Advanced Features (Future Enhancements)**

1. **Step Specification**:
   - Add an optional step value for ranges:
     ```genia
     1..10:2  // Generates [1, 3, 5, 7, 9]
     ```
   - Syntax: `start..end:step`

2. **Lazy Evaluation**:
   - Use lazy generation for large ranges to optimize performance.

3. **Range Functions**:
   - Add utility functions like `range.length`, `range.contains(x)`, etc.

---

This specification provides a detailed blueprint for implementing and using ranges in the Genia language. Let me know if you'd like to proceed with implementing any part of this!
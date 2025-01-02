Here’s the updated documentation specification for regex in Genia, with all references to `if` statements removed:

---

# **Genia Language Specification: Regular Expressions**

This document defines how regular expressions are integrated into the Genia language and the functionality of the `~` operator.

---

## **Overview**

Regular expressions provide powerful text pattern matching. Genia introduces the `~` operator for regex matching, enabling concise and expressive syntax. Regex patterns can be defined using strings or raw strings.

---

## **Regex Syntax**

Genia uses regex syntax compatible with Python's `re` module.

### **Defining Regex Patterns**

Regex patterns can be defined using:
1. **Regular Strings**:
   - Supports escape sequences.
   ```genia
   pattern = "[A-Z]+\\n"  // Matches uppercase letters followed by a newline
   ```

2. **Raw Strings**:
   - Treats backslashes literally, simplifying regex definitions.
   ```genia
   pattern = r"[A-Z]+\n"  // Matches uppercase letters followed by a newline
   ```

---

## **Regex Matching with `~`**

### **Definition**

The `~` operator performs a regex match between two strings.

### **Syntax**

```genia
string ~ pattern
```

- **`string`**: The text to match against the regex.
- **`pattern`**: The regex pattern.

### **Return Value**

- Returns `true` if the string matches the regex.
- Returns `false` otherwise.

---

## **Examples**

### **Basic Matching**

```genia
input = "HELLO"
pattern = "[A-Z]+"
result = input ~ pattern
// result is true
```

### **Case-Sensitive Matching**

```genia
input = "hello"
pattern = "[A-Z]+"
result = input ~ pattern
// result is false
```

### **Raw String Patterns**

```genia
input = "HELLO"
pattern = r"[A-Z]+\n"
result = input ~ pattern
// result is false (newline is required)
```

---

## **Error Handling**

1. **Invalid Regex Pattern**:
   - Throws a `RuntimeError` with a clear error message.
   ```genia
   pattern = "[A-Z"  // Missing closing bracket
   result = input ~ pattern  // RuntimeError: Invalid regex pattern "[A-Z"
   ```

2. **Non-String Operands**:
   - Throws a `RuntimeError` if either operand is not a string.
   ```genia
   input = 123
   pattern = "[A-Z]+"
   result = input ~ pattern  // RuntimeError: Regex match requires both operands to be strings
   ```

---

Here’s the updated documentation with a new section on using regex as a guard:

---

# **Genia Language Specification: Regular Expressions**

This document defines how regular expressions are integrated into the Genia language and the functionality of the `~` operator.

---

## **Overview**

Regular expressions provide powerful text pattern matching. Genia introduces the `~` operator for regex matching, enabling concise and expressive syntax. Regex patterns can be defined using strings or raw strings.

---

## **Regex Syntax**

Genia uses regex syntax compatible with Python's `re` module.

### **Defining Regex Patterns**

Regex patterns can be defined using:
1. **Regular Strings**:
   - Supports escape sequences.
   ```genia
   pattern = "[A-Z]+\\n"  // Matches uppercase letters followed by a newline
   ```

2. **Raw Strings**:
   - Treats backslashes literally, simplifying regex definitions.
   ```genia
   pattern = r"[A-Z]+\n"  // Matches uppercase letters followed by a newline
   ```

---

## **Regex Matching with `~`**

### **Definition**

The `~` operator performs a regex match between two strings.

### **Syntax**

```genia
string ~ pattern
```

- **`string`**: The text to match against the regex.
- **`pattern`**: The regex pattern.

### **Return Value**

- Returns `true` if the string matches the regex.
- Returns `false` otherwise.

---

## **Using Regex as a Guard**

Guards in Genia allow conditions to refine the applicability of a function definition or pattern. Regular expressions can be used as guards to ensure input matches specific patterns.

### **Syntax**

```genia
fn function_name(param) when param ~ pattern -> result
```

- **`when param ~ pattern`**: The function definition is selected only if `param` matches the regex pattern.

### **Examples**

#### **Guard with Regex Matching**

```genia
fn validate(input) when input ~ r"^\d{3}-\d{3}-\d{4}$" -> true
                   | _ -> false;

result = validate("123-456-7890")
// result is true
```

#### **Multiple Guards**

```genia
fn classify(input) when input ~ r"^\d+$" -> "All digits"
                   | input ~ r"^[A-Za-z]+$" -> "All letters"
                   | _ -> "Mixed content";

result1 = classify("12345")
// result1 is "All digits"

result2 = classify("Hello")
// result2 is "All letters"

result3 = classify("Hello123")
// result3 is "Mixed content"
```

---

## **Error Handling**

1. **Invalid Regex Pattern in Guard**:
   - Throws a `RuntimeError` with a clear error message.
   ```genia
   fn example(input) when input ~ "[A-Z" -> true
   // RuntimeError: Invalid regex pattern "[A-Z"
   ```

2. **Non-String Parameter**:
   - Throws a `RuntimeError` if the guarded parameter is not a string.
   ```genia
   fn example(input) when input ~ r"^\d+$" -> true
   result = example(123)
   // RuntimeError: Regex match requires the parameter to be a string
   ```

---

## **Examples**

### **Regex Guards in Functions**

```genia
fn format_date(input) when input ~ r"^\d{4}-\d{2}-\d{2}$" -> "Valid date format"
                        | _ -> "Invalid date format";

result1 = format_date("2025-01-15")
// result1 is "Valid date format"

result2 = format_date("01/15/2025")
// result2 is "Invalid date format"
```

---

This section describes how regex can be used in guards to enhance function definitions with conditional matching logic. Let me know if you'd like further refinements!

## **Advanced Features (Future Enhancements)**

1. **Regex Flags**:
   - Add support for flags (e.g., case-insensitive matching):
     ```genia
     result = input ~ r"(?i)[a-z]+"  // Matches ignoring case
     ```

2. **Regex Functions**:
   - Add built-in functions for regex operations:
     - **`regex.find(string, pattern)`**: Returns the first match.
     - **`regex.replace(string, pattern, replacement)`**: Performs regex-based substitution.

3. **Capture Groups**:
   - Enable access to capture groups in matches:
     ```genia
     result = input ~ r"(\d{3})-(\d{3})-(\d{4})"
     groups = result.groups  // Access captured groups
     ```

---

## **Example Script**

```genia
fn validate_phone(input) -> input ~ r"^\d{3}-\d{3}-\d{4}$";

phone = "123-456-7890"
is_valid = validate_phone(phone)
// is_valid is true
```


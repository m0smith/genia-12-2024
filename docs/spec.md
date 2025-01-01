Here’s a specification for the GENIA language incorporating the current features, including the FFI system, extended identifier rules, and module-like functionality.

---

# GENIA Language Specification

## Overview
GENIA is a dynamic scripting language designed for data processing and automation. It combines simplicity with expressive power, offering features like flexible function definitions, a Foreign Function Interface (FFI), and modular organization.

## Features
- Dynamic typing with extensive support for identifiers, including Unicode.
- Flexible function definitions supporting native and foreign implementations.
- A module system inspired by JavaScript for organizing code.
- Operator context sensitivity to distinguish identifiers and operators.

---

## Syntax

### Identifiers
- Identifiers can consist of:
  - ASCII letters, digits, `_`, `$`.
  - Unicode characters, including non-Latin scripts.
  - Special characters `*` and `?`.
- Identifiers must begin with `$`, `_`, a Unicode letter, or a Latin alphabet letter.
- Examples:
  ```genia
  valid_identifiers = [x, αβγ, my_var, $value, _start, compute*]
  ```

---

### Comments
- **Single-line comments**: Use `//` or `#`.
- **Block comments**: Enclosed in `/* ... */`.
- Examples:
  ```genia
  // This is a single-line comment
  # Another single-line comment
  /*
  This is a block comment
  spanning multiple lines.
  */
  ```

---

### Variables
Variables are dynamically typed and can be assigned using `=`:
```genia
count = 10;
name = "GENIA";
```

---

### Functions

#### Function Definitions
Functions are defined using the `fn` keyword. Parameters are enclosed in parentheses, and the return value follows `->`.

##### Native Functions
```genia
fn add(x, y) -> x + y;
```

##### Foreign Functions
Foreign functions are defined using the `-> foreign` syntax:
```genia
fn rem(x, y) -> foreign "math.remainder";
```

#### Combined Functions
Supports combining multiple functions into a single function using the `|` operator:
```genia
fn compute(x, y) -> foreign "math.remainder" | (x) -> x | () -> 0
```

#### Multi-body Functions
Functions can define multiple bodies with the `|` operator:
```genia
fn fact(0) -> 1 | fact(n) -> n * fact(n - 1);
```

#### Pattern Matching
Pattern matching is supported using constants in the arg list:
```genia
fn cons(a, b) -> fn () -> 1 | (1) -> a | (2) -> b;
fn cons() -> fn () -> 0;
---

### Modules
Modules organize code into reusable namespaces.



---

### Operators
- Operators include: `+`, `-`, `*`, `/`, `=`, `<`, `>`, `!`, `==`, `!=`, `<=`, `>=`.
- Operators are context-sensitive:
  - Treated as part of an identifier if adjacent to identifier characters.
  - Otherwise treated as standalone operators.

#### Examples
```genia
fn example(x*, y?) -> x* + y?;
```

Lexer output:
```
IDENTIFIER: x*
OPERATOR: +
IDENTIFIER: y?
```

---

### Foreign Function Interface (FFI)
The FFI allows GENIA to call functions from external modules, libraries, or built-in Python functionality.

#### Syntax
```genia
fn rem(x, y) -> foreign "math.remainder";
```

- The string `"math.remainder"` is resolved into a Python callable using dynamic import:
  ```python
  module_name, func_name = "math.remainder".rsplit('.', 1)
  module = __import__(module_name)
  function = getattr(module, func_name)
  ```

- Errors are raised if:
  - The module or function does not exist.
  - The resolved object is not callable.

---

### Example Script

#### Math Utilities
```genia
fn add(x, y) -> x + y;
fn sub(x, y) -> x - y;
fn rem(x, y) -> foreign "math.remainder";

print(add(5, 3));  // Output: 8
print(sub(10, 4)); // Output: 6
print(rem(7, 3));  // Output: 1.0
```

#### Using Modules
```genia
// File: math.genia
export fn square(x) -> x * x;
export fn cube(x) -> x * x * x;
export const PI = 3.14159;

// Main Script
import { square, cube, PI } from "math";

print(square(3));  // Output: 9
print(cube(2));    // Output: 8
print(PI);         // Output: 3.14159
```

---

## Future Enhancements
1. **Module Aliases**: Allow imports with aliases for convenience.
   ```genia
   import * as math from "math";
   ```
2. **Remote Modules**: Enable imports from URLs or APIs.
   ```genia
   import "https://example.com/my_module.genia" as remote;
   ```
3. **Mixed Implementations**: Combine foreign and native bodies seamlessly.
4. **Pattern Matching**: Extend function definitions to support destructuring and pattern matching.

---

This specification reflects GENIA’s current capabilities and provides a foundation for further language evolution. Let me know if you'd like to refine or expand on any section!
Here's a specification for GENIA based on your requirements, existing files, and current features:

---

# GENIA Language Specification

## Overview

GENIA is a dynamic, expressive scripting language designed for human-readable syntax and ease of implementation. Its primary use cases include data processing, scripting, and automation, with influences from Clojure, AWK, and Erlang. GENIA supports modularity, pattern matching, tail-call optimization (TCO), and unique constructs like `decide` for conditional logic.

---

## Features

- **Dynamic Typing**: Variables are dynamically typed.
- **Pattern Matching**: Functions and conditionals support sophisticated pattern matching.
- **Modular Design**: Code can be organized into reusable modules.
- **Foreign Function Interface (FFI)**: Seamlessly integrates with Python and other external libraries.
- **Human-Centric Syntax**: Designed to be minimalistic and readable.
- **AWK-like Processing Mode**: Simplifies line-based data processing.
- **Error Handling**: Erlang-style retries and restarts with configurable backoff strategies.

---

## Syntax and Language Constructs

### Comments
- **Single-line**: `//` or `#`
- **Block**: `/* ... */`

Example:
```genia
// This is a single-line comment
/* This is a
   block comment */
```

### Variables
Variables are immutable by default but can be made mutable.

Example:
```genia
count = 42  // Immutable
mut value = "Mutable variable"
```

---

### Functions
#### Definitions
Functions can be defined natively or as foreign functions.

Example:
```genia
fn add(x, y) -> x + y
fn foreign_rem(x, y) -> foreign "math.remainder"
```

#### Multi-body Functions
Functions support multiple bodies and guards:
```genia
fn fact(0) -> 1 | fact(n) -> n * fact(n - 1)
```

#### Optional Syntax
Parentheses and commas are optional in definitions:
```genia
fn greet name -> "Hello, " + name
```

---

### Control Structures
#### `decide`
A replacement for `if` or `cond`, supporting pattern matching:
```genia
decide x:
  | x < 0 -> "Negative"
  | x == 0 -> "Zero"
  | -> "Positive"
```

---

### Looping
- `repeat` is the primary looping construct, working with collections and streams.
- Example:
```genia
repeat items -> print(item)
```

---

### Modules
Modules enable organized code and reusable namespaces.

Example:
```genia
// math.genia
export fn square(x) -> x * x

// main.genia
import { square } from "math"
print(square(4))
```

---

### Algebraic Data Types
GENIA supports simple tagged unions using the `data` keyword. Constructors are
regular functions that build structured values which can be decomposed through
pattern matching.

Example:
```genia
data Trio = Trio(a, b, c)

fn first(Trio(x, _, _)) -> x
first(Trio(1, 2, 3))
```

The call above evaluates to `1` as the `first` function matches the `Trio`
constructor and extracts its first field.

---

### Command-Line Arguments
Command-line arguments are accessed via `$1`, `$2`, ... `$NF` for the total count.

---

### AWK-Like Mode
Simplifies processing line-based input with `before()` and `after()` hooks:
```genia
decide before() { lineCount = 0 }
decide after() { print("Processed " + lineCount + " lines.") }
```

---

### Error Handling
Supports Erlang-style restarts:
```genia
retry(fn, max_attempts=3, backoff=exponential)
```

---

## Technical Details

### Lexer
- Supports Unicode and special characters like `*` and `?`.
- Tokens:
  - Keywords: `fn`, `foreign`, `when`
  - Operators: `+`, `-`, `*`, `/`, `=`, etc.
  - Punctuation: `(`, `)`, `{`, `}`, `,`, `;`

### Parser
- Recursive descent parser with support for precedence.
- Handles named and anonymous functions, pattern matching, and guards.

### Interpreter
- Manages environment variables, functions, and execution modes.
- AWK-like mode updates variables like `NR`, `NF`, and `$0`.

### Foreign Function Interface (FFI)
- Links GENIA functions to external Python functions.
- Example:
```genia
fn foreign_rem(x, y) -> foreign "math.remainder"
```

---

## Future Enhancements
- **Remote Modules**: Import modules from URLs.
- **More Patterns**: Extend pattern matching to include destructuring.
- **Native Error Handling**: More built-in error-handling constructs.
- **Parallelism**: Erlang-inspired actor model for concurrency.

This specification captures the key aspects of GENIA as currently implemented and offers a roadmap for further enhancements. Let me know if you'd like refinements or additions!
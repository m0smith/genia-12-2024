# GENIA

GENIA is a concise and dynamic scripting language designed for data processing and automation tasks. It offers dual execution modes, context-aware variables, and intuitive syntax, making it accessible for both novice and experienced programmers.

See [docs/goals.md](docs/goals.md) for the project goals.

## Features

- **Dual Execution Modes**: Supports Default and AWK-like modes for versatile input processing.
- **Context-Aware Variables**: Provides predefined variables for streamlined scripting.
- **Function Overloading**: Allows functions to support multiple argument patterns.
- **Pattern Matching**: Enables destructuring and guards in user-defined functions.
- **Tail Call Optimization**: Improves efficiency for recursive functions.
- **Built-in Functions**: Includes common utilities like `print`, `count`, and `reduce`.

## Installation

### Using Poetry

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/genia.git
   cd genia
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Activate the environment:
   ```bash
   poetry shell
   ```

4. Install the package:
   ```bash
   pip install .
   ```

## Usage

### Running a Script

To run a GENIA script:

```bash
python -m genia_interpreter path/to/script.genia
```

### Example Scripts

#### Default Mode Example

```genia
sum = reduce(+, 0, $ARGS);
print("Sum of arguments: " + sum);
```

Run:

```bash
python -m genia_interpreter script.genia 1 2 3
```

#### AWK Mode Example

```genia
define before() {
    lineCount = 0;
}

lineCount = lineCount + 1;

define after() {
    print("Total lines: " + lineCount);
}
```

Run:

```bash
echo -e "line1\nline2" | python -m genia_interpreter --awk script.genia
```

#### Dice Rolling Example

The `scripts/dice.genia` file defines a simple `roll` function. The interpreter
exposes a foreign `randrange` function which the built-in `randint` function
wraps for convenience.

```genia
define roll(sides) -> roll(1, sides)
define roll(0, _) -> 0
define roll(n, sides) -> randint(1, sides) + roll(n - 1, sides)
```

Run a 2d6 roll:

```bash
python -m genia_interpreter scripts/dice.genia 2 6
```

### Anthropic MCP Service

This repository also includes a small HTTP service that exposes the `roll`
function for use with Anthropic's MCP tools. The request-handling logic is
implemented in the `dice.genia` script itself. Start the service and send it a
request as follows:

```bash
python -m genia.services.dice_service &
curl -X POST -d '{"count": 2, "sides": 6}' http://localhost:8000
```


## Development

To run tests:

```bash
poetry run pytest
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request with a detailed description.

## Author

[Your Name](https://github.com/yourusername)

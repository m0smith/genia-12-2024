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

import sys
from genia.interpreter import GENIAInterpreter


def main():
    if len(sys.argv) < 2 or '--help' in sys.argv:
        print("Usage: genia <script_path> [arguments...] [--awk]")
        print("  --help       Show this help message")
        print("  --awk        Enable AWK-like processing mode")
        sys.exit(0)

    script_path = sys.argv[1]
    awk_mode = '--awk' in sys.argv

    try:
        with open(script_path, 'r') as file:
            code = file.read()
    except FileNotFoundError:
        print(f"Error: File '{script_path}' not found.")
        sys.exit(1)

    # Extract arguments excluding script path and flags
    script_args = [arg for arg in sys.argv[2:] if arg != '--awk']

    # Run the interpreter
    interpreter = GENIAInterpreter()
    try:
        interpreter.run(code, args=script_args, awk_mode=awk_mode)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

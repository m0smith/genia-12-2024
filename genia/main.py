import sys
import argparse

from genia.interpreter import GENIAInterpreter


def main():
    parser = argparse.ArgumentParser(description="GENIA script interpreter")
    parser.add_argument("script_path", type=str, help="Path to the GENIA script")
    parser.add_argument(
        "--awk",
        nargs="?",
        const="whitespace",  # Default value if --awk is specified without a value
        help="Enable AWK-like processing mode with optional split mode (e.g., 'csv')",
    )
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Additional arguments for the script")

    args = parser.parse_args()
    # Extract arguments
    script_path = args.script_path
    awk_mode = args.awk  # None if not provided, or 'whitespace' if --awk is used without a value
    script_args = args.args
    
    print(awk_mode)
    
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

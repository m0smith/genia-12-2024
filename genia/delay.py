import threading

class Delay:
    def __init__(self, expression):
        self.expression = expression
        self._value = None
        self._evaluated = False
        self._lock = threading.Lock()

    def value(self, interpreter=None):
        """
        Evaluates the delayed expression if it hasn't been evaluated yet.
        Returns the cached result on subsequent accesses.
        If an exception occurs, it is raised every time the value is accessed until a successful evaluation.
        """
        if not self._evaluated:
            with self._lock:
                if not self._evaluated:
                    try:
                        self._value = self.expression() if callable(self.expression) else self.expression
                        self._evaluated = True
                    except Exception as e:
                        self._evaluated = False
                        raise e
        return self._value

class Interpreter:
    def __init__(self):
        self.environment = {}

    def evaluate(self, node):
        """
        Evaluates an AST node.
        If the node is a Delay instance, it returns the delayed value.
        """
        if isinstance(node, Delay):
            return node.value(self)
        if callable(node):
            return node()
        # Add other evaluation logic here for handling different node types
        return node

def main():
    # Example Usage
    def expensive_computation():
        print("Computing...")
        return 42

    interpreter = Interpreter()

    delayed_value = Delay(expensive_computation)

    # First access triggers computation
    print(delayed_value.value(interpreter))  # Output: Computing... 42

    # Subsequent access returns cached result
    print(delayed_value.value(interpreter))  # Output: 42

    # Using Delay in a lazy list
    lazy_list = [Delay(lambda: i * 2) for i in range(5)]

    # Accessing elements in the lazy list
    print(lazy_list[0].value(interpreter))  # Output: 0
    print(lazy_list[3].value(interpreter))  # Output: 6

    # Exception Handling
    def error_prone_computation():
        raise ValueError("An error occurred!")

    error_delay = Delay(error_prone_computation)
    try:
        print(error_delay.value(interpreter))
    except Exception as e:
        print(e)  # Output: An error occurred!

    # Another attempt to access will raise the exception again
    try:
        print(error_delay.value(interpreter))
    except Exception as e:
        print(e)  # Output: An error occurred!

if __name__ == "__main__":
    main()
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
                        if isinstance(self.expression, dict):
                            # The expression is an AST node
                            self._value = interpreter.evaluate(self.expression)
                        elif callable(self.expression):
                            self._value = self.expression()
                        else:
                            self._value = self.expression
                        self._evaluated = True
                    except Exception as e:
                        self._evaluated = False
                        raise e
        return self._value


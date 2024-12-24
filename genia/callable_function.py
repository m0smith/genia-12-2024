class CallableFunction:
    def __init__(self, name, closure_context=None):
        self.name = name
        self.definitions = []
        self.closure_context = closure_context or {}  # Captured variables

    def add_definition(self, definition):
        if 'guard' not in definition:
            definition['guard'] = None
        self.definitions.append(definition)
        return self
    
    def __repr__(self):
        import json
        return f"CallableFunction('{self.name}, {self.closure_context}')"

    def __call__(self, interpreter, args, node_context):
        matching_function = None
        local_env = {}
        
        # Combine closure context with the current interpreter environment
        combined_env = {**interpreter.environment, **self.closure_context}
        previous_env = interpreter.environment
        for func in self.definitions:
            if len(func['parameters']) != len(args):
                continue
            trace_args = ""
            match = True
            for param, arg in zip(func['parameters'], args):
                trace_args = f"{trace_args} {param['value']}={arg}"
                if param['type'] == 'identifier':
                    local_env[param['value']] = arg
                elif param['type'] == 'number' and arg != int(param['value']):
                    match = False
                    break
                elif param['type'] == 'string' and arg != param['value']:
                    match = False
                    break
            if not match:
                continue

            if func['guard']:
                combined_env.update(local_env)
                interpreter.environment = combined_env
                try:
                    if not interpreter.evaluate(func['guard']):
                        continue
                finally:
                    interpreter.environment = previous_env

            matching_function = func
            break

        if not matching_function:
            raise RuntimeError(f"No matching function for {self.name} with arguments {args} at {node_context}")

        # Use the combined environment for body evaluation
        combined_env.update(local_env)
        interpreter.environment = combined_env
        try:
            body = matching_function['body']
            if interpreter.trace:
                interpreter.write_to_stderr(f"Executing {self.name} with  {trace_args} at {node_context} with body {body}")

            if callable(body):
                # If body is a Python function, call it with args
                return body(*args)
            else:
                # Otherwise, evaluate it as an AST
                return interpreter.evaluate(body)
        finally:
            interpreter.environment = previous_env

    def append(self, ast_node):
        """
        Append a new function definition to the CallableFunction.
    
        Parameters:
        - ast_node: The AST node representing the function definition.
        """
        if not isinstance(ast_node, dict) or 'parameters' not in ast_node or 'body' not in ast_node:
            raise ValueError("Invalid AST node: must contain 'parameters' and 'body'.")
        self.add_definition(ast_node)

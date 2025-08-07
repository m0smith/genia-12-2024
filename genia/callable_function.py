from genia.lazy_seq import LazySeq
from genia.patterns import bind_list_pattern
from genia.seq import Sequence


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
    
    def matches(self, definition, args):
        if len(definition['parameters']) != len(args):
            return False
        for param, arg in zip(definition['parameters'], args):
            if not self.match_parameter(param, arg):
                return False
        return True
    
    def match_parameter(self, param, arg):
        match param.get('type'):
            case 'list_pattern':
                return self.match_list_pattern(param, arg)
            case 'identifier':
                return True # Identifiers always match
            case 'string':
                return param['value'] == arg
            case 'number':
                return int(param['value']) == arg
            case _:
                
                raise ValueError(f"Unsupported parameter type: {param['type']}")
            
    def match_list_pattern(self, pattern, arg):
        if not isinstance(arg, (list, LazySeq, Sequence)):
            return False
        if isinstance(arg, list):
            return self.match_list_pattern_list(pattern, arg)
        elif isinstance(arg, LazySeq):
            return self.match_list_pattern_lazy_seq(pattern, arg)
        elif isinstance(arg, Sequence):
            return self.match_list_pattern_sequence(pattern, arg)
        else:
            raise ValueError(f"Unsupported type: {type(arg)}")
    
    def match_list_pattern_list(self, pattern, lst):
        elements = pattern['elements']
        if len(elements) == 0:  # Match an empty list
            return len(lst) == 0
        if len(elements) >= 2 and elements[-1]['type'] == 'rest':
            # Match `[first, ..rest]`
            return len(lst) >= len(elements) - 1
        return len(lst) == len(elements)  # Exact length match
    
    def _match_length_iter(self, elements, iterator):
        """Check sequence length using incremental iteration.

        Only consumes as many elements from ``iterator`` as necessary to
        determine whether ``elements`` match by length.  This avoids eager
        evaluation of potentially infinite or expensive sequences.
        """
        n = len(elements)

        # Handle empty pattern
        if n == 0:
            try:
                next(iterator)
                return False
            except StopIteration:
                return True

        # Determine if the pattern uses a rest element at the end
        has_rest = n >= 2 and elements[-1]["type"] == "rest"
        required = n - 1 if has_rest else n

        count = 0
        for _ in iterator:
            count += 1
            if count >= required:
                if has_rest:
                    return True
                # For exact match, we still need to ensure there are no extra
                # elements.  Peek one more and abort early if found.
                try:
                    next(iterator)
                    return False
                except StopIteration:
                    return True
        # Iterator exhausted before reaching required length
        return False

    def match_list_pattern_lazy_seq(self, pattern, lazy_seq):
        elements = pattern["elements"]
        return self._match_length_iter(elements, iter(lazy_seq))

    def match_list_pattern_sequence(self, pattern, sequence):
        elements = pattern["elements"]

        def iter_sequence(seq):
            s = seq
            while isinstance(s, Sequence) and not s.is_empty():
                # We don't care about the actual values, only the presence of
                # elements, so just advance the sequence.
                s = s.rest()
                yield None
            if isinstance(s, list):
                for _ in s:
                    yield None

        return self._match_length_iter(elements, iter_sequence(sequence))
    
    def bind_parameters(self, definition, args):
        local_env = {}
        for param, arg in zip(definition['parameters'], args):
            match param.get('type'):
                case 'list_pattern':
                    bind_list_pattern(param, arg, local_env)
                case 'identifier':
                    local_env[param['value']] = arg
                case 'string':
                    pass
                case 'number':
                    pass
                case _:
                    raise ValueError(f"Unsupported parameter type: {param['type']}")
        return local_env
    
    def __repr__(self):
        import json
        return f"CallableFunction('{self.name}, {self.definitions}')"

    def __call__(self, interpreter, args, node_context):
        matching_function = None
        local_env = {}
        
        # Combine closure context with the current interpreter environment
        combined_env = {**interpreter.environment, **self.closure_context}
        previous_env = interpreter.environment
        for definition in self.definitions:
            if not self.matches(definition, args):
                continue
            local_env = self.bind_parameters(definition, args)
            
            # trace_args = ""
            # match = True
            # for param, arg in zip(definition['parameters'], args):
            #     trace_args = f"{trace_args} {param['value']}={arg}"
            #     if param['type'] == 'identifier':
            #         local_env[param['value']] = arg
            #     elif param['type'] == 'number' and arg != int(param['value']):
            #         match = False
            #         break
            #     elif param['type'] == 'string' and arg != param['value']:
            #         match = False
            #         break
            # if not match:
            #     continue

            if definition['guard']:
                combined_env.update(local_env)
                interpreter.environment = combined_env
                try:
                    if not interpreter.evaluate(definition['guard']):
                        continue
                finally:
                    interpreter.environment = previous_env

            matching_function = definition
            break

        if not matching_function:
            raise RuntimeError(f"No matching function for {self.name} with arguments {args} at {node_context}")

        # Use the combined environment for body evaluation
        combined_env.update(local_env)
        interpreter.environment = combined_env
        try:
            body = matching_function['body']
            if interpreter.trace:
                interpreter.write_to_stderr(f"Executing {self.name} at {node_context} with body {body}")

            if matching_function.get("foreign", False):
                # If body is a Foreign function, call it with args
                result = body(*args)
            else:
                # Otherwise, evaluate it as an AST
                result = interpreter.evaluate(body)
            
            return result
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

from genia.lazy_seq import LazySeq
from collections import deque
from itertools import islice


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
                
                raise ValueError(f"Unsupport parameter type: {param['type']}")
            
    def match_list_pattern(self, pattern, arg):
        if not isinstance(arg, (list, LazySeq)):
            return False
        if isinstance(arg, list):
            return self.match_list_pattern_list(pattern, arg)
        elif isinstance(arg, LazySeq):
            return self.match_list_pattern_lazy_seq(pattern, arg)
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
    
    def match_list_pattern_lazy_seq(self, pattern, lazy_seq):
        elements = pattern['elements']
        it = iter(lazy_seq)
        len_it = len(deque(it, maxlen=len(elements) + 1))
        # if len(elements) == 0:  # Match an empty list
        #     return len(lazy_seq) == 0
        if len(elements) >= 2 and elements[-1]['type'] == 'rest':
            # Match `[first, ..rest]`
            return len_it >= len(elements) - 1
        return len_it == len(elements)  # Exact length match
    
    def bind_parameters(self, definition, args):
        local_env = {}
        for param, arg in zip(definition['parameters'], args):
            match param.get('type'):
                case 'list_pattern':
                    self.bind_list_pattern(param, arg, local_env)
                case 'identifier':
                    local_env[param['value']] = arg
                case 'string':
                    pass
                case 'number':
                    pass
                case _:
                    raise ValueError(f"Unsupport parameter type: {param['type']}")
        return local_env

    def bind_list_pattern(self, pattern, arg, local_env):
        elements = pattern['elements']
        if len(elements) == 0:  # Empty list
            return
        for i, element in enumerate(elements):
            if element['type'] == 'rest':
                # Convert the remaining elements of the iterator into a list
                if hasattr(arg, '__getitem__'):  # Check if `arg` is a list-like object
                    local_env[element['value']] = arg[i:]
                else:  # Assume `arg` is an iterator
                    local_env[element['value']] = list(islice(arg, i, None))
            else:
                if hasattr(arg, '__getitem__'):  # Check if `arg` is a list-like object
                    local_env[element['value']] = arg[i]
                else:  # Assume `arg` is an iterator
                    local_env[element['value']] = next(islice(arg, i, i + 1))
    
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

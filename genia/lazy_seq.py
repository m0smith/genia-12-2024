import copy
from threading import RLock

class LazySeq:
    def __init__(self, fn=None, seq=None):
            self.fn = fn
            self.seq = seq
            self.seq_value = None
            self.lock = RLock()

    def __iter__(self):
        if self.fn:
            self._lock_and_force()
        if self.seq_value is None:
            return iter([]) if self.seq is None else self.seq  # Return an empty iterator if sv is None
        return iter(self.seq_value)

    def _lock_and_force(self):
        with self.lock:
            if self.fn:
                # Create a copy if the result is list-like to ensure immutability
                result = self.fn()
                if isinstance(result, list):
                    self.seq_value = copy.deepcopy(result)
                else:
                    self.seq_value =  result if result is not None else []
                self.fn = None
                self.seq = iter(self.seq_value)

    def _realize(self):
        with self.lock:
            if self.fn:
                self._lock_and_force()
                # Further unwrapping as needed
                self.seq = iter(self.seq_value)
                self.lock = None

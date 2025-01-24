from abc import ABC, abstractmethod

class Sequence(ABC):
    @abstractmethod
    def first(self):
        """Returns the first element of the sequence."""
        pass

    @abstractmethod
    def rest(self):
        """Returns the rest of the sequence."""
        pass
    @abstractmethod
    def is_empty(self):
        """Return true is first is available"""
        pass
    
class IterSeq(Sequence):
    def __init__(self, iterator):
        self._iterator = iter(iterator)
        self._first = None
        self._has_first = False
        self._rest = None
        

    def first(self):
        """Returns the first element of the sequence."""
        if not self._has_first:
            try:
                self._first = next(self._iterator)
                self._has_first = True
            except StopIteration:
                raise ValueError("IterSeq The sequence is empty.")
        return self._first
    
    def is_empty(self):
        """Returns true if first is available"""
        if not self._has_first:
            try:
                self._first = next(self._iterator)
                self._has_first = True
            except StopIteration:
                return True
        return False

    def rest(self):
        """Returns the rest of the sequence as another IterSeq."""
        if self._rest is not None:
            return self._rest
        if not self._has_first:
            self.first()  # Ensure the first element is consumed.
        self._rest = IterSeq(self._iterator)
        return self._rest
    
class DelaySeq(Sequence):
    def __init__(self, value=None, delayed=None):
        """
        Initialize DelaySeq with a value and a Delay.
        :param value: The first element of the sequence.
        :param delay: An object with a value() method that returns a Sequence.
        """
        self.empty = value is None and delayed is None
        self._value = value
        if self.empty:
            self._delayed = delayed
        else:
            self._delayed = delayed
        
    def is_empty(self):
        return self.empty
    
    def first(self):
        """Return the first element of the sequence."""
        if self.empty:
            raise ValueError("The sequence is empty.")
        return self._value

    def rest(self):
        """
        Return the rest of the sequence. Lazily evaluates the delay.
        :return: A Sequence representing the rest of the elements.
        """
        if self.empty or self._delayed is None:
            return []
        return self._delayed.value()

def delay_seq(head, tail):
    return DelaySeq(head, tail)

def count_seq(max, seq):
    if max < 1 or seq.is_empty():
        return 0
    return 1 + count_seq(max - 1, seq.rest())

def nth_seq(n, seq):
    """Zero based"""
    if n == 0:
        return seq.first()
    else:
        return nth_seq(n - 1, seq.rest())
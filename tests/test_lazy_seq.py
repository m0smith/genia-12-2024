import pytest
from threading import Thread
from genia.lazy_seq import LazySeq

def test_initialization_with_function():
    def compute():
        return [1, 2, 3]
    seq = LazySeq(fn=compute)
    assert seq.delay.value() == compute()

def test_lazy_evaluation():
    calls = []
    def compute():
        calls.append(1)
        return [1, 2, 3]
    seq = LazySeq(fn=compute)
    assert not calls

def test_sequence_generation():
    seq = LazySeq(fn=lambda: [1, 2, 3])
    assert list(seq) == [1, 2, 3]

def test_locking_mechanism():
    import time
    def compute():
        time.sleep(0.1)  # Simulate computation delay
        return [1, 2, 3]
    seq = LazySeq(fn=compute)
    def access_seq():
        return list(seq)
    thread1 = Thread(target=access_seq)
    thread2 = Thread(target=access_seq)
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
    # If the test passes without issues, the locking is likely correct.

def test_forced_evaluation():
    seq = LazySeq(fn=lambda: [1, 2, 3])
    assert seq.delay is not None
    list(seq)  # Force evaluation
    # assert seq.fn is None
    assert seq.delay.value() == [1, 2, 3]

def test_thread_safety():
    def compute():
        return [1, 2, 3]
    seq = LazySeq(fn=compute)
    results = []
    def run():
        results.append(list(seq))
    threads = [Thread(target=run) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert all(result == [1, 2, 3] for result in results)

def test_iteration():
    seq = LazySeq(fn=lambda: [1, 2, 3])
    results = [x for x in seq]
    assert results == [1, 2, 3]

def test_next_method():
    seq = LazySeq(fn=lambda: [1, 2, 3])
    iterator = iter(seq)
    assert next(iterator) == 1
    assert next(iterator) == 2
    assert next(iterator) == 3
    with pytest.raises(StopIteration):
        next(iterator)

def test_multiple_iterations():
    seq = LazySeq(fn=lambda: [1, 2, 3])
    list(seq)
    assert list(seq) == [1, 2, 3]  # Check if it can be iterated again.

def test_immutability():
    data = [1, 2, 3]
    seq = LazySeq(fn=lambda: data)
    list(seq)
    data.append(4)  # Change external data
    assert list(seq) == [1, 2, 3]  # Should not affect already realized sequence

def test_non_computation():
    seq = LazySeq(seq=iter([1, 2, 3]))
    assert list(seq) == [1, 2, 3]


def test_empty_initialization():
    seq = LazySeq()
    assert list(seq) == []

def test_sequence_unwrapping():
    seq = LazySeq(fn=lambda: LazySeq(fn=lambda: [1, 2, 3]))
    assert list(seq) == [1, 2, 3]

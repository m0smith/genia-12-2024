import random


def randrange(*args):
    """Return a randomly selected element from range(*args)."""
    int_args = [int(a) for a in args]
    return random.randrange(*int_args)


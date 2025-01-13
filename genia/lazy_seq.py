from genia.delay import Delay
import copy

def make_persistent(fn):
    def i():
        rtnval = fn()
        if isinstance(rtnval, (list, dict, set)):
            rtnval = copy.deepcopy(rtnval)
        return rtnval
    return i

class LazySeq:
    def __init__(self, fn=None, seq=None):
        print(f"LazySeq fn={fn} seq={seq}")
        if isinstance(fn, list):
            seq = fn
            fn = None
        if fn:
            self.delay = Delay(make_persistent(fn))
        elif seq is not None:
            self.delay = Delay(make_persistent(lambda: seq))
        else:
            self.delay = Delay(lambda: [])

    def __iter__(self):
        rtnval = self.delay.value()
        return iter(rtnval)
    
def lazyseq(fn=None, seq=None):
    print(f"lazyseq fn={fn}" )
    return LazySeq(fn, seq)

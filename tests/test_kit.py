import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from genia.interpreter import GENIAInterpreter


def test_kit_import_and_visibility():
    code = """
    kit math(a) {
        export fn inc(x) -> x + a;
    }
    import math(1);
    inc(5);
    """
    interp = GENIAInterpreter()
    result = interp.run(code)
    assert result == 6
    assert 'a' not in interp.interpreter.environment


def test_kit_reload():
    code = """
    kit math(a) {
        export fn inc(x) -> x + a;
    }
    import math(1);
    r1 = inc(3);
    import math(2);
    inc(3);
    """
    interp = GENIAInterpreter()
    result = interp.run(code)
    assert interp.interpreter.environment['r1'] == 4
    assert result == 5


def test_nested_kit_import():
    code = """
    kit base(v) {
        export fn val() -> v;
    }
    kit wrapper() {
        import base(5);
        export fn get() -> val();
    }
    import wrapper();
    get();
    """
    interp = GENIAInterpreter()
    result = interp.run(code)
    assert result == 5


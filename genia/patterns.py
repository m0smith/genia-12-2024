from __future__ import annotations

from itertools import islice
from genia.lazy_seq import LazySeq
from genia.seq import Sequence, nth_seq


def _is_spread(element: dict) -> bool:
    return (
        (element.get("type") == "unary_operator" and element.get("operator") == "..")
        or element.get("type") == "rest"
    )


def _spread_name(element: dict) -> str:
    if element.get("type") == "unary_operator":
        return element["operand"]["value"]
    return element["value"]


def bind_list_pattern(pattern: dict, arg, local_env: dict) -> None:
    """Bind a list pattern to ``arg`` updating ``local_env``.

    Supports patterns like ``[head, ..tail]`` and ``[..pre, mid, ..post]``.
    ``arg`` may be a list, ``LazySeq`` or ``Sequence`` instance.
    """
    elements = pattern["elements"]
    if len(elements) == 0:
        return

    # Handle pattern of form [..pre, mid, ..post]
    if (
        len(elements) == 3
        and _is_spread(elements[0])
        and _is_spread(elements[2])
        and isinstance(arg, list)
    ):
        pre_name = _spread_name(elements[0])
        post_name = _spread_name(elements[2])
        mid_pat = elements[1]
        from genia.interpreter import CallableFunction

        cf = CallableFunction("_bind_helper")
        for i, val in enumerate(arg):
            if cf.match_parameter(mid_pat, val):
                local_env[pre_name] = arg[:i]
                local_env[post_name] = arg[i + 1 :]
                match mid_pat.get("type"):
                    case "identifier":
                        local_env[mid_pat["value"]] = val
                    case "wildcard":
                        pass
                    case "list_pattern":
                        bind_list_pattern(mid_pat, val, local_env)
                    case "constructor_pattern":
                        cf.bind_constructor_pattern(mid_pat, val, local_env)
                    case "number_literal":
                        if val != mid_pat["value"]:
                            raise RuntimeError("Pattern mismatch")
                    case "string_literal":
                        if val != mid_pat["value"]:
                            raise RuntimeError("Pattern mismatch")
                return
        raise RuntimeError("No matching element for pattern")

    for i, element in enumerate(elements):
        if _is_spread(element):
            name = _spread_name(element)
            if isinstance(arg, list):
                local_env[name] = arg[i:]
            elif isinstance(arg, LazySeq):
                local_env[name] = list(islice(arg, i, None))
            elif isinstance(arg, Sequence):
                local_env[name] = arg.rest()
            else:
                raise ValueError(
                    f"Unsupported type for spread binding: {type(arg).__name__}"
                )
        else:
            if isinstance(arg, list):
                if i < len(arg):
                    if element["type"] == "wildcard":
                        pass
                    elif element["type"] == "list_pattern":
                        bind_list_pattern(element, arg[i], local_env)
                    else:
                        local_env[element["value"]] = arg[i]
                else:
                    raise RuntimeError(
                        f"Not enough elements to bind parameter '{element.get('value', '?')}'"
                    )
            elif isinstance(arg, LazySeq):
                try:
                    v = next(islice(arg, i, i + 1))
                    if element["type"] == "wildcard":
                        pass
                    elif element["type"] == "list_pattern":
                        bind_list_pattern(element, v, local_env)
                    else:
                        local_env[element["value"]] = v
                except StopIteration:
                    raise RuntimeError(
                        f"Not enough elements to bind parameter '{element.get('value', '?')}'"
                    )
            elif isinstance(arg, Sequence):
                try:
                    v = nth_seq(i, arg)
                    if element["type"] == "wildcard":
                        pass
                    elif element["type"] == "list_pattern":
                        bind_list_pattern(element, v, local_env)
                    else:
                        local_env[element["value"]] = v
                except StopIteration:
                    raise RuntimeError(
                        f"Not enough elements to bind parameter '{element.get('value', '?')}'"
                    )
            else:
                raise ValueError(
                    f"Unsupported type for binding: {type(arg).__name__}"
                )

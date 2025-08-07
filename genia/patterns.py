from __future__ import annotations

from genia.interpreter import as_list_protocol


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
    ``arg`` is adapted using :func:`as_list_protocol` and must therefore
    conform to :class:`genia.interpreter.ListProtocol`.
    """
    elements = pattern["elements"]
    if len(elements) == 0:
        return

    adapter = as_list_protocol(arg)

    # Handle pattern of form [..pre, mid, ..post]
    if (
        len(elements) == 3
        and _is_spread(elements[0])
        and _is_spread(elements[2])
    ):
        lst = adapter.to_list()
        pre_name = _spread_name(elements[0])
        post_name = _spread_name(elements[2])
        mid_pat = elements[1]
        from genia.interpreter import CallableFunction

        cf = CallableFunction("_bind_helper")
        for i, val in enumerate(lst):
            if cf.match_parameter(mid_pat, val):
                local_env[pre_name] = lst[:i]
                local_env[post_name] = lst[i + 1 :]
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
            local_env[name] = adapter.tail(i)
        else:
            try:
                v = adapter.head(i)
            except Exception:
                raise RuntimeError(
                    f"Not enough elements to bind parameter '{element.get('value', '?')}'",
                )
            match element["type"]:
                case "wildcard":
                    pass
                case "list_pattern":
                    bind_list_pattern(element, v, local_env)
                case "constructor_pattern":
                    from genia.interpreter import CallableFunction
                    CallableFunction("_bind_helper").bind_constructor_pattern(
                        element, v, local_env
                    )
                case "number_literal":
                    if v != element["value"]:
                        raise RuntimeError("Pattern mismatch")
                case "string_literal":
                    if v != element["value"]:
                        raise RuntimeError("Pattern mismatch")
                case _:
                    local_env[element["value"]] = v


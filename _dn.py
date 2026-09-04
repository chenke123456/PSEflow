def port_dn(inputs: dict, slot: str = "输入口"):
    raw = inputs.get(slot)
    if raw is None or isinstance(raw, (dict, list)):
        return None
    try:
        n = float(raw)
    except (TypeError, ValueError):
        return None
    return n if n > 0 else None


def pass_dn(dn) -> int:
    return int(round(dn))

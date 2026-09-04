from .registry import NodePlugin, register

# HG/T 20592 管法兰公称直径档，单位 mm。
DN_GRADES = (
    10, 15, 20, 25, 32, 40, 50, 65, 80, 100, 125, 150, 200, 250,
    300, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000,
)


def _parse_dn(raw) -> int:
    text = str(raw if raw is not None else "").strip()
    if not text:
        raise ValueError("公称直径：请选择法兰公称直径")
    if text.upper().startswith("DN"):
        text = text[2:].strip()
    try:
        n = int(round(float(text)))
    except ValueError as exc:
        raise ValueError("公称直径：须为法兰标准档") from exc
    if n not in DN_GRADES:
        raise ValueError("公称直径：须为 HG/T 20592 法兰档")
    return n


@register
class NominalDN(NodePlugin):
    type = "NominalDN"
    title = "公称直径"
    category = "通用件"
    order = 28
    inputs = []
    outputs = [{"name": "公称直径", "type": "公称直径"}]
    widgets = [
        {
            "key": "DN",
            "label": "DN",
            "value": "80",
            "options": [str(n) for n in DN_GRADES],
        }
    ]
    hint = "无上游。中间选法兰公称直径档，输出公称直径量。查 HG/T 20592"

    def execute(self, node, inputs, vault):
        w = node.get("widgets") or {}
        n = _parse_dn(w.get("DN"))
        return {"公称直径": n}

    def preview(self, pack):
        n = pack.get("公称直径")
        return f"DN{n}" if n is not None else "公称直径"

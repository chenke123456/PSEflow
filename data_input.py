from .registry import NodePlugin, register


@register
class DataInput(NodePlugin):
    type = "DataInput"
    title = "输入数据"
    category = "数据"
    order = 27
    inputs = []
    outputs = [{"name": "数据", "type": "INT"}]
    widgets = [{"key": "value", "label": "变量", "step": 1, "value": "0"}]
    hint = "无上游。填一个整数中间变量，输出 INT。"

    def execute(self, node, inputs, vault):
        w = node.get("widgets") or {}
        raw = str(w.get("value") if w.get("value") is not None else "").strip()
        if not raw:
            raise ValueError("输入数据：请填写整数变量")
        try:
            n = int(float(raw))
        except ValueError as exc:
            raise ValueError("输入数据：变量必须是整数") from exc
        return {"数据": n}

    def preview(self, pack):
        n = pack.get("数据")
        return f"数据 {n}" if n is not None else "输入数据"

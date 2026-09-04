from engine import calc_support, clone_data

from .registry import NodePlugin, register


@register
class Support(NodePlugin):
    type = "Support"
    title = "支座"
    category = "通用件"
    order = 22
    inputs = [{"name": "数据", "type": "DATA"}]
    outputs = [{"name": "数据", "type": "DATA"}, {"name": "鞍座宽", "type": "INT"}]
    widgets = [
        {"key": "kind", "label": "型式", "numeric": False, "value": "鞍式"},
        {"key": "n", "label": "数量", "step": 1, "value": "2"},
    ]
    hint = "通用件。按 Di 选 NB/T 47065 鞍式，宽度约 0.1Di"

    def execute(self, node, inputs, vault):
        data = calc_support(clone_data(inputs), node.get("widgets") or {})
        return {"数据": data, "鞍座宽": data["saddle_b"]}

    def preview(self, pack):
        data = pack.get("数据") if isinstance(pack.get("数据"), dict) else {}
        return data.get("support_kind") or "支座"

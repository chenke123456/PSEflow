from engine import calc_manhole, clone_data

from .registry import NodePlugin, register


@register
class Manhole(NodePlugin):
    type = "Manhole"
    title = "人孔"
    category = "通用件"
    order = 21
    inputs = [{"name": "数据", "type": "DATA"}]
    outputs = [{"name": "数据", "type": "DATA"}, {"name": "人孔直径", "type": "INT"}]
    widgets = [
        {"key": "DN", "label": "DN", "step": 50},
        {"key": "kind", "label": "型式", "numeric": False, "value": "回转盖人孔"},
    ]
    hint = "通用件。按 Di 选 HG/T 21514，不估盖板强度"

    def execute(self, node, inputs, vault):
        data = calc_manhole(clone_data(inputs), node.get("widgets") or {})
        return {"数据": data, "人孔直径": data["manhole_dn"]}

    def preview(self, pack):
        return f"DN{pack.get('人孔直径')}"

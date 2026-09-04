from engine import calc_fastener, take_data

from .registry import NodePlugin, register


@register
class Fastener(NodePlugin):
    type = "Fastener"
    title = "紧固件"
    category = "通用件"
    order = 24
    inputs = [{"name": "数据", "type": "DATA"}]
    outputs = [{"name": "数据", "type": "DATA"}, {"name": "螺栓数", "type": "INT"}]
    widgets = [
        {"key": "DN", "label": "DN", "step": 5, "value": "80"},
        {"key": "PN", "label": "PN", "step": 0.2, "value": "1.6"},
    ]
    hint = "通用件。型号已知则螺栓数已知。上游数据可选"

    def execute(self, node, inputs, vault):
        data = calc_fastener(take_data(inputs), node.get("widgets") or {})
        return {"数据": data, "螺栓数": data["bolt_count"]}

    def preview(self, pack):
        data = pack.get("数据") if isinstance(pack.get("数据"), dict) else {}
        return f"{data.get('bolt_count')}×{data.get('bolt_size')}"

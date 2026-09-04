from engine import calc_tubes, clone_data

from .registry import NodePlugin, register


@register
class HexTubes(NodePlugin):
    type = "HexTubes"
    title = "换热管"
    category = "通用件"
    order = 9
    inputs = [{"name": "数据", "type": "DATA"}]
    outputs = [{"name": "数据", "type": "DATA"}, {"name": "管数", "type": "INT"}, {"name": "管间距", "type": "INT"}]
    widgets = [{"key": "N", "label": "N", "step": 1}, {"key": "t", "label": "t", "step": 1}]
    hint = "通用件。N = A / (π·do·L)"

    def execute(self, node, inputs, vault):
        data = calc_tubes(clone_data(inputs), node.get("widgets") or {})
        return {"数据": data, "管数": data["N"], "管间距": data["t"]}

    def preview(self, pack):
        return f"管数 {pack.get('管数')} · 间距 {pack.get('管间距')} mm"

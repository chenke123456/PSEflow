from engine import calc_head, clone_data

from .registry import NodePlugin, register


@register
class HexHead(NodePlugin):
    type = "HexHead"
    title = "封头"
    category = "通用件"
    order = 13
    inputs = [{"name": "数据", "type": "DATA"}]
    outputs = [{"name": "数据", "type": "DATA"}, {"name": "封头厚", "type": "INT"}]
    widgets = [{"key": "K", "label": "K", "step": 0.1, "value": "1"}]
    hint = "通用件。标准椭圆封头"

    def execute(self, node, inputs, vault):
        data = calc_head(clone_data(inputs), node.get("widgets") or {})
        return {"数据": data, "封头厚": data["t_head"]}

    def preview(self, pack):
        return f"封头厚 {pack.get('封头厚')} mm"

from engine import calc_hex_area, clone_data, widget_data

from .registry import NodePlugin, register

WIDGETS = [
    {"key": "K", "label": "总传热系数 K", "step": 10, "value": "500"},
    {"key": "phi_A", "label": "面积裕量", "step": 0.05, "value": "0.2"},
    {"key": "flow", "label": "流向", "numeric": False, "value": "逆流"},
]


@register
class HexArea(NodePlugin):
    type = "HexArea"
    title = "换热面积"
    category = "理论计算"
    order = 26
    inputs = [{"name": "数据", "type": "DATA"}]
    outputs = [{"name": "数据", "type": "DATA"}, {"name": "面积", "type": "INT"}]
    widgets = WIDGETS
    hint = "逆流 LMTD：A = Q / (K·Δtm)，含裕量。不要接再沸器的温差面积"

    def execute(self, node, inputs, vault):
        data = clone_data(inputs)
        data.update(widget_data(node.get("widgets") or {}))
        data = calc_hex_area(data)
        return {"数据": data, "面积": data["A"]}

    def preview(self, pack):
        return f"A={pack.get('面积')} m²"

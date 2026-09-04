from engine import calc_reb_area, clone_data

from .registry import NodePlugin, register


@register
class RebArea(NodePlugin):
    type = "RebArea"
    title = "温差面积"
    category = "理论计算"
    order = 8
    inputs = [{"name": "数据", "type": "DATA"}]
    outputs = [{"name": "数据", "type": "DATA"}, {"name": "面积", "type": "INT"}]
    widgets = []
    hint = "恒温传热：A = Q / (K·ΔTm)，含裕量"

    def execute(self, node, inputs, vault):
        data = calc_reb_area(clone_data(inputs))
        return {"数据": data, "面积": data["A"]}

    def preview(self, pack):
        return f"A={pack.get('面积')} m²"

from engine import calc_reb_dia, clone_data

from .registry import NodePlugin, register


@register
class RebDia(NodePlugin):
    type = "RebDia"
    title = "壳径初估"
    category = "理论计算"
    order = 10
    inputs = [{"name": "数据", "type": "DATA"}]
    outputs = [{"name": "数据", "type": "DATA"}, {"name": "内径", "type": "INT"}]
    widgets = []
    hint = "Di ≈ do·√(N/η)，无内径时写入后续筒体"

    def execute(self, node, inputs, vault):
        data = calc_reb_dia(clone_data(inputs))
        return {"数据": data, "内径": data.get("Di")}

    def preview(self, pack):
        return f"Di={pack.get('内径')} mm"

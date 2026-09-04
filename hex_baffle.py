from engine import calc_baffle, clone_data

from .registry import NodePlugin, register


@register
class HexBaffle(NodePlugin):
    type = "HexBaffle"
    title = "折流板"
    category = "通用件"
    order = 14
    inputs = [{"name": "数据", "type": "DATA"}]
    outputs = [{"name": "数据", "type": "DATA"}, {"name": "间距", "type": "INT"}, {"name": "数量", "type": "INT"}]
    widgets = [
        {"key": "B_ratio", "label": "B/Di", "step": 0.05, "value": "0.4"},
        {"key": "h_ratio", "label": "h/Di", "step": 0.05, "value": "0.25"},
    ]
    hint = "管壳式换热器用，再沸器可不接"

    def execute(self, node, inputs, vault):
        data = calc_baffle(clone_data(inputs), node.get("widgets") or {})
        return {"数据": data, "间距": data["B"], "数量": data["NB"]}

    def preview(self, pack):
        return f"间距 {pack.get('间距')} mm · {pack.get('数量')} 块"

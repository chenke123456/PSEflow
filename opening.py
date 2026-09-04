from engine import calc_opening, clone_data

from .registry import NodePlugin, register


@register
class OpeningReinforcement(NodePlugin):
    type = "OpeningReinforcement"
    title = "开孔补强"
    category = "通用件"
    order = 20
    inputs = [{"name": "数据", "type": "DATA"}]
    outputs = [{"name": "数据", "type": "DATA"}, {"name": "补强面积", "type": "INT"}]
    widgets = [{"key": "d", "label": "d", "step": 5, "value": "50"}]
    hint = "通用件。GB/T 150 等面积：A=d·δ。先接筒体更好"

    def execute(self, node, inputs, vault):
        data = calc_opening(clone_data(inputs), node.get("widgets") or {})
        return {"数据": data, "补强面积": data["A_open"]}

    def preview(self, pack):
        data = pack.get("数据") if isinstance(pack.get("数据"), dict) else {}
        return "补强通过" if data.get("pass_open") == "是" else "需补强圈"

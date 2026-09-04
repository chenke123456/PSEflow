from engine import calc_tubesheet, clone_data

from .registry import NodePlugin, register


@register
class HexTubesheet(NodePlugin):
    type = "HexTubesheet"
    title = "管板"
    category = "通用件"
    order = 11
    inputs = [{"name": "数据", "type": "DATA"}]
    outputs = [{"name": "数据", "type": "DATA"}, {"name": "布管圆", "type": "INT"}, {"name": "管板厚", "type": "INT"}]
    widgets = [{"key": "n_row", "label": "n_row", "step": 1}]
    hint = "通用件。换热器与再沸器都可接"

    def execute(self, node, inputs, vault):
        data = calc_tubesheet(clone_data(inputs), node.get("widgets") or {})
        return {"数据": data, "布管圆": data["Dtl"], "管板厚": data["tp"]}

    def preview(self, pack):
        return f"布管圆 {pack.get('布管圆')} mm · 板厚 {pack.get('管板厚')} mm"

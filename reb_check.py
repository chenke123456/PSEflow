from engine import calc_reb_check, clone_data

from .registry import NodePlugin, register


@register
class RebCheck(NodePlugin):
    type = "RebCheck"
    title = "校核"
    category = "理论计算"
    order = 15
    inputs = [{"name": "数据", "type": "DATA"}]
    outputs = [{"name": "数据", "type": "DATA"}]
    widgets = []
    hint = "实际面积、传热量与汽化量校核"

    def execute(self, node, inputs, vault):
        data = calc_reb_check(clone_data(inputs))
        return {"数据": data}

    def preview(self, pack):
        data = pack.get("数据") if isinstance(pack.get("数据"), dict) else {}
        return "面积通过" if data.get("pass_area") == "是" else "待校核"

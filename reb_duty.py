from engine import calc_reb_duty, clone_data

from .registry import NodePlugin, register


@register
class RebDuty(NodePlugin):
    type = "RebDuty"
    title = "再沸器热负荷"
    category = "理论计算"
    order = 7
    inputs = [{"name": "数据", "type": "DATA"}]
    outputs = [{"name": "数据", "type": "DATA"}, {"name": "热负荷", "type": "INT"}]
    widgets = []
    hint = "Q = mv·r，可加显热；并算蒸汽量"

    def execute(self, node, inputs, vault):
        data = calc_reb_duty(clone_data(inputs))
        return {"数据": data, "热负荷": data["Q_kW"]}

    def preview(self, pack):
        return f"Q={pack.get('热负荷')} kW"

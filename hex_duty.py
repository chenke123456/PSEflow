from engine import calc_hex_duty, clone_data, widget_data

from .registry import NodePlugin, register

WIDGETS = [
    {"key": "mh", "label": "热侧流量 kg/s", "step": 0.5, "value": "19"},
    {"key": "cph", "label": "热侧比热", "step": 50, "value": "2200"},
    {"key": "Thi", "label": "热侧进口 ℃", "step": 1, "value": "90"},
    {"key": "Tho", "label": "热侧出口 ℃", "step": 1, "value": "60"},
    {"key": "mc", "label": "冷侧流量 kg/s", "step": 0.5, "value": "30"},
    {"key": "cpc", "label": "冷侧比热", "step": 50, "value": "4180"},
    {"key": "Tci", "label": "冷侧进口 ℃", "step": 1, "value": "32"},
    {"key": "Tco", "label": "冷侧出口 ℃", "step": 1, "value": "42"},
]


@register
class HexDuty(NodePlugin):
    type = "HexDuty"
    title = "换热器热负荷"
    category = "理论计算"
    order = 25
    inputs = [{"name": "数据", "type": "DATA"}]
    outputs = [{"name": "数据", "type": "DATA"}, {"name": "热负荷", "type": "INT"}]
    widgets = WIDGETS
    hint = "Q = m·cp·ΔT。热侧或冷侧填一侧即可；两侧都填则用热侧"

    def execute(self, node, inputs, vault):
        data = clone_data(inputs)
        data.update(widget_data(node.get("widgets") or {}))
        data = calc_hex_duty(data)
        return {"数据": data, "热负荷": data["Q_kW"]}

    def preview(self, pack):
        return f"Q={pack.get('热负荷')} kW"

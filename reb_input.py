from engine import widget_data

from .registry import NodePlugin, register

WIDGETS = [
    {"key": "equipment", "label": "位号", "numeric": False, "value": "E-201"},
    {"key": "name", "label": "名称", "numeric": False, "value": "卧式再沸器"},
    {"key": "mv", "label": "mv", "step": 0.1, "value": "1.2"},
    {"key": "r", "label": "r", "step": 10, "value": "900"},
    {"key": "m", "label": "m", "step": 0.1, "value": "2.5"},
    {"key": "cp", "label": "cp", "step": 50, "value": "2800"},
    {"key": "Tb", "label": "Tb", "step": 1, "value": "120"},
    {"key": "Tin", "label": "Tin", "step": 1, "value": "110"},
    {"key": "Ts", "label": "Ts", "step": 1, "value": "158"},
    {"key": "rs", "label": "rs", "step": 10, "value": "2085"},
    {"key": "K", "label": "K", "step": 10, "value": "800"},
    {"key": "phi_A", "label": "φA", "step": 0.05, "value": "0.2"},
    {"key": "do", "label": "do", "step": 1, "value": "25"},
    {"key": "L", "label": "L", "step": 0.5, "value": "3"},
    {"key": "eta", "label": "η", "step": 0.05, "value": "0.7"},
    {"key": "P", "label": "P", "step": 0.1, "value": "1.6"},
    {"key": "S", "label": "S", "step": 1, "value": "137"},
    {"key": "phi", "label": "φ", "step": 0.05, "value": "0.85"},
    {"key": "C", "label": "C", "step": 0.5, "value": "1.5"},
    {"key": "Delta", "label": "Δ", "step": 0.5, "value": "3"},
    {"key": "Kp", "label": "Kp", "step": 0.05, "value": "0.4"},
]


@register
class RebInput(NodePlugin):
    type = "RebInput"
    title = "再沸器参数"
    category = "理论计算"
    order = 3
    inputs = []
    outputs = [{"name": "数据", "type": "DATA"}]
    widgets = WIDGETS
    hint = "在节点内填写再沸器已知量"

    def execute(self, node, inputs, vault):
        w = node.get("widgets") or {}
        data = {"type": "reb-input", **widget_data(w)}
        data["title"] = data.get("name") or data.get("equipment") or "再沸器"
        if not data.get("mv") or not data.get("r"):
            raise ValueError("再沸器参数：请填写 mv、r")
        return {"数据": data}

    def preview(self, pack):
        data = pack.get("数据") if isinstance(pack.get("数据"), dict) else {}
        return data.get("equipment") or "再沸器参数"

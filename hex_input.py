from engine import widget_data

from .registry import NodePlugin, register

# 只收整机已知量。折流板 / 法兰 / 开孔 / 人孔 / 支座不要放这里。
# 旧键名冻结（A, do, L, C_clean, t, n_row, Di, P, S, phi, C, Delta, Kp），只改 label、只加新字段。
WIDGETS = [
    {"key": "equipment", "label": "位号", "numeric": False, "value": "E-101"},
    {"key": "name", "label": "名称", "numeric": False, "value": "循环水冷却器"},
    {"key": "hex_style", "label": "结构型式", "numeric": False, "value": "固定管板"},
    {"key": "A", "label": "换热面积", "step": 5, "value": "80"},
    {"key": "do", "label": "管外径 mm", "step": 1, "value": "25"},
    {"key": "delta_t", "label": "管壁厚 mm", "step": 0.5, "value": "2.5"},
    {"key": "L", "label": "管长 m", "step": 0.5, "value": "6"},
    {"key": "n_pass", "label": "管程数", "step": 1, "value": "2"},
    {"key": "n_shell", "label": "壳程数", "step": 1, "value": "1"},
    {"key": "arrangement", "label": "布管", "numeric": False, "value": "正三角形"},
    {"key": "C_clean", "label": "清洗间隙 mm", "step": 0.5, "value": "3.5"},
    {"key": "t", "label": "管间距 mm", "step": 1, "value": "32"},
    {"key": "n_row", "label": "管排数", "step": 1, "value": "16"},
    {"key": "Di", "label": "壳体内径 mm", "step": 10, "value": "600"},
    {"key": "P", "label": "设计压力 MPa", "step": 0.1, "value": "1.6"},
    {"key": "Td", "label": "设计温度 ℃", "step": 5, "value": "80"},
    {"key": "S", "label": "许用应力 MPa", "step": 1, "value": "137"},
    {"key": "phi", "label": "焊缝系数", "step": 0.05, "value": "0.85"},
    {"key": "C", "label": "腐蚀余量 mm", "step": 0.5, "value": "1.5"},
    {"key": "Delta", "label": "厚度附加 mm", "step": 0.5, "value": "3"},
    {"key": "Kp", "label": "管板系数", "step": 0.05, "value": "0.4"},
    {"key": "tube_material", "label": "管材", "numeric": False, "value": "10#"},
    {"key": "shell_material", "label": "壳体材料", "numeric": False, "value": "Q345R"},
]


@register
class HexInput(NodePlugin):
    type = "HexInput"
    title = "换热器参数"
    category = "理论计算"
    order = 2
    inputs = []
    outputs = [{"name": "数据", "type": "DATA"}]
    widgets = WIDGETS
    hint = "机械已知量。必填：管外径、管长；面积可空，由换热面积节点写入"

    def execute(self, node, inputs, vault):
        w = dict(node.get("widgets") or {})
        for spec in WIDGETS:
            if spec["key"] not in w:
                w[spec["key"]] = spec.get("value", "")
        data = {"type": "hex-input", **widget_data(w)}
        data["title"] = data.get("name") or data.get("equipment") or "换热器"
        if not data.get("do") or not data.get("L"):
            raise ValueError("换热器参数：请填写管外径、管长")
        return {"数据": data}

    def preview(self, pack):
        data = pack.get("数据") if isinstance(pack.get("数据"), dict) else {}
        return f"{data.get('equipment', '')} A={data.get('A')}"

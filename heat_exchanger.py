from .registry import NodePlugin, register


@register
class HeatExchanger(NodePlugin):
    type = "HeatExchanger"
    title = "冷凝器"
    category = "物理"
    order = 33
    inputs = [
        {"name": "输入口1", "type": "公称直径"},
        {"name": "输入口2", "type": "公称直径"},
    ]
    outputs = [
        {"name": "输出口1", "type": "公称直径"},
        {"name": "输出口2", "type": "公称直径"},
    ]
    widgets = [
        {"key": "equipment", "label": "位号", "numeric": False, "value": "E-101"},
        {"key": "name", "label": "名称", "numeric": False, "value": "换热器"},
    ]
    hint = "物理目录。换热器整机，输出数据。工艺计算在理论计算。"

    def execute(self, node, inputs, vault):
        w = node.get("widgets") or {}
        equipment = str(w.get("equipment") or "").strip()
        name = str(w.get("name") or "").strip()
        return {
            "数据": {
                "equipment": equipment,
                "name": name,
                "title": name or equipment or "换热器",
                "type": "heat-exchanger",
                "frontmatter": {},
            }
        }

    def preview(self, pack):
        data = pack.get("数据") if isinstance(pack.get("数据"), dict) else {}
        return data.get("equipment") or data.get("name") or "换热器"

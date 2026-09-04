from .registry import NodePlugin, register


@register
class Tank(NodePlugin):
    type = "Tank"
    title = "罐子"
    category = "物理"
    order = 31
    inputs = []
    outputs = [{"name": "数据", "type": "DATA"}]
    widgets = [
        {"key": "equipment", "label": "位号", "numeric": False, "value": "V-101"},
        {"key": "name", "label": "名称", "numeric": False, "value": "储罐"},
    ]
    hint = "物理目录。罐子已知量，输出数据。"

    def execute(self, node, inputs, vault):
        w = node.get("widgets") or {}
        equipment = str(w.get("equipment") or "").strip()
        name = str(w.get("name") or "").strip()
        return {
            "数据": {
                "equipment": equipment,
                "name": name,
                "title": name or equipment or "罐子",
                "type": "tank",
                "frontmatter": {},
            }
        }

    def preview(self, pack):
        data = pack.get("数据") if isinstance(pack.get("数据"), dict) else {}
        return data.get("equipment") or data.get("name") or "罐子"

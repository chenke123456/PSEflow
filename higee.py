from .registry import NodePlugin, register


@register
class Higee(NodePlugin):
    type = "Higee"
    title = "超重力精馏机"
    category = "物理"
    order = 32
    inputs = [
        {"name": "输入口1", "type": "公称直径"},
        {"name": "输入口2", "type": "公称直径"},
        {"name": "输入口3", "type": "公称直径"},
        {"name": "输入口4", "type": "公称直径"},
    ]
    outputs = [
        {"name": "输出口1", "type": "公称直径"},
        {"name": "输出口2", "type": "公称直径"},
    ]
    widgets = [
        {"key": "equipment", "label": "位号", "numeric": False, "value": "C-101"},
        {"key": "name", "label": "名称", "numeric": False, "value": "超重力精馏机"},
    ]
    hint = "物理目录。超重力精馏机已知量，输出数据。"

    def execute(self, node, inputs, vault):
        w = node.get("widgets") or {}
        equipment = str(w.get("equipment") or "").strip()
        name = str(w.get("name") or "").strip()
        return {
            "数据": {
                "equipment": equipment,
                "name": name,
                "title": name or equipment or "超重力精馏机",
                "type": "higee",
                "frontmatter": {},
            }
        }

    def preview(self, pack):
        data = pack.get("数据") if isinstance(pack.get("数据"), dict) else {}
        return data.get("equipment") or data.get("name") or "超重力精馏机"

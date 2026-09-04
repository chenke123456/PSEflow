from .registry import NodePlugin, register


@register
class Reboiler(NodePlugin):
    type = "Reboiler"
    title = "再沸器"
    category = "物理"
    order = 34
    inputs = [
        {"name": "输入口1", "type": "公称直径"},
    ]
    outputs = [{"name": "输出口1", "type": "公称直径"}]
    widgets = [
        {"key": "equipment", "label": "位号", "numeric": False, "value": "E-201"},
        {"key": "name", "label": "名称", "numeric": False, "value": "再沸器"},
    ]
    hint = "物理目录。再沸器整机，输出数据。工艺计算在理论计算。"

    def execute(self, node, inputs, vault):
        w = node.get("widgets") or {}
        equipment = str(w.get("equipment") or "").strip()
        name = str(w.get("name") or "").strip()
        return {
            "数据": {
                "equipment": equipment,
                "name": name,
                "title": name or equipment or "再沸器",
                "type": "reboiler",
                "frontmatter": {},
            }
        }

    def preview(self, pack):
        data = pack.get("数据") if isinstance(pack.get("数据"), dict) else {}
        return data.get("equipment") or data.get("name") or "再沸器"

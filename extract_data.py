from engine import as_text, build_note_payload

from .registry import NodePlugin, register


@register
class ExtractData(NodePlugin):
    type = "ExtractData"
    title = "获取数据"
    category = "数据"
    order = 6
    inputs = [{"name": "文本", "type": "STRING"}]
    outputs = [{"name": "数据", "type": "DATA"}]
    widgets = []
    hint = "解析标题、正文、frontmatter、占位符"

    def execute(self, node, inputs, vault):
        text = as_text(inputs.get("文本"))
        if not str(text).strip():
            raise ValueError("获取数据失败：请先连接「加载笔记」")
        return {"数据": build_note_payload("", text)}

    def preview(self, pack):
        data = pack.get("数据") if isinstance(pack.get("数据"), dict) else {}
        return f"{data.get('equipment') or data.get('title', '')} A={data.get('A')}"

from .registry import NodePlugin, register


@register
class CurrentNote(NodePlugin):
    type = "CurrentNote"
    title = "最近笔记"
    category = "数据"
    order = 4
    inputs = []
    outputs = [{"name": "文本", "type": "STRING"}]
    widgets = []
    hint = "读取库中最近修改的 Markdown"

    def execute(self, node, inputs, vault):
        latest = vault.latest_markdown()
        if not latest:
            raise ValueError("库里没有 Markdown")
        text = latest.read_text(encoding="utf-8")
        return {"文本": text}

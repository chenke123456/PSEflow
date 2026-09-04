from engine import preview_of

from .registry import NodePlugin, register


@register
class LoadNote(NodePlugin):
    type = "LoadNote"
    title = "加载笔记"
    category = "数据"
    order = 5
    inputs = []
    outputs = [{"name": "文本", "type": "STRING"}]
    widgets = [{"key": "path", "label": "路径", "numeric": False}]
    hint = "按路径读取笔记"

    def execute(self, node, inputs, vault):
        w = node.get("widgets") or {}
        rel = str(w.get("path") or "").strip()
        if not rel:
            raise ValueError("请填写笔记路径")
        rel, text = vault.read_text(rel)
        if not text.strip():
            raise ValueError("笔记没有内容：" + rel)
        return {"文本": text}

    def preview(self, pack):
        return preview_of(pack.get("文本"))

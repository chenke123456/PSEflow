from engine import preview_of

from .registry import NodePlugin, register


@register
class TemplateFolder(NodePlugin):
    type = "TemplateFolder"
    title = "模板文件夹"
    category = "模板"
    order = 0
    inputs = []
    outputs = [{"name": "模板", "type": "TEMPLATE"}, {"name": "列表", "type": "STRING"}]
    widgets = [
        {"key": "folder", "label": "目录", "numeric": False, "value": "模板"},
        {"key": "file", "label": "文件", "numeric": False, "value": "换热器/计算方案.md"},
    ]
    hint = "从模板文件夹读取方案骨架"

    def execute(self, node, inputs, vault):
        w = node.get("widgets") or {}
        folder = str(w.get("folder") or "模板").replace("\\", "/").rstrip("/")
        files = vault.list_markdown(folder)
        if not files:
            raise ValueError("模板文件夹是空的：" + folder)
        hit = vault.pick_template(folder, str(w.get("file") or "").strip())
        if not hit:
            raise ValueError("模板文件夹里没有可用的 .md：" + folder)
        text = hit.read_text(encoding="utf-8")
        if not text.strip():
            raise ValueError("模板是空的：" + vault.rel(hit))
        return {"模板": text, "列表": "\n".join(vault.rel(f) for f in files)}

    def preview(self, pack):
        return preview_of(pack.get("列表"))

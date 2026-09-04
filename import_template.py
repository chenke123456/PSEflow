from engine import build_note_payload, preview_of

from .registry import NodePlugin, register


@register
class ImportTemplate(NodePlugin):
    type = "ImportTemplate"
    title = "导入模板"
    category = "模板"
    order = 1
    inputs = []
    outputs = [{"name": "模板", "type": "TEMPLATE"}, {"name": "数据", "type": "DATA"}]
    widgets = [{"key": "path", "label": "路径", "numeric": False}]
    hint = "读取指定模板原文"

    def execute(self, node, inputs, vault):
        w = node.get("widgets") or {}
        rel = str(w.get("path") or "").strip() or "模板/换热器/计算方案.md"
        rel, text = vault.read_text(rel)
        data = build_note_payload(rel, text)
        data["templatePath"] = rel
        data["templateName"] = data["basename"]
        if not text.strip():
            raise ValueError("导入的模板是空的：" + rel)
        return {"模板": text, "数据": data}

    def preview(self, pack):
        return preview_of(pack.get("模板"))

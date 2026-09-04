from engine import render_preview_html

from .registry import NodePlugin, register


@register
class Preview(NodePlugin):
    type = "Preview"
    title = "预览"
    category = "导出"
    order = 17
    inputs = [{"name": "数据", "type": "ANY"}]
    outputs = []
    widgets = []
    hint = "把上游结果做成表格显示"

    def execute(self, node, inputs, vault):
        return {"_html": render_preview_html(inputs.get("数据"))}

    def preview(self, pack):
        return "预览"

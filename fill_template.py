from engine import clone_data, fill_scheme, preview_of, stamp_time

from .registry import NodePlugin, register


@register
class FillTemplate(NodePlugin):
    type = "FillTemplate"
    title = "填充模板"
    category = "计算"
    order = 16
    inputs = [{"name": "模板", "type": "TEMPLATE"}, {"name": "数据", "type": "DATA"}]
    outputs = [{"name": "正文", "type": "STRING"}, {"name": "数据", "type": "DATA"}]
    widgets = []
    hint = "把计算结果填进方案骨架"

    def execute(self, node, inputs, vault):
        data = stamp_time(clone_data(inputs))
        return {"正文": fill_scheme(inputs.get("模板"), data), "数据": data}

    def preview(self, pack):
        return preview_of(pack.get("正文"))

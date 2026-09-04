from engine import calc_shell, clone_data

from .registry import NodePlugin, register


@register
class HexShell(NodePlugin):
    type = "HexShell"
    title = "筒体"
    category = "通用件"
    order = 12
    inputs = [{"name": "数据", "type": "DATA"}]
    outputs = [{"name": "数据", "type": "DATA"}, {"name": "壁厚", "type": "INT"}]
    widgets = []
    hint = "通用件。圆筒壁厚，GB/T 150"

    def execute(self, node, inputs, vault):
        data = calc_shell(clone_data(inputs))
        return {"数据": data, "壁厚": data["t_shell"]}

    def preview(self, pack):
        return f"壁厚 {pack.get('壁厚')} mm"

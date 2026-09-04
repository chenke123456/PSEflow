from .registry import NodePlugin, register
from ._dn import pass_dn, port_dn


@register
class Pipe(NodePlugin):
    type = "Pipe"
    title = "管道"
    category = "物理"
    order = 19
    inputs = [{"name": "输入口", "type": "公称直径"}]
    outputs = [{"name": "输出口", "type": "公称直径"}]
    widgets = []
    hint = "输入口进公称直径，输出口原样传出。管内不要填 DN。"

    def execute(self, node, inputs, vault):
        dn = port_dn(inputs)
        if dn is None:
            raise ValueError("管道：请把公称直径连到输入口")
        return {"输出口": pass_dn(dn)}

    def preview(self, pack):
        n = pack.get("输出口")
        return f"DN{n}" if n is not None else "管道"

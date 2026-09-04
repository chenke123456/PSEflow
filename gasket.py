from engine import calc_gasket, take_data

from .registry import NodePlugin, register
from ._dn import pass_dn, port_dn


@register
class Gasket(NodePlugin):
    type = "Gasket"
    title = "垫片"
    category = "物理"
    order = 23
    inputs = [
        {"name": "输入口", "type": "公称直径"},
    ]
    outputs = [
        {"name": "输出口", "type": "公称直径"},
    ]
    widgets = [{"key": "PN", "label": "PN", "step": 0.2, "value": "1.6"}]
    hint = "输入口/输出口传公称直径。PN 在胶囊上填。上游数据可选。查 HG/T 20606"

    def execute(self, node, inputs, vault):
        w = dict(node.get("widgets") or {})
        dn = port_dn(inputs)
        if dn is None:
            raise ValueError("垫片：请把公称直径连到输入口")
        w["DN"] = dn
        return {
            "输出口": pass_dn(dn),
            "数据": calc_gasket(take_data(inputs), w),
        }

    def preview(self, pack):
        data = pack.get("数据") if isinstance(pack.get("数据"), dict) else {}
        name = data.get("gasket_name") or "垫片"
        n = pack.get("输出口")
        return f"{name} DN{n}" if n is not None else name

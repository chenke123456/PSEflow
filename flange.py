from engine import calc_flange, pn16_plate_flange_table, take_data

from .registry import NodePlugin, register
from ._dn import pass_dn, port_dn


@register
class Flange(NodePlugin):
    type = "Flange"
    title = "法兰"
    category = "物理"
    order = 19
    inputs = [{"name": "输入口", "type": "公称直径"}]
    outputs = [
        {"name": "输出口", "type": "公称直径"},
        {"name": "公称压力", "type": "INT"},
        {"name": "螺栓数", "type": "INT"},
        {"name": "尺寸", "type": "TABLE"},
    ]
    widgets = [
        {"key": "PN", "label": "PN", "step": 0.2, "value": "1.6"},
        {"key": "kind", "label": "型式", "numeric": False, "value": "板式平焊"},
        {"key": "face", "label": "密封面", "numeric": False, "value": "突面 RF"},
    ]
    hint = "输入口/输出口传公称直径。PN16 板式平焊按表 8.2.1-4 出尺寸。PN、型式、密封面在胶囊上填。"

    def execute(self, node, inputs, vault):
        w = dict(node.get("widgets") or {})
        dn = port_dn(inputs)
        if dn is None:
            raise ValueError("法兰：请把公称直径连到输入口")
        w["DN"] = dn
        data = calc_flange(take_data(inputs), w)
        table = pn16_plate_flange_table(int(round(dn))) if data.get("flange_D") is not None else {
            "columns": [],
            "rows": [],
        }
        out = pass_dn(dn)
        return {
            "输出口": out,
            "数据": data,
            "公称压力": data["PN"],
            "螺栓数": data["bolt_count"],
            "尺寸": table,
        }

    def preview(self, pack):
        data = pack.get("数据") if isinstance(pack.get("数据"), dict) else {}
        d = data.get("flange_D")
        extra = f" D{d}" if d is not None else ""
        return f"公称直径 {pack.get('输出口')} PN{pack.get('公称压力')}{extra} {pack.get('螺栓数')} 栓"

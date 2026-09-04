from __future__ import annotations

import json
import math
import re
from copy import deepcopy
from datetime import datetime


PITCH = {10: 15, 14: 20, 16: 23.5, 19: 28.5, 25: 36, 32: 45}


def as_text(v) -> str:
    if v is None:
        return ""
    if isinstance(v, (str, int, float, bool)):
        return str(v)
    try:
        return json.dumps(v, ensure_ascii=False, indent=2)
    except TypeError:
        return str(v)


def preview_of(v, limit: int = 88) -> str:
    s = re.sub(r"\s+", " ", as_text(v)).strip()
    if not s:
        return "(空)"
    return s[:limit] + "…" if len(s) > limit else s


def parse_frontmatter(text: str) -> tuple[dict, str]:
    src = text or ""
    m = re.match(r"^---\r?\n([\s\S]*?)\r?\n---\r?\n?", src)
    fm: dict = {}
    if not m:
        return fm, src
    for line in m.group(1).splitlines():
        kv = re.match(r"^([A-Za-z0-9_\u4e00-\u9fff-]+)\s*:\s*(.*)$", line)
        if not kv:
            continue
        val = kv.group(2).strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        if re.fullmatch(r"-?\d+(\.\d+)?", val):
            val = float(val) if "." in val else int(val)
        fm[kv.group(1)] = val
    return fm, src[m.end() :]


def find_placeholders(text: str) -> list[str]:
    keys: list[str] = []
    for m in re.finditer(r"\{\{\s*([\w.\u4e00-\u9fff]+)\s*\}\}", text or ""):
        if m.group(1) not in keys:
            keys.append(m.group(1))
    return keys


def get_path(obj, key: str):
    if not isinstance(obj, dict):
        return ""
    if key in obj and obj[key] is not None:
        return obj[key]
    cur = obj
    for part in str(key).split("."):
        if not isinstance(cur, dict):
            return ""
        if part in cur:
            cur = cur[part]
        elif isinstance(cur.get("frontmatter"), dict) and part in cur["frontmatter"]:
            cur = cur["frontmatter"][part]
        else:
            return ""
    return "" if cur is None else cur


def render_template(tpl: str, data: dict) -> str:
    return re.sub(r"\{\{\s*([\w.\u4e00-\u9fff]+)\s*\}\}", lambda m: as_text(get_path(data, m.group(1))), tpl or "")


def num(data: dict, key: str, fallback=0.0):
    v = data.get(key)
    if v is None and isinstance(data.get("frontmatter"), dict):
        v = data["frontmatter"].get(key)
    try:
        n = float(v)
    except (TypeError, ValueError):
        return fallback
    return n if math.isfinite(n) else fallback


def _is_num(data: dict, key: str) -> bool:
    v = data.get(key)
    if v is None and isinstance(data.get("frontmatter"), dict):
        v = data["frontmatter"].get(key)
    try:
        return math.isfinite(float(v))
    except (TypeError, ValueError):
        return False


def widget_num(w: dict, key: str):
    if not w or w.get(key) is None or str(w.get(key)).strip() == "":
        return None
    try:
        n = float(w[key])
    except (TypeError, ValueError):
        return None
    return n if math.isfinite(n) else None


def widget_data(w: dict) -> dict:
    data = {}
    for key, raw in (w or {}).items():
        s = str("" if raw is None else raw).strip()
        if not s:
            continue
        data[key] = float(s) if re.fullmatch(r"-?\d+\.\d+", s) else (int(s) if re.fullmatch(r"-?\d+", s) else s)
    return data


_FIELD_PAIR = re.compile(r"([A-Za-z_][\w]*)\s*[:=]\s*([^\s,;]+)")
_SKIP_INPUT_KEYS = {"type", "frontmatter", "fm", "fields", "_html"}


def parse_fields_line(text: str) -> dict:
    found = {}
    for m in _FIELD_PAIR.finditer(text or ""):
        key = m.group(1)
        if key in _SKIP_INPUT_KEYS or re.fullmatch(r"[kv]\d+", key):
            continue
        found.update(widget_data({key: m.group(2)}))
    return found


def pair_fields(w: dict, n: int = 8) -> dict:
    data = {}
    src = w or {}
    for i in range(1, n + 1):
        key = str(src.get(f"k{i}") or "").strip()
        val = str(src.get(f"v{i}") or "").strip()
        if not key or not val or key in _SKIP_INPUT_KEYS or re.fullmatch(r"[kv]\d+", key):
            continue
        data.update(widget_data({key: val}))
    return data


def as_j_per_kg(x) -> float:
    try:
        n = float(x)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(n) or n <= 0:
        return 0.0
    return n * 1000 if n < 50000 else n


def stamp_time(data: dict) -> dict:
    now = datetime.now()
    data.setdefault("date", now.strftime("%Y-%m-%d"))
    data.setdefault("time", now.strftime("%H:%M"))
    data.setdefault("datetime", now.strftime("%Y-%m-%d %H:%M"))
    return data


def build_note_payload(rel: str, text: str) -> dict:
    fm, body = parse_frontmatter(text)
    heading = None
    for line in body.splitlines():
        if line.startswith("# "):
            heading = line[2:].strip()
            break
    title = fm.get("title") or fm.get("name") or heading or (rel.rsplit("/", 1)[-1].removesuffix(".md") if rel else "未命名")
    folder = rel.rsplit("/", 1)[0] if rel and "/" in rel else ""
    basename = rel.rsplit("/", 1)[-1].removesuffix(".md") if rel else title
    data = {
        "path": rel,
        "basename": basename,
        "folder": folder,
        "title": title,
        "body": body,
        "content": text,
        "frontmatter": fm,
        "fm": fm,
        "placeholders": find_placeholders(text),
    }
    reserved = set(data)
    for key, val in fm.items():
        if key not in reserved:
            data[key] = val
    return stamp_time(data)


def pitch_of(do_mm: float) -> float:
    return PITCH.get(int(do_mm), round(do_mm * 1.3))


def baffle_thk(di: float) -> float:
    if di < 400:
        return 3.5
    if di <= 700:
        return 4.5
    if di <= 1000:
        return 7
    return 9


def rnd(x, n=2):
    return round(float(x), n) if isinstance(x, (int, float)) and math.isfinite(x) else x


def clone_data(inputs: dict) -> dict:
    src = inputs.get("数据")
    if not isinstance(src, dict):
        raise ValueError("请把上游「数据」连到本节点")
    data = deepcopy(src)
    data["frontmatter"] = deepcopy(src.get("frontmatter") or {})
    return data


def take_data(inputs: dict) -> dict:
    src = inputs.get("数据")
    if isinstance(src, dict):
        data = deepcopy(src)
        data["frontmatter"] = deepcopy(src.get("frontmatter") or {})
        return data
    return {"frontmatter": {}}


def calc_tubes(data: dict, w: dict) -> dict:
    a = num(data, "A", 0)
    do_mm = num(data, "do", 0)
    length = num(data, "L", 0)
    if not a or not do_mm or not length:
        raise ValueError("换热管：输入缺少 A / do / L")
    c_clean = num(data, "C_clean", 3)
    n_raw = a / (math.pi * (do_mm / 1000) * length)
    n_force = widget_num(w, "N")
    n = math.ceil(n_force) if n_force is not None else math.ceil(n_raw)
    t_min = do_mm + 2 * c_clean
    auto_t = max(t_min, pitch_of(do_mm))
    t_force = widget_num(w, "t")
    t = t_force if t_force is not None else num(data, "t", auto_t)
    data.update(
        {
            "N": n,
            "N_raw": rnd(n_raw, 2),
            "t_min": rnd(t_min, 1),
            "t": rnd(t, 1),
            "Pt": rnd(1.25 * do_mm, 1),
            "formula": "math/换热器公式.md",
        }
    )
    return data


def calc_tubesheet(data: dict, w: dict) -> dict:
    n = num(data, "N", 0)
    do_mm = num(data, "do", 0)
    t = num(data, "t", 0)
    if not n or not do_mm or not t:
        raise ValueError("管板：请先连接「换热管」")
    di = num(data, "Di", 0)
    p = num(data, "P", 1.6)
    s = num(data, "S", 137)
    phi = num(data, "phi", 1)
    delta = num(data, "Delta", 3)
    kp = num(data, "Kp", 0.4)
    n_row = widget_num(w, "n_row")
    if n_row is None:
        n_row = num(data, "n_row", 0)
    if not n_row:
        n_row = max(2, math.ceil(math.sqrt(n * 1.15)))
    dtl = t * (n_row - 1) + do_mm
    do_ts = (di or dtl) + 2 * delta
    tp = dtl * math.sqrt((kp * p) / (s * phi))
    a_bundle = (math.pi * dtl * dtl) / 4
    a_eff = a_bundle - (n * math.pi * do_mm * do_mm) / 4
    eta_tp = ((n * do_mm * do_mm) / (dtl * dtl)) * 100
    data.update(
        {
            "n_row": n_row,
            "n_c": n_row,
            "Dtl": rnd(dtl, 1),
            "Do_ts": rnd(do_ts, 1),
            "tp": rnd(tp, 2),
            "A_bundle": rnd(a_bundle, 0),
            "A_eff": rnd(a_eff, 0),
            "eta_tp": rnd(eta_tp, 1),
        }
    )
    return data


def calc_shell(data: dict) -> dict:
    di = num(data, "Di", 0)
    if not di:
        raise ValueError("壳体：输入缺少 Di")
    p = num(data, "P", 1.6)
    s = num(data, "S", 137)
    phi = num(data, "phi", 1)
    c = num(data, "C", 1.5)
    delta = num(data, "Delta", 3)
    t1 = (p * di) / (2 * s * phi - p)
    t2 = (p * di) / (4 * s * phi + 0.8 * p)
    t_shell = max(t1, t2)
    data.update(
        {
            "t1": rnd(t1, 2),
            "t2": rnd(t2, 2),
            "t_shell": rnd(t_shell, 2),
            "delta_nom": rnd(t_shell + c + delta, 2),
        }
    )
    return data


def calc_head(data: dict, w: dict) -> dict:
    di = num(data, "Di", 0)
    if not di:
        raise ValueError("封头：输入缺少 Di")
    p = num(data, "P", 1.6)
    s = num(data, "S", 137)
    phi = num(data, "phi", 1)
    k = widget_num(w, "K")
    k = 1 if k is None else k
    t_head = (k * p * di) / (2 * s * phi - 0.5 * p)
    data.update({"K_head": k, "t_head": rnd(t_head, 2)})
    return data


_PN_GRADES = (0.25, 0.6, 1.0, 1.6, 2.5, 4.0, 6.4)
_DN_GRADES = (
    10, 15, 20, 25, 32, 40, 50, 65, 80, 100, 125, 150, 200, 250,
    300, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000,
)


# 表 8.2.1-4 PN16 板式平焊钢制管法兰，mm。
# A1_A, A1_B, D, K, L, n, Th, C, B1_A, B1_B, b
_PN16_PLATE_FLANGE = {
    10: (17.2, 14, 90, 60, 14, 4, "M12", 14, 18, 15, 4),
    15: (21.3, 18, 95, 65, 14, 4, "M12", 14, 22.5, 19, 4),
    20: (26.9, 25, 105, 75, 14, 4, "M12", 16, 27.5, 26, 4),
    25: (33.7, 32, 115, 85, 14, 4, "M12", 16, 34.5, 33, 5),
    32: (42.4, 38, 140, 100, 18, 4, "M16", 18, 43.5, 39, 5),
    40: (48.3, 45, 150, 110, 18, 4, "M16", 18, 49.5, 46, 5),
    50: (60.3, 57, 165, 125, 18, 4, "M16", 19, 61.5, 59, 5),
    65: (76.1, 76, 185, 145, 18, 8, "M16", 20, 77.5, 78, 6),
    80: (88.9, 89, 200, 160, 18, 8, "M16", 20, 90.5, 91, 6),
    100: (114.3, 108, 220, 180, 18, 8, "M16", 22, 116, 110, 6),
    125: (139.7, 133, 250, 210, 18, 8, "M16", 22, 143.5, 135, 6),
    150: (168.3, 159, 285, 240, 22, 8, "M20", 24, 170.5, 161, 6),
    200: (219.1, 219, 340, 295, 22, 12, "M20", 26, 221.5, 222, 8),
    250: (273, 273, 405, 355, 26, 12, "M24", 29, 276.5, 276, 10),
    300: (323.9, 325, 460, 410, 26, 12, "M24", 32, 328, 328, 11),
    350: (355.6, 377, 520, 470, 26, 16, "M24", 35, 360, 381, 12),
    400: (406.4, 426, 580, 525, 30, 16, "M27", 38, 411, 430, 12),
    450: (457, 480, 640, 585, 30, 20, "M27", 42, 462, 485, 12),
    500: (508, 530, 715, 650, 33, 20, "M30", 46, 513.5, 535, 12),
    600: (610, 630, 840, 770, 33, 20, "M30", 52, 616.5, 636, 12),
}


def lookup_pn16_plate_flange(dn: int) -> dict | None:
    row = _PN16_PLATE_FLANGE.get(int(dn))
    if not row:
        return None
    a1_a, a1_b, d, k, l, n, th, c, b1_a, b1_b, b = row
    return {
        "flange_A1_A": a1_a,
        "flange_A1_B": a1_b,
        "flange_D": d,
        "flange_K": k,
        "flange_L": l,
        "flange_C": c,
        "flange_B1_A": b1_a,
        "flange_B1_B": b1_b,
        "flange_b": b,
        "bolt_count": n,
        "bolt_size": th,
        "nut_qty": n * 2,
        "flange_table": "表 8.2.1-4 PN16 板式平焊钢制管法兰",
    }


def pn16_plate_flange_table(dn: int) -> dict:
    cols = [
        "公称尺寸 DN",
        "钢管外径 A₁A",
        "钢管外径 A₁B",
        "法兰外径 D",
        "螺栓孔中心圆直径 K",
        "螺栓孔直径 L",
        "螺栓孔数量 n",
        "螺栓 Th",
        "法兰厚度 C",
        "法兰内径 B₁A",
        "法兰内径 B₁B",
        "坡口宽度 b",
    ]
    row = _PN16_PLATE_FLANGE.get(int(dn))
    if not row:
        return {"columns": cols, "rows": []}
    return {"columns": cols, "rows": [[int(dn), *row]]}


def calc_flange(data: dict, w: dict) -> dict:
    dn = widget_num(w, "DN")
    pn = widget_num(w, "PN")
    if pn is None:
        pn = num(data, "PN", 0)
    if not dn or not pn:
        raise ValueError("法兰：请填写公称直径、公称压力")
    kind = str(w.get("kind") or data.get("flange_kind") or "板式平焊").strip()
    face = str(w.get("face") or data.get("flange_face") or "突面 RF").strip()
    spec = _lookup_joint(dn, pn)
    data.update(
        {
            "PN": pn,
            "flange_std": "HG/T 20592",
            "flange_face": face,
            "flange_kind": kind,
            "bolt_count": spec.bolt_count,
            "bolt_size": spec.bolt_size,
            "nut_qty": spec.bolt_count * 2,
            "gasket_name": spec.gasket_name,
            "gasket_std": "HG/T 20606",
            "gasket_remark": spec.remark or "",
            "fastener_std": "HG/T 20592",
            "fastener_remark": spec.remark or "",
        }
    )
    if _pn_code(pn) == 16 and "板式平焊" in kind:
        dim = lookup_pn16_plate_flange(int(dn))
        if not dim:
            raise ValueError("法兰：表 8.2.1-4 PN16 板式平焊无此公称直径")
        data.update(dim)
    return data


def _pn_code(pn: float) -> int:
    if pn >= 6:
        return int(round(pn))
    return int(round(pn * 10))


def _lookup_joint(dn, pn):
    import sys
    from pathlib import Path

    root = str(Path(__file__).resolve().parent.parent)
    if root not in sys.path:
        sys.path.insert(0, root)
    from piping_mto.data.flange_bolts_hgt20592 import lookup_flange_joint

    return lookup_flange_joint(int(dn), _pn_code(pn))


def _need_dn_pn(data: dict, w: dict) -> tuple[int, float]:
    dn = widget_num(w, "DN")
    if dn is None:
        dn = num(data, "DN", 0)
    pn = widget_num(w, "PN")
    if pn is None:
        pn = num(data, "PN", 0)
    if not dn or not pn:
        raise ValueError("请填写法兰型号 DN、PN")
    return int(dn), pn


def calc_opening(data: dict, w: dict) -> dict:
    di = num(data, "Di", 0)
    p = num(data, "P", 0)
    s = num(data, "S", 137)
    phi = num(data, "phi", 1)
    c = num(data, "C", 1.5)
    if not di or not p:
        raise ValueError("开孔补强：输入缺少 Di / P")
    d = widget_num(w, "d")
    if d is None:
        d = num(data, "d_open", 0)
    if not d:
        raise ValueError("开孔补强：请填写开孔直径 d")
    delta = num(data, "t_shell", 0)
    if not delta:
        denom = 2 * s * phi - p
        if denom <= 0:
            raise ValueError("开孔补强：2Sφ−P 不成立")
        delta = (p * di) / denom
    delta_n = num(data, "delta_nom", 0) or (delta + c + num(data, "Delta", 3))
    d_max = min(di / 2, 520) if di <= 1500 else min(di / 3, 1000)
    area = d * delta
    extra = max(0.0, (delta_n - delta - c) * (d + 2 * delta_n))
    area_pad = max(0.0, area - extra)
    t_pad = delta_n
    w_pad = area_pad / t_pad if t_pad else 0
    data.update(
        {
            "d_open": rnd(d, 1),
            "d_open_max": rnd(d_max, 1),
            "A_open": rnd(area, 1),
            "A_open_shell": rnd(extra, 1),
            "A_pad": rnd(area_pad, 1),
            "t_pad": rnd(t_pad, 2),
            "w_pad": rnd(w_pad, 1),
            "pass_open": "是" if extra >= area else "否",
            "pass_open_size": "是" if d <= d_max else "否",
        }
    )
    return data


def calc_manhole(data: dict, w: dict) -> dict:
    di = num(data, "Di", 0)
    if not di:
        raise ValueError("人孔：输入缺少 Di")
    dn_w = widget_num(w, "DN")
    dn = int(dn_w) if dn_w is not None else (400 if di < 1000 else 450)
    kind = str(w.get("kind") or data.get("manhole_kind") or "回转盖人孔").strip()
    p = num(data, "P", 0)
    pn = num(data, "PN", 0)
    if not pn and p:
        pn = next((x for x in _PN_GRADES if p <= x), _PN_GRADES[-1])
    data.update(
        {
            "manhole_dn": dn,
            "manhole_kind": kind,
            "manhole_std": "HG/T 21514",
            "manhole_pn": pn or "",
        }
    )
    return data


def calc_support(data: dict, w: dict) -> dict:
    di = num(data, "Di", 0)
    if not di:
        raise ValueError("支座：输入缺少 Di")
    kind = str(w.get("kind") or data.get("support_kind") or "鞍式").strip()
    n_w = widget_num(w, "n")
    n = int(n_w) if n_w is not None else 2
    b = 0.1 * di
    data.update(
        {
            "support_kind": kind,
            "support_std": "NB/T 47065",
            "saddle_n": n,
            "saddle_b": rnd(b, 1),
        }
    )
    return data


def calc_gasket(data: dict, w: dict) -> dict:
    dn, pn = _need_dn_pn(data, w)
    spec = _lookup_joint(dn, pn)
    data.update(
        {
            "gasket_name": spec.gasket_name,
            "gasket_std": "HG/T 20606",
            "gasket_remark": spec.remark or "",
        }
    )
    return data


def calc_fastener(data: dict, w: dict) -> dict:
    dn, pn = _need_dn_pn(data, w)
    spec = _lookup_joint(dn, pn)
    data.update(
        {
            "bolt_count": spec.bolt_count,
            "bolt_size": spec.bolt_size,
            "nut_qty": spec.bolt_count * 2,
            "fastener_std": "HG/T 20592",
            "fastener_remark": spec.remark or "",
        }
    )
    return data


def calc_baffle(data: dict, w: dict) -> dict:
    di = num(data, "Di", 0)
    length = num(data, "L", 0)
    do_mm = num(data, "do", 0)
    if not di or not length:
        raise ValueError("折流板：输入缺少 Di / L")
    b_ratio = widget_num(w, "B_ratio")
    h_ratio = widget_num(w, "h_ratio")
    b_ratio = 0.4 if b_ratio is None else b_ratio
    h_ratio = 0.25 if h_ratio is None else h_ratio
    n_c = num(data, "n_c", num(data, "n_row", 0))
    b = b_ratio * di
    h_baffle = h_ratio * di
    delta_b = baffle_thk(di)
    nb = max(0, round((length * 1000) / b - 1)) if b else 0
    a_s = b * (di - n_c * do_mm)
    data.update(
        {
            "B_ratio": b_ratio,
            "h_ratio": h_ratio,
            "B": rnd(b, 1),
            "h_baffle": rnd(h_baffle, 1),
            "delta_b": rnd(delta_b, 1),
            "NB": nb,
            "As": rnd(a_s, 0),
        }
    )
    return data


def calc_hex_duty(data: dict) -> dict:
    mh = num(data, "mh", 0)
    cph = num(data, "cph", 0)
    thi = num(data, "Thi", 0)
    tho = num(data, "Tho", 0)
    mc = num(data, "mc", 0)
    cpc = num(data, "cpc", 0)
    tci = num(data, "Tci", 0)
    tco = num(data, "Tco", 0)
    q_h = mh * cph * (thi - tho) if mh and cph else 0
    q_c = mc * cpc * (tco - tci) if mc and cpc else 0
    if q_h < 0:
        raise ValueError("热负荷：热侧进口温度应高于出口")
    if q_c < 0:
        raise ValueError("热负荷：冷侧出口温度应高于进口")
    if not q_h and not q_c:
        raise ValueError("热负荷：请填写热侧或冷侧的流量、比热、进出口温度")
    q = q_h if q_h else q_c
    data.update(
        {
            "Q_h": rnd(q_h, 0),
            "Q_c": rnd(q_c, 0),
            "Q": rnd(q, 0),
            "Q_kW": rnd(q / 1000, 2),
        }
    )
    return data


def calc_hex_area(data: dict) -> dict:
    q = num(data, "Q", 0)
    k = num(data, "K", 0)
    if not q or not k:
        raise ValueError("换热面积：请先算热负荷，并填写总传热系数 K")
    thi = num(data, "Thi", 0)
    tho = num(data, "Tho", 0)
    tci = num(data, "Tci", 0)
    tco = num(data, "Tco", 0)
    if not all(_is_num(data, k) for k in ("Thi", "Tho", "Tci", "Tco")):
        raise ValueError("换热面积：请填写热侧、冷侧进出口温度")
    flow = str(data.get("flow") or "逆流").strip() or "逆流"
    if "并" in flow:
        dt1 = thi - tci
        dt2 = tho - tco
    else:
        dt1 = thi - tco
        dt2 = tho - tci
    if dt1 <= 0 or dt2 <= 0:
        raise ValueError("换热面积：对数温差非正，请检查四路温度或改逆流")
    dtm = dt1 if abs(dt1 - dt2) < 1e-9 else (dt1 - dt2) / math.log(dt1 / dt2)
    a_req = q / (k * dtm)
    phi_a = num(data, "phi_A", 0.2)
    ad = (1 + phi_a) * a_req
    data.update(
        {
            "flow": flow,
            "dT1": rnd(dt1, 2),
            "dT2": rnd(dt2, 2),
            "dTm": rnd(dtm, 2),
            "A_req": rnd(a_req, 2),
            "Ad": rnd(ad, 2),
            "A": rnd(ad, 2),
            "phi_A": phi_a,
        }
    )
    return data


def calc_reb_duty(data: dict) -> dict:
    mv = num(data, "mv", 0)
    r = as_j_per_kg(num(data, "r", 0))
    if not mv or not r:
        raise ValueError("热负荷：请填写汽化量 mv 和潜热 r")
    m = num(data, "m", 0)
    cp = num(data, "cp", 0)
    tb = num(data, "Tb", 0)
    tin = num(data, "Tin", tb)
    q_lat = mv * r
    q_sens = m * cp * (tb - tin) if m and cp else 0
    q = q_lat + q_sens
    rs = as_j_per_kg(num(data, "rs", 0))
    ms = q / rs if rs else 0
    data.update(
        {
            "r_J": r,
            "rs_J": rs,
            "Q": rnd(q, 0),
            "Q_kW": rnd(q / 1000, 2),
            "Q_lat": rnd(q_lat, 0),
            "Q_sens": rnd(q_sens, 0),
            "ms": rnd(ms, 4),
            "ms_h": rnd(ms * 3600, 2),
        }
    )
    return data


def calc_reb_area(data: dict) -> dict:
    q = num(data, "Q", 0)
    k = num(data, "K", 0)
    ts = num(data, "Ts", 0)
    tb = num(data, "Tb", 0)
    if not q or not k:
        raise ValueError("温差面积：请先算热负荷，并填写 K")
    dtm = (ts - tb) if ts and tb else num(data, "dTm", 0)
    if not dtm or dtm <= 0:
        raise ValueError("温差面积：Ts 应高于 Tb")
    a_req = q / (k * dtm)
    phi_a = num(data, "phi_A", 0.2)
    ad = (1 + phi_a) * a_req
    data.update({"dTm": rnd(dtm, 2), "A_req": rnd(a_req, 2), "Ad": rnd(ad, 2), "A": rnd(ad, 2), "phi_A": phi_a})
    return data


def calc_reb_dia(data: dict) -> dict:
    n = num(data, "N", 0)
    do_mm = num(data, "do", 0)
    if not n or not do_mm:
        raise ValueError("壳径初估：请先连接「换热管」")
    eta = num(data, "eta", 0.7)
    ds = do_mm * math.sqrt(n / eta)
    data.update({"eta": eta, "Ds_est": rnd(ds, 0)})
    if not num(data, "Di", 0):
        data["Di"] = rnd(ds, 0)
    return data


def calc_reb_check(data: dict) -> dict:
    n = num(data, "N", 0)
    do_mm = num(data, "do", 0)
    length = num(data, "L", 0)
    a_req = num(data, "A_req", num(data, "A", 0))
    k = num(data, "K", 0)
    dtm = num(data, "dTm", 0)
    r = num(data, "r_J", as_j_per_kg(num(data, "r", 0)))
    mv = num(data, "mv", 0)
    if not n or not do_mm or not length:
        raise ValueError("校核：请先连接「换热管」")
    a_act = n * math.pi * (do_mm / 1000) * length
    eta_a = ((a_act - a_req) / a_req) * 100 if a_req else 0
    q_act = k * a_act * dtm if k and dtm else 0
    mv_cal = q_act / r if r else 0
    data.update(
        {
            "A_act": rnd(a_act, 2),
            "eta_A": rnd(eta_a, 1),
            "Q_act": rnd(q_act, 0),
            "Q_act_kW": rnd(q_act / 1000, 2),
            "mv_cal": rnd(mv_cal, 4),
            "pass_area": "是" if a_act >= a_req else "否",
            "pass_duty": "是" if q_act >= num(data, "Q", 0) else "否",
            "pass_vap": "是" if mv_cal >= mv else "否",
        }
    )
    return data


def fill_scheme(tpl, data: dict) -> str:
    stamp_time(data)
    text = as_text(tpl)
    if not text.strip():
        raise ValueError("请连接方案模板")
    return render_template(text, data)


_SKIP_KEYS = {"_html"}
_LABELS = {
    "equipment": "位号",
    "name": "名称",
    "title": "标题",
    "type": "类型",
    "A": "面积 A",
    "A_req": "所需面积",
    "A_act": "实际面积",
    "Ad": "设计面积",
    "A_bundle": "管束面积",
    "A_eff": "有效面积",
    "do": "管外径 do",
    "L": "管长 L",
    "N": "管数 N",
    "N_raw": "管数原值",
    "t": "管间距 t",
    "t_min": "最小管间距",
    "Pt": "节距 Pt",
    "Di": "内径 Di",
    "Ds_est": "壳径估算",
    "Dtl": "布管圆",
    "Do_ts": "管板外径",
    "tp": "管板厚",
    "t1": "计算壁厚 t1",
    "t2": "计算壁厚 t2",
    "t_shell": "筒体壁厚",
    "t_head": "封头厚",
    "delta_nom": "名义厚度",
    "B": "折流板间距",
    "NB": "折流板数量",
    "B_ratio": "B/Di",
    "h_ratio": "h/Di",
    "h_baffle": "缺口高",
    "delta_b": "折流板厚",
    "As": "壳程流通面积",
    "Q": "热负荷 Q",
    "Q_kW": "热负荷 kW",
    "Q_lat": "潜热负荷",
    "Q_sens": "显热负荷",
    "Q_act": "实际热负荷",
    "Q_act_kW": "实际热负荷 kW",
    "K": "总传热系数 K",
    "K_head": "封头系数",
    "Kp": "管板系数 Kp",
    "C_clean": "清洗间隙",
    "hex_style": "结构型式",
    "delta_t": "管壁厚",
    "n_pass": "管程数",
    "n_shell": "壳程数",
    "arrangement": "布管",
    "Td": "设计温度",
    "tube_material": "管材",
    "shell_material": "壳体材料",
    "mh": "热侧流量",
    "mc": "冷侧流量",
    "cph": "热侧比热",
    "cpc": "冷侧比热",
    "Thi": "热侧进口",
    "Tho": "热侧出口",
    "Tci": "冷侧进口",
    "Tco": "冷侧出口",
    "flow": "流向",
    "Q_h": "热侧负荷",
    "Q_c": "冷侧负荷",
    "dT1": "端差 ΔT1",
    "dT2": "端差 ΔT2",
    "dTm": "温差",
    "mv": "汽化量",
    "mv_cal": "计算汽化量",
    "ms": "蒸汽量",
    "ms_h": "蒸汽量 kg/h",
    "r": "汽化潜热 r",
    "r_J": "汽化潜热 J/kg",
    "rs": "蒸汽潜热",
    "rs_J": "蒸汽潜热 J/kg",
    "m": "液体量 m",
    "cp": "比热 cp",
    "Tb": "沸腾温度",
    "Tin": "进口温度",
    "Ts": "蒸汽温度",
    "eta": "布管效率",
    "eta_A": "面积裕量",
    "eta_tp": "管板效率",
    "n_row": "管排数",
    "n_c": "中心排管数",
    "phi_A": "面积裕量系数",
    "pass_area": "面积校核",
    "pass_duty": "负荷校核",
    "pass_vap": "汽化量校核",
    "P": "设计压力",
    "PN": "公称压力 PN",
    "DN": "公称直径 DN",
    "flange_std": "法兰标准",
    "flange_face": "密封面",
    "flange_kind": "法兰类型",
    "flange_table": "法兰尺寸表",
    "flange_A1_A": "钢管外径 A₁A",
    "flange_A1_B": "钢管外径 A₁B",
    "flange_D": "法兰外径 D",
    "flange_K": "螺栓孔中心圆直径 K",
    "flange_L": "螺栓孔直径 L",
    "flange_C": "法兰厚度 C",
    "flange_B1_A": "法兰内径 B₁A",
    "flange_B1_B": "法兰内径 B₁B",
    "flange_b": "坡口宽度 b",
    "d_open": "开孔直径",
    "d_open_max": "允许开孔",
    "A_open": "所需补强面积",
    "A_open_shell": "壳体多余金属",
    "A_pad": "补强圈面积",
    "t_pad": "补强圈厚",
    "w_pad": "补强圈宽",
    "pass_open": "补强是否够",
    "pass_open_size": "开孔尺寸是否允许",
    "manhole_dn": "人孔 DN",
    "manhole_kind": "人孔型式",
    "manhole_std": "人孔标准",
    "manhole_pn": "人孔 PN",
    "support_kind": "支座型式",
    "support_std": "支座标准",
    "saddle_n": "支座数量",
    "saddle_b": "鞍座宽度",
    "gasket_name": "垫片",
    "gasket_std": "垫片标准",
    "gasket_remark": "垫片备注",
    "bolt_count": "螺栓数量",
    "bolt_size": "螺栓规格",
    "nut_qty": "螺母数量",
    "fastener_std": "紧固件标准",
    "fastener_remark": "紧固件备注",
    "S": "许用应力",
    "phi": "焊缝系数",
    "C": "腐蚀余量",
    "Delta": "厚度附加",
    "path": "路径",
    "basename": "文件名",
    "folder": "目录",
    "date": "日期",
    "time": "时间",
    "datetime": "日期时间",
    "formula": "公式",
    "frontmatter": "前置信息",
    "fm": "前置信息",
    "content": "正文",
    "body": "正文",
    "placeholders": "占位符",
    "headings": "标题",
}


def _esc(v) -> str:
    import html as htmlmod

    return htmlmod.escape("" if v is None else str(v))


def _cell(v) -> str:
    if isinstance(v, bool):
        return _esc("是" if v else "否")
    if isinstance(v, float):
        s = str(int(v)) if v.is_integer() else str(rnd(v, 4))
        return _esc(s)
    if isinstance(v, (dict, list)):
        return _esc(_plain(v))
    return _esc(v)


def _plain(v) -> str:
    if isinstance(v, bool):
        return "是" if v else "否"
    if isinstance(v, float):
        return str(int(v)) if v.is_integer() else str(rnd(v, 4))
    if isinstance(v, dict):
        parts = []
        for key, val in v.items():
            if key in _SKIP_KEYS or str(key).startswith("_"):
                continue
            parts.append(f"{_LABELS.get(key, key)}={_plain(val)}")
        return "；".join(parts)
    if isinstance(v, list):
        return "、".join(_plain(x) for x in v)
    if v is None:
        return ""
    return str(v)


def _label_of(key, prefix: str) -> str:
    name = _LABELS.get(key, str(key))
    return f"{prefix} · {name}" if prefix else name


def render_preview_html(value) -> str:
    if value is None or value == "":
        return '<div class="ck-view-empty">没有数据</div>'
    if isinstance(value, bool):
        return f'<div class="ck-view-num">{_esc("是" if value else "否")}</div>'
    if isinstance(value, (int, float)):
        return f'<div class="ck-view-num">{_cell(value)}</div>'
    if isinstance(value, str):
        return f'<pre class="ck-view-text">{_esc(value)}</pre>'
    if isinstance(value, dict):
        path = str(value.get("path") or "")
        mime = str(value.get("mime") or "")
        low = path.lower()
        if path and (mime.startswith("image/") or low.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"))):
            from urllib.parse import quote

            return f'<img class="ck-view-img" src="/api/file?path={quote(path)}" alt="{_esc(path)}">'
        if isinstance(value.get("columns"), list) and isinstance(value.get("rows"), list):
            return _html_table(value["columns"], value["rows"])
        if path and set(value.keys()) <= {"path", "mime", "kind"}:
            return f'<div class="ck-view-file">{_esc(path)}</div>'
        return _html_kv(value)
    if isinstance(value, list):
        if value and all(isinstance(x, dict) for x in value):
            cols = []
            for row in value:
                for k in row:
                    if k not in cols:
                        cols.append(k)
            rows = [[row.get(c, "") for c in cols] for row in value]
            return _html_table(cols, rows)
        text = "\n".join(_plain(x) for x in value)
        return f'<pre class="ck-view-text">{_esc(text)}</pre>'
    return f'<pre class="ck-view-text">{_esc(value)}</pre>'


def _html_kv(data: dict, prefix: str = "") -> str:
    rows = []
    nested = []
    for key, val in data.items():
        if key in _SKIP_KEYS or str(key).startswith("_"):
            continue
        label = _label_of(key, prefix)
        if isinstance(val, dict) and val:
            nested.append(_html_kv(val, label))
            continue
        if isinstance(val, list) and val and all(isinstance(x, dict) for x in val):
            cols = []
            for row in val:
                for k in row:
                    if k not in cols:
                        cols.append(k)
            rows_data = [[row.get(c, "") for c in cols] for row in val]
            nested.append(f'<div class="ck-view-block"><div class="ck-view-cap">{_esc(label)}</div>{_html_table(cols, rows_data)}</div>')
            continue
        rows.append(f"<tr><th>{_esc(label)}</th><td>{_cell(val)}</td></tr>")
    parts = []
    if rows:
        parts.append('<table class="ck-view-table">' + "".join(rows) + "</table>")
    parts.extend(nested)
    if not parts:
        return '<div class="ck-view-empty">没有可显示的字段</div>'
    return "".join(parts)


def _html_table(columns, rows) -> str:
    head = "".join(f"<th>{_esc(_LABELS.get(c, c))}</th>" for c in columns)
    body = []
    for row in rows:
        cells = row if isinstance(row, (list, tuple)) else [row]
        body.append("<tr>" + "".join(f"<td>{_cell(c)}</td>" for c in cells) + "</tr>")
    return f'<table class="ck-view-grid"><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table>'

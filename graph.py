from __future__ import annotations

from collections import defaultdict, deque

from nodes import def_of, exec_node, preview_pack
from vault import Vault


def topo_order(nodes: list[dict], edges: list[dict]) -> list[str]:
    ids = [n["id"] for n in nodes]
    incoming: dict[str, int] = {i: 0 for i in ids}
    outs: dict[str, list[str]] = defaultdict(list)
    for e in edges:
        if e["from"] not in incoming or e["to"] not in incoming:
            continue
        outs[e["from"]].append(e["to"])
        incoming[e["to"]] += 1
    q = deque([i for i, n in incoming.items() if n == 0])
    order: list[str] = []
    while q:
        cur = q.popleft()
        order.append(cur)
        for nxt in outs[cur]:
            incoming[nxt] -= 1
            if incoming[nxt] == 0:
                q.append(nxt)
    if len(order) != len(ids):
        raise ValueError("连线存在循环，无法执行")
    return order


def bypass_pack(node: dict, inputs: dict) -> dict:
    dst = def_of(node["type"])
    ins = dst.get("inputs") or []
    pack: dict = {}
    used: set[str] = set()
    for out in dst.get("outputs") or []:
        name = out.get("name")
        typ = out.get("type")
        if name in inputs:
            pack[name] = inputs[name]
            continue
        hit = None
        for inn in ins:
            in_name = inn.get("name")
            if in_name in used:
                continue
            in_typ = inn.get("type")
            if in_typ == typ or typ == "ANY" or in_typ == "ANY":
                hit = in_name
                break
        if hit is None and ins:
            hit = next((inn.get("name") for inn in ins if inn.get("name") not in used), None)
        if hit:
            used.add(hit)
            pack[name] = inputs.get(hit)
    return pack


def run_graph(nodes: list[dict], edges: list[dict], vault: Vault) -> dict:
    if not nodes:
        raise ValueError("画布是空的")
    by_id = {n["id"]: n for n in nodes}
    order = topo_order(nodes, edges)
    values: dict[str, dict] = {}
    previews: dict[str, str] = {}
    exported: list[str] = []
    views: dict[str, str] = {}
    for nid in order:
        node = by_id[nid]
        src_def = None
        inputs: dict = {}
        dst_def = def_of(node["type"])
        for e in edges:
            if e["to"] != nid:
                continue
            src = by_id.get(e["from"])
            if not src:
                continue
            src_def = def_of(src["type"])
            outs = src_def.get("outputs") or []
            ins = dst_def.get("inputs") or []
            from_slot = int(e.get("fromSlot") or 0)
            to_slot = int(e.get("toSlot") or 0)
            out_name = (outs[from_slot] if from_slot < len(outs) else {}).get("name")
            in_name = (ins[to_slot] if to_slot < len(ins) else {}).get("name")
            pack = values.get(e["from"]) or {}
            if in_name:
                inputs[in_name] = pack.get(out_name)
        if node.get("bypass"):
            pack = bypass_pack(node, inputs)
            values[nid] = pack
            previews[nid] = "不启动"
            continue
        pack = exec_node(node, inputs, vault)
        values[nid] = pack or {}
        previews[nid] = preview_pack(node["type"], values[nid])
        if node["type"] == "Preview" and values[nid].get("_html"):
            views[nid] = values[nid]["_html"]
        if node["type"] == "ExportTemplate" and values[nid].get("路径"):
            exported.append(values[nid]["路径"])
    return {"ok": True, "previews": previews, "views": views, "exported": exported}

from __future__ import annotations

import importlib
from pathlib import Path

TYPE_COLOR = {
    "TEMPLATE": "#c9a227",
    "STRING": "#7FDB6A",
    "TEXT": "#7FDB6A",
    "DATA": "#c77dff",
    "INT": "#73B2FF",
    "NUMBER": "#73B2FF",
    "JSON": "#ff9f43",
    "IMAGE": "#ff6b8a",
    "TABLE": "#4ecdc4",
    "FILE": "#a8dadc",
    "ANY": "#C8C8C8",
    "公称直径": "#5ec8c5",
}
CAT_COLOR = {
    "模板": "#8a6d1b",
    "数据": "#6b3fa0",
    "物理": "#4a5568",
    "换热器": "#4a6fa5",
    "再沸器": "#2a6f7a",
    "通用件": "#5a6570",
    "理论计算": "#3b6ea5",
    "计算": "#3b6ea5",
    "导出": "#b05050",
}

_PLUGINS: dict[str, "NodePlugin"] = {}
NODE_DEFS: list[dict] = []


class NodePlugin:
    type = ""
    title = ""
    category = ""
    inputs: list = []
    outputs: list = []
    widgets: list = []
    hint = ""
    order = 1000

    def as_def(self) -> dict:
        return {
            "type": self.type,
            "title": self.title,
            "category": self.category,
            "inputs": list(self.inputs or []),
            "outputs": list(self.outputs or []),
            "widgets": list(self.widgets or []),
            "hint": self.hint or "",
        }

    def execute(self, node: dict, inputs: dict, vault) -> dict:
        raise NotImplementedError

    def preview(self, pack: dict) -> str | None:
        return None


def register(cls):
    plugin = cls()
    if not plugin.type:
        raise ValueError("节点插件缺少 type：" + cls.__name__)
    if plugin.type in _PLUGINS:
        raise ValueError("重复注册节点：" + plugin.type)
    _PLUGINS[plugin.type] = plugin
    return cls


def rebuild_defs() -> None:
    NODE_DEFS[:] = [p.as_def() for p in sorted(_PLUGINS.values(), key=lambda p: (p.order, p.type))]


def plugin_of(node_type: str) -> NodePlugin:
    plugin = _PLUGINS.get(node_type)
    if not plugin:
        raise ValueError("未知节点：" + node_type)
    return plugin


def def_of(node_type: str) -> dict:
    return plugin_of(node_type).as_def()


def exec_node(node: dict, inputs: dict, vault) -> dict:
    return plugin_of(node["type"]).execute(node, inputs, vault) or {}


def source_of(node_type: str) -> Path:
    import inspect

    plugin = plugin_of(node_type)
    path = Path(inspect.getfile(type(plugin))).resolve()
    root = Path(__file__).resolve().parent
    if path.parent != root:
        raise ValueError("源码不在节点插件目录")
    return path


def _reload_plugin_file(path: Path) -> None:
    import inspect
    import sys

    path = path.resolve()
    for typ in [t for t, p in list(_PLUGINS.items()) if Path(inspect.getfile(type(p))).resolve() == path]:
        del _PLUGINS[typ]
    name = f"{__package__}.{path.stem}"
    mod = sys.modules.get(name)
    if mod is None:
        importlib.import_module(name)
    else:
        importlib.reload(mod)
    rebuild_defs()
    still = [t for t, p in _PLUGINS.items() if Path(inspect.getfile(type(p))).resolve() == path]
    if not still:
        raise ValueError("文件里没有 @register 的节点")


def save_source(node_type: str, code: str) -> Path:
    path = source_of(node_type)
    text = (code or "").replace("\r\n", "\n")
    if not text.strip():
        raise ValueError("源码是空的")
    try:
        compile(text, str(path), "exec")
    except SyntaxError as err:
        loc = f"（第 {err.lineno} 行）" if err.lineno else ""
        raise ValueError("语法错误：" + (err.msg or "无效") + loc) from err
    old = path.read_text(encoding="utf-8")
    path.write_text(text, encoding="utf-8", newline="\n")
    try:
        _reload_plugin_file(path)
    except Exception as err:
        path.write_text(old, encoding="utf-8", newline="\n")
        try:
            _reload_plugin_file(path)
        except Exception:
            pass
        raise ValueError("加载失败，已还原：" + str(err)) from err
    return path


def preview_pack(node_type: str, pack: dict) -> str:
    if not pack:
        return "(空)"
    plugin = _PLUGINS.get(node_type)
    if plugin:
        text = plugin.preview(pack)
        if text is not None:
            return str(text)
    from engine import preview_of

    first = next(iter(pack.values()), None)
    if isinstance(first, dict):
        return preview_of(first.get("title") or first.get("path") or first.get("equipment"))
    return preview_of(first)


def load_all() -> None:
    here = Path(__file__).resolve().parent
    skip = {"__init__", "registry"}
    for path in sorted(here.glob("*.py")):
        stem = path.stem
        if stem in skip or stem.startswith("_"):
            continue
        importlib.import_module(f"{__package__}.{stem}")
    rebuild_defs()

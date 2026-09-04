from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


class Vault:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def resolve(self, rel: str) -> Path:
        rel = (rel or "").replace("\\", "/").lstrip("/")
        path = (self.root / rel).resolve()
        if path != self.root and self.root not in path.parents:
            raise ValueError("路径超出库范围：" + rel)
        return path

    def rel(self, path: Path) -> str:
        return path.resolve().relative_to(self.root).as_posix()

    def list_markdown(self, folder: str = "模板") -> list[Path]:
        root = self.resolve(folder)
        if not root.exists():
            return []
        if root.is_file() and root.suffix.lower() == ".md":
            return [root]
        return sorted(p for p in root.rglob("*.md") if p.is_file() and ".obsidian" not in p.parts)

    def pick_template(self, folder: str, rel: str = "") -> Path | None:
        files = self.list_markdown(folder)
        if not files:
            return None
        folder = (folder or "模板").replace("\\", "/").rstrip("/")
        if rel:
            want = rel if rel.startswith(folder + "/") else f"{folder}/{rel}"
            want = want.replace("//", "/")
            for f in files:
                r = self.rel(f)
                if r == want or r.endswith("/" + rel):
                    return f
        for f in files:
            if "计算方案" in f.stem:
                return f
        for f in files:
            if f.stem != "说明":
                return f
        return files[0]

    def read_text(self, rel: str) -> tuple[str, str]:
        path = self.resolve(rel)
        if not path.is_file():
            raise FileNotFoundError("找不到笔记：" + rel)
        return self.rel(path), path.read_text(encoding="utf-8")

    def write_text(self, rel: str, text: str) -> str:
        path = self.resolve(rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return self.rel(path)

    def latest_markdown(self) -> Path | None:
        files = [
            p
            for p in self.root.rglob("*.md")
            if p.is_file() and ".obsidian" not in p.parts and "workflow_web" not in p.parts
        ]
        if not files:
            return None
        return max(files, key=lambda p: p.stat().st_mtime)

    def list_workflows(self) -> list[dict]:
        items = []
        folder = self.root / "工作流"
        folder.mkdir(parents=True, exist_ok=True)
        for p in sorted(folder.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            st = p.stat()
            items.append(
                {
                    "path": self.rel(p),
                    "name": p.stem,
                    "mtime": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M"),
                }
            )
        return items

    def load_workflow(self, rel: str) -> dict:
        path = self.resolve(rel)
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("工作流不是对象：" + rel)
        return data

    def save_workflow(self, rel: str, data: dict) -> str:
        rel = self._workflow_path(rel)
        payload = {
            "version": 1,
            "type": "wn-node-panel-workflow",
            "pan": data.get("pan") or {"x": 16, "y": 16},
            "zoom": data.get("zoom") or 1,
            "nodes": data.get("nodes") or [],
            "edges": data.get("edges") or [],
            "saved": datetime.now().isoformat(timespec="seconds"),
        }
        return self.write_text(rel, json.dumps(payload, ensure_ascii=False, indent=2))

    def delete_workflow(self, rel: str) -> str:
        path = self.resolve(self._workflow_path(rel))
        if not path.is_file():
            raise FileNotFoundError("找不到工作流：" + rel)
        path.unlink()
        return self.rel(path)

    def rename_workflow(self, rel: str, new_name: str) -> str:
        src = self.resolve(self._workflow_path(rel))
        if not src.is_file():
            raise FileNotFoundError("找不到工作流：" + rel)
        dest_rel = self._workflow_path(new_name)
        dest = self.resolve(dest_rel)
        if dest.parent != src.parent:
            raise ValueError("只能在工作流目录内改名")
        if dest.exists() and dest != src:
            raise ValueError("已有同名工作流：" + dest.stem)
        src.rename(dest)
        return self.rel(dest)

    def _workflow_path(self, raw: str) -> str:
        name = Path(str(raw or "").replace("\\", "/")).name
        name = "".join(ch for ch in name if ch not in '<>:"/\\|?*')
        if not name:
            raise ValueError("名字不能为空")
        if not name.lower().endswith(".json"):
            name += ".json"
        return "工作流/" + name

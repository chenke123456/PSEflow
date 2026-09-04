from __future__ import annotations

import argparse
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from graph import run_graph
from nodes import CAT_COLOR, NODE_DEFS, TYPE_COLOR, save_source, source_of
from vault import Vault

HERE = Path(__file__).resolve().parent
DEFAULT_VAULT = HERE.parent


class GraphPayload(BaseModel):
    nodes: list[dict] = []
    edges: list[dict] = []
    pan: dict | None = None
    zoom: float | None = None


class SavePayload(GraphPayload):
    path: str


class RenamePayload(BaseModel):
    path: str
    name: str


class NodeSourcePayload(BaseModel):
    type: str
    code: str


def create_app(vault_root: Path) -> FastAPI:
    vault = Vault(vault_root)
    api = FastAPI(title="CK Workflow")
    api.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    @api.get("/api/meta")
    def meta():
        return {
            "vault": str(vault.root),
            "defs": NODE_DEFS,
            "typeColor": TYPE_COLOR,
            "catColor": CAT_COLOR,
        }

    @api.get("/api/workflows")
    def workflows():
        return {"items": vault.list_workflows()}

    @api.get("/api/workflow")
    def load_workflow(path: str):
        try:
            return vault.load_workflow(path)
        except FileNotFoundError as err:
            raise HTTPException(404, str(err)) from err
        except Exception as err:
            raise HTTPException(400, str(err)) from err

    @api.post("/api/workflow")
    def save_workflow(body: SavePayload):
        try:
            saved = vault.save_workflow(body.path, body.model_dump())
            return {"ok": True, "path": saved}
        except Exception as err:
            raise HTTPException(400, str(err)) from err

    @api.post("/api/workflow/rename")
    def rename_workflow(body: RenamePayload):
        try:
            return {"ok": True, "path": vault.rename_workflow(body.path, body.name)}
        except FileNotFoundError as err:
            raise HTTPException(404, str(err)) from err
        except Exception as err:
            raise HTTPException(400, str(err)) from err

    @api.delete("/api/workflow")
    def delete_workflow(path: str):
        try:
            return {"ok": True, "path": vault.delete_workflow(path)}
        except FileNotFoundError as err:
            raise HTTPException(404, str(err)) from err
        except Exception as err:
            raise HTTPException(400, str(err)) from err

    @api.get("/api/file")
    def read_file(path: str):
        try:
            file_path = vault.resolve(path)
        except ValueError as err:
            raise HTTPException(400, str(err)) from err
        if not file_path.is_file():
            raise HTTPException(404, "找不到文件：" + path)
        return FileResponse(file_path)

    @api.get("/api/node-source")
    def node_source(type: str):
        try:
            path = source_of(type)
        except ValueError as err:
            raise HTTPException(404, str(err)) from err
        rel = path.relative_to(HERE).as_posix()
        return {"path": rel, "code": path.read_text(encoding="utf-8")}

    @api.post("/api/node-source")
    def write_node_source(body: NodeSourcePayload):
        try:
            path = save_source(body.type, body.code)
        except ValueError as err:
            raise HTTPException(400, str(err)) from err
        rel = path.relative_to(HERE).as_posix()
        return {"ok": True, "path": rel}

    @api.post("/api/run")
    def run(body: GraphPayload):
        try:
            return run_graph(body.nodes, body.edges, vault)
        except Exception as err:
            raise HTTPException(400, str(err)) from err

    api.mount("/", StaticFiles(directory=str(HERE / "static"), html=True), name="static")
    return api


app = create_app(DEFAULT_VAULT)


def port_in_use(host: str, port: int) -> bool:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.4)
        return sock.connect_ex((host, port)) == 0


if __name__ == "__main__":
    import sys
    import webbrowser

    import uvicorn

    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", default=str(DEFAULT_VAULT))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    url = f"http://127.0.0.1:{args.port}"
    if port_in_use("127.0.0.1", args.port):
        print(f"端口 {args.port} 已经在用，直接打开 {url}")
        webbrowser.open(url)
        sys.exit(0)
    webbrowser.open(url)
    uvicorn.run(create_app(Path(args.vault)), host=args.host, port=args.port, reload=False)

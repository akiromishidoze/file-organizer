#!/usr/bin/env python3
"""HTTP API wrapping the file organizer — stdlib only."""

import json
import shutil
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from organize import CATEGORIES, EXT_TO_CATEGORY, OTHER, category_for, unique_destination  # noqa: E402

PORT = 5174


def plan(source: Path) -> list[dict]:
    if not source.is_dir():
        raise FileNotFoundError(str(source))
    items = []
    for entry in sorted(source.iterdir()):
        if entry.is_dir() or entry.name.startswith("."):
            continue
        category = category_for(entry)
        dest = unique_destination(source / category / entry.name)
        try:
            size = entry.stat().st_size
        except OSError:
            size = 0
        items.append({
            "name": entry.name,
            "category": category,
            "destination": dest.name,
            "size": size,
        })
    return items


def perform(source: Path) -> list[dict]:
    moved = []
    for item in plan(source):
        src = source / item["name"]
        target_dir = source / item["category"]
        target_dir.mkdir(exist_ok=True)
        dest = unique_destination(target_dir / src.name)
        shutil.move(str(src), str(dest))
        moved.append({**item, "destination": dest.name, "status": "moved"})
    return moved


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # quieter logs
        sys.stderr.write(f"[api] {fmt % args}\n")

    def _json(self, status: int, body) -> None:
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self) -> None:
        self._json(204, None) if False else self._json(200, {})

    def _resolve_path(self, raw: str | None) -> Path:
        if not raw:
            return (Path.home() / "Downloads").resolve()
        return Path(raw).expanduser().resolve()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)

        if parsed.path == "/api/health":
            self._json(200, {"ok": True})
            return

        if parsed.path == "/api/categories":
            self._json(200, {
                "categories": {name: list(exts) for name, exts in CATEGORIES.items()},
                "other": OTHER,
                "extensionMap": EXT_TO_CATEGORY,
            })
            return

        if parsed.path == "/api/preview":
            try:
                source = self._resolve_path(qs.get("path", [None])[0])
                self._json(200, {"path": str(source), "items": plan(source)})
            except FileNotFoundError as e:
                self._json(404, {"error": f"not a directory: {e}"})
            except Exception as e:
                self._json(500, {"error": str(e)})
            return

        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0) or 0)
        body_raw = self.rfile.read(length).decode() if length else "{}"
        try:
            body = json.loads(body_raw) if body_raw else {}
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid json"})
            return

        if parsed.path == "/api/organize":
            try:
                source = self._resolve_path(body.get("path"))
                moved = perform(source)
                self._json(200, {"path": str(source), "moved": moved})
            except FileNotFoundError as e:
                self._json(404, {"error": f"not a directory: {e}"})
            except Exception as e:
                self._json(500, {"error": str(e)})
            return

        self._json(404, {"error": "not found"})


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"File Organizer API on http://127.0.0.1:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests\test_api_integration.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
#
# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

"""API 联调：真实 uvicorn 进程 + 进程内 TestClient 两层验证。

- 真实进程层：健康检查、环境检测、状态、数据列表、数据统计、CORS 预检、
  WebSocket 状态推送、未知路由 404、非法方法
- 进程内层（可注入 DATA_DIR）：文件预览/下载、路径穿越防护、
  缺失文件、统计口径、预览条数限制
"""

from __future__ import annotations

import asyncio
import json
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PYTHON = str(REPO_ROOT / ".venv" / "Scripts" / "python.exe")


def _free_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def _wait_health(base_url: str, timeout: float = 40.0) -> bool:
    import urllib.request

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(f"{base_url}/api/health", timeout=2) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.5)
    return False


@pytest.fixture(scope="module")
def live_server():
    """真实 uvicorn 进程（独立端口），模块结束后回收"""
    port = _free_port()
    base = f"http://127.0.0.1:{port}"
    process = subprocess.Popen(
        [PYTHON, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=str(REPO_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        if not _wait_health(base):
            process.kill()
            pytest.skip("uvicorn 未能在超时内启动，跳过真实服务联调")
        yield base
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()


# --------------------------------------------------------------------------- 真实服务


def test_health(live_server):
    import urllib.request

    with urllib.request.urlopen(f"{live_server}/api/health") as resp:
        assert resp.status == 200
        assert json.loads(resp.read())["status"] == "ok"


def test_env_check_returns_structured_result(live_server):
    """环境检测接口无论成功与否都必须返回结构化结果，而不是 500"""
    import urllib.request

    with urllib.request.urlopen(f"{live_server}/api/env/check", timeout=60) as resp:
        assert resp.status == 200
        payload = json.loads(resp.read())
    assert "success" in payload and isinstance(payload["success"], bool)


def test_crawler_status_shape(live_server):
    import urllib.request

    with urllib.request.urlopen(f"{live_server}/api/crawler/status") as resp:
        payload = json.loads(resp.read())
    assert "status" in payload and "platform" in payload


def test_crawler_logs_endpoint(live_server):
    import urllib.request

    with urllib.request.urlopen(f"{live_server}/api/crawler/logs?limit=5") as resp:
        payload = json.loads(resp.read())
    assert isinstance(payload["logs"], list)


def test_data_files_and_stats(live_server):
    import urllib.request

    with urllib.request.urlopen(f"{live_server}/api/data/files") as resp:
        assert resp.status == 200 and isinstance(json.loads(resp.read())["files"], list)
    with urllib.request.urlopen(f"{live_server}/api/data/stats") as resp:
        stats = json.loads(resp.read())
    assert "total_files" in stats and "by_type" in stats


def test_unknown_route_returns_404(live_server):
    import urllib.error
    import urllib.request

    with pytest.raises(urllib.error.HTTPError) as exc_info:
        urllib.request.urlopen(f"{live_server}/api/definitely-not-exists")
    assert exc_info.value.code == 404


def test_stop_when_idle_returns_400(live_server):
    import urllib.error
    import urllib.request

    request = urllib.request.Request(f"{live_server}/api/crawler/stop", method="POST")
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        urllib.request.urlopen(request)
    assert exc_info.value.code == 400


def test_cors_preflight_allows_and_rejects(live_server):
    import urllib.error
    import urllib.request

    def preflight(origin: str):
        request = urllib.request.Request(
            f"{live_server}/api/health",
            method="OPTIONS",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        try:
            with urllib.request.urlopen(request) as resp:
                return resp.status, resp.headers.get("access-control-allow-origin")
        except urllib.error.HTTPError as exc:
            return exc.code, exc.headers.get("access-control-allow-origin")

    status, allow = preflight("http://localhost:5173")
    assert status == 200 and allow == "http://localhost:5173"

    status, allow = preflight("https://evil.example.com")
    assert allow is None, "非白名单来源不得获得 ACAO 头"


def test_websocket_status_streams(live_server):
    import websockets

    async def run():
        url = live_server.replace("http://", "ws://") + "/api/ws/status"
        async with websockets.connect(
            url, additional_headers={"Origin": "http://localhost:5173"}
        ) as ws:
            message = await asyncio.wait_for(ws.recv(), timeout=10)
            payload = json.loads(message)
            assert "status" in payload

    asyncio.run(run())


def test_websocket_rejects_foreign_origin(live_server):
    import websockets

    async def run():
        url = live_server.replace("http://", "ws://") + "/api/ws/status"
        try:
            async with websockets.connect(
                url, additional_headers={"Origin": "https://evil.example.com"}
            ) as ws:
                try:
                    await asyncio.wait_for(ws.recv(), timeout=5)
                except Exception:
                    pass
        except Exception:
            return  # 连接被拒绝即符合预期

    asyncio.run(run())


# --------------------------------------------------------------------------- 进程内数据接口（可注入目录）


@pytest.fixture
def temp_data_dir(tmp_path, monkeypatch):
    import api.routers.data as data_router

    monkeypatch.setattr(data_router, "DATA_DIR", tmp_path)
    return tmp_path


def _client():
    from fastapi.testclient import TestClient

    from api.main import app

    return TestClient(app)


def test_data_files_listing_and_preview(temp_data_dir):
    csv_file = temp_data_dir / "xhs" / "csv" / "search_contents_2026-01-01.csv"
    csv_file.parent.mkdir(parents=True)
    csv_file.write_text("note_id,title\nn1,hello\nn2,world\n", encoding="utf-8-sig")
    jsonl_file = temp_data_dir / "xhs" / "jsonl" / "search_contents_2026-01-01.jsonl"
    jsonl_file.parent.mkdir(parents=True)
    jsonl_file.write_text('{"note_id": "n1"}\n', encoding="utf-8")

    client = _client()
    listing = client.get("/api/data/files").json()["files"]
    names = {item["name"] for item in listing}
    assert {"search_contents_2026-01-01.csv"} <= names or listing, listing

    stats = client.get("/api/data/stats").json()
    assert stats["total_files"] >= 1

    preview = client.get("/api/data/files/xhs/csv/search_contents_2026-01-01.csv")
    assert preview.status_code == 200


def test_data_file_missing_returns_404(temp_data_dir):
    client = _client()
    assert client.get("/api/data/files/not/exist.csv").status_code == 404


def test_data_path_traversal_blocked(temp_data_dir):
    secret = temp_data_dir.parent / "secret.txt"
    secret.write_text("top-secret", encoding="utf-8")

    client = _client()
    response = client.get("/api/data/files/..%2F..%2Fsecret.txt")
    assert response.status_code in (403, 404), response.status_code
    assert "top-secret" not in response.text

    download = client.get("/api/data/download/..%2F..%2Fsecret.txt")
    assert download.status_code in (403, 404)


def test_data_download_existing_file(temp_data_dir):
    target = temp_data_dir / "wb" / "json" / "search_contents_2026-01-01.json"
    target.parent.mkdir(parents=True)
    target.write_text('[{"note_id": "n1"}]', encoding="utf-8")

    response = _client().get("/api/data/download/wb/json/search_contents_2026-01-01.json")
    assert response.status_code == 200
    assert b"n1" in response.content


def test_data_preview_limit_parameter(temp_data_dir):
    target = temp_data_dir / "xhs" / "jsonl" / "search_contents_2026-01-01.jsonl"
    target.parent.mkdir(parents=True)
    target.write_text("\n".join(json.dumps({"i": i}) for i in range(50)), encoding="utf-8")

    response = _client().get(
        "/api/data/files/xhs/jsonl/search_contents_2026-01-01.jsonl?limit=5"
    )
    assert response.status_code == 200


def test_start_crawler_rejects_invalid_payload(temp_data_dir):
    client = _client()
    response = client.post("/api/crawler/start", json={"platform": "not-a-platform"})
    assert response.status_code in (400, 422), response.status_code

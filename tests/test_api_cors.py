# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests/test_api_cors.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
"""CORS allow-list regression tests.

api.main 的 CORS 中间件从"反射任意 Origin"收紧为 allow-list：
- 本机开发端口（localhost/127.0.0.1 任意端口）始终放行（vite dev）；
- 同源请求放行（与 Host 头一致）；
- 额外来源必须通过 MEDIACRAWLER_CORS_EXTRA_ORIGINS 显式配置；
- 其余来源不下发 CORS 头（浏览器将拦截跨域响应）。
"""
import pytest
from fastapi import WebSocketDisconnect
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture()
def client():
    return TestClient(app)


def _get(client, origin=None, host=None):
    headers = {}
    if origin:
        headers["Origin"] = origin
    if host:
        headers["Host"] = host
    return client.get("/api/health", headers=headers)


def test_cors_allows_localhost_dev_origin(client):
    resp = _get(client, origin="http://localhost:5173")
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert resp.headers.get("access-control-allow-credentials") == "true"


def test_cors_allows_loopback_ip_dev_origin(client):
    resp = _get(client, origin="http://127.0.0.1:5173")
    assert resp.headers.get("access-control-allow-origin") == "http://127.0.0.1:5173"


def test_cors_allows_same_origin(client):
    # 同源：Origin 与 Host 一致（例如 Railway/ngrok 上静态前端与 API 同域）
    resp = _get(client, origin="https://demo.example.com", host="demo.example.com")
    assert resp.headers.get("access-control-allow-origin") == "https://demo.example.com"


def test_cors_rejects_arbitrary_origin(client):
    resp = _get(client, origin="https://evil.example")
    assert "access-control-allow-origin" not in resp.headers
    assert "access-control-allow-credentials" not in resp.headers


def test_cors_preflight_rejected_origin_gets_no_acao(client):
    resp = client.options(
        "/api/health",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert "access-control-allow-origin" not in resp.headers


def test_cors_extra_origins_via_env(client, monkeypatch):
    monkeypatch.setenv("MEDIACRAWLER_CORS_EXTRA_ORIGINS", "https://partner.example, https://pages.example")
    resp = _get(client, origin="https://partner.example")
    assert resp.headers.get("access-control-allow-origin") == "https://partner.example"
    resp2 = _get(client, origin="https://pages.example")
    assert resp2.headers.get("access-control-allow-origin") == "https://pages.example"
    resp3 = _get(client, origin="https://not-listed.example")
    assert "access-control-allow-origin" not in resp3.headers


def test_cors_preflight_permits_ngrok_skip_header(client):
    # 前端经 ngrok 隧道请求时必发 ngrok-skip-browser-warning（webui/src/lib/api.ts），
    # 预检 Access-Control-Request-Headers 必须放行，否则 GH-Pages→ngrok 部署路径全挂
    resp = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "ngrok-skip-browser-warning, content-type",
        },
    )
    assert resp.status_code == 200
    assert "ngrok-skip-browser-warning" in resp.headers.get("access-control-allow-headers", "")


def test_cors_host_spoof_with_foreign_origin_rejected(client):
    # Origin 与 Host 不一致时，不能凭 Host 是合法域名放行（防 Host 伪造绕过）
    resp = _get(client, origin="https://evil.example", host="demo.example.com")
    assert "access-control-allow-origin" not in resp.headers


# ----------------------------- WebSocket 握手 Origin 校验 -----------------------------

def test_ws_status_allows_localhost_origin(client):
    with client.websocket_connect(
        "/api/ws/status", headers={"Origin": "http://localhost:5173"}
    ) as ws:
        data = ws.receive_json()
        assert isinstance(data, dict)


def test_ws_status_rejects_foreign_origin(client):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(
            "/api/ws/status", headers={"Origin": "https://evil.example"}
        ):
            pass


def test_ws_logs_rejects_foreign_origin(client):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(
            "/api/ws/logs", headers={"Origin": "https://evil.example"}
        ):
            pass


def test_ws_allows_same_origin(client):
    # 与 Host 头一致的同源 WS 握手放行（ngrok/Railway 部署形态）
    with client.websocket_connect(
        "/api/ws/status",
        headers={"Origin": "https://demo.example.com", "Host": "demo.example.com"},
    ) as ws:
        data = ws.receive_json()
        assert isinstance(data, dict)

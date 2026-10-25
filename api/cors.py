# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/api/cors.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
"""跨域来源 allow-list（HTTP CORS 中间件与 WebSocket 握手共用）。

该 API 可控制爬虫并回传采集数据，不反射任意 Origin：
- 本机开发端口（localhost/127.0.0.1 任意端口）始终放行（vite dev）；
- 同源请求（Origin 与 Host 头一致，如 Railway/ngrok 上静态前端与 API 同域）放行；
- 其余来源必须通过环境变量 MEDIACRAWLER_CORS_EXTRA_ORIGINS 显式追加（逗号分隔）。
"""

import os

CORS_METHODS = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
# ngrok-skip-browser-warning: 前端(webui/src/lib/api.ts)经 ngrok 隧道请求时必发，
# 缺失会导致跨域预检被浏览器拒绝（GH-Pages → ngrok 部署路径）。
CORS_HEADERS = "Content-Type, Authorization, X-Requested-With, ngrok-skip-browser-warning"


def cors_extra_origins() -> list:
    raw = os.environ.get("MEDIACRAWLER_CORS_EXTRA_ORIGINS", "")
    return [o.strip() for o in raw.split(",") if o.strip()]


def origin_allowed(origin: str, host_header: str) -> bool:
    if not origin:
        return False
    if origin in cors_extra_origins():
        return True
    # 同源请求（浏览器对同源 fetch 也会带 Origin，与 Host 一致时直接放行）
    if host_header:
        for scheme in ("http://", "https://"):
            if origin.startswith(scheme) and origin[len(scheme):] == host_header:
                return True
    # 本机开发来源：任意端口
    for prefix in ("http://localhost:", "http://127.0.0.1:", "https://localhost:", "https://127.0.0.1:"):
        if origin.startswith(prefix):
            return True
    return False

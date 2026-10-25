# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests\test_cdp_browser.py
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

from unittest.mock import AsyncMock, MagicMock

import pytest

import config
from tools.cdp_browser import CDPBrowserManager


@pytest.mark.asyncio
async def test_existing_browser_connects_directly_to_devtools_browser(monkeypatch):
    monkeypatch.setattr(config, "CDP_CONNECT_EXISTING", True)
    monkeypatch.setattr(config, "BROWSER_LAUNCH_TIMEOUT", 60)

    manager = CDPBrowserManager()
    manager.debug_port = 9222
    manager._get_browser_websocket_url = AsyncMock(  # type: ignore[method-assign]
        side_effect=AssertionError("existing browser mode must not call /json/version")
    )

    browser = MagicMock()
    browser.is_connected.return_value = True
    browser.contexts = []

    playwright = MagicMock()
    playwright.chromium.connect_over_cdp = AsyncMock(return_value=browser)

    await manager._connect_via_cdp(playwright)

    playwright.chromium.connect_over_cdp.assert_awaited_once_with(
        "ws://localhost:9222/devtools/browser",
        timeout=60000,
    )


@pytest.mark.asyncio
async def test_existing_browser_falls_back_to_discovered_websocket_url(monkeypatch):
    monkeypatch.setattr(config, "CDP_CONNECT_EXISTING", True)
    monkeypatch.setattr(config, "BROWSER_LAUNCH_TIMEOUT", 60)

    manager = CDPBrowserManager()
    manager.debug_port = 9222
    manager._get_browser_websocket_url = AsyncMock(  # type: ignore[method-assign]
        return_value="ws://localhost:9222/devtools/browser/generated-id"
    )

    browser = MagicMock()
    browser.is_connected.return_value = True
    browser.contexts = []

    playwright = MagicMock()
    playwright.chromium.connect_over_cdp = AsyncMock(
        side_effect=[RuntimeError("direct websocket failed"), browser]
    )

    await manager._connect_via_cdp(playwright)

    manager._get_browser_websocket_url.assert_awaited_once_with(9222)
    assert playwright.chromium.connect_over_cdp.await_args_list[0].args == (
        "ws://localhost:9222/devtools/browser",
    )
    assert playwright.chromium.connect_over_cdp.await_args_list[0].kwargs == {
        "timeout": 60000,
    }
    assert playwright.chromium.connect_over_cdp.await_args_list[1].args == (
        "ws://localhost:9222/devtools/browser/generated-id",
    )
    assert playwright.chromium.connect_over_cdp.await_args_list[1].kwargs == {
        "timeout": 60000,
    }


@pytest.mark.asyncio
async def test_launched_browser_uses_discovered_websocket_url(monkeypatch):
    monkeypatch.setattr(config, "CDP_CONNECT_EXISTING", False)

    manager = CDPBrowserManager()
    manager.debug_port = 9223
    manager._get_browser_websocket_url = AsyncMock(  # type: ignore[method-assign]
        return_value="ws://localhost:9223/devtools/browser/generated-id"
    )

    browser = MagicMock()
    browser.is_connected.return_value = True
    browser.contexts = []

    playwright = MagicMock()
    playwright.chromium.connect_over_cdp = AsyncMock(return_value=browser)

    await manager._connect_via_cdp(playwright)

    manager._get_browser_websocket_url.assert_awaited_once_with(9223)
    playwright.chromium.connect_over_cdp.assert_awaited_once_with(
        "ws://localhost:9223/devtools/browser/generated-id"
    )

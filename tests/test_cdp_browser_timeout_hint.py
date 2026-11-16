# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests\test_cdp_browser_timeout_hint.py
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
async def test_existing_browser_attach_failure_explains_what_to_do(monkeypatch):
    monkeypatch.setattr(config, "CDP_CONNECT_EXISTING", True)
    monkeypatch.setattr(config, "BROWSER_LAUNCH_TIMEOUT", 60)

    manager = CDPBrowserManager()
    manager.debug_port = 9222
    manager._get_browser_websocket_url = AsyncMock(  # type: ignore[method-assign]
        side_effect=RuntimeError("HTTP 404: ")
    )

    direct_error = TimeoutError("connect_over_cdp: Timeout 60000ms exceeded.")
    playwright = MagicMock()
    playwright.chromium.connect_over_cdp = AsyncMock(side_effect=direct_error)

    with pytest.raises(RuntimeError) as exc_info:
        await manager._connect_via_cdp(playwright)

    message = str(exc_info.value)
    assert "port 9222 within 60s" in message
    assert "remote debugging dialog was not accepted" in message
    assert "tab or window is not responding" in message
    assert "Timeout 60000ms exceeded" in message
    assert "HTTP 404" in message
    assert exc_info.value.__cause__ is direct_error
    playwright.chromium.connect_over_cdp.assert_awaited_once()

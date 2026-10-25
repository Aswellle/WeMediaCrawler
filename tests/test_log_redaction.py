# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests/test_log_redaction.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
"""日志脱敏回归测试：cookies 值不得进入日志（日志经 /ws/logs 广播并重放给每个新连接）。"""
from api.schemas import CrawlerStartRequest
from api.services.crawler_manager import CrawlerManager


def test_redact_cmd_masks_cookies_value():
    config = CrawlerStartRequest(platform="xhs", cookies="SECRET_COOKIE_VALUE")
    cmd = CrawlerManager()._build_command(config)

    redacted = CrawlerManager._redact_cmd(cmd)

    # 日志可见形式不含 cookie 明文，且占位符就位
    assert "SECRET_COOKIE_VALUE" not in redacted
    assert "--cookies ***" in redacted


def test_redact_cmd_leaves_real_subprocess_command_intact():
    # 脱敏只作用于日志：真正交给子进程的 argv 仍包含完整值
    config = CrawlerStartRequest(platform="xhs", cookies="SECRET_COOKIE_VALUE")
    cmd = CrawlerManager()._build_command(config)

    assert "SECRET_COOKIE_VALUE" in " ".join(cmd)


def test_redact_cmd_without_sensitive_flags_is_identity():
    config = CrawlerStartRequest(platform="xhs", keywords="编程副业")
    cmd = CrawlerManager()._build_command(config)

    assert CrawlerManager._redact_cmd(cmd) == " ".join(cmd)

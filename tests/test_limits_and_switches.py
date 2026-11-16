# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests\test_limits_and_switches.py
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

"""流量与并发限制、开关的真实有效性回归测试。

- ENABLE_GET_COMMENTS=False：不得发起任何评论接口调用
- ENABLE_GET_SUB_COMMENTS=False：不得发起任何子评论接口调用
- MAX_CONCURRENCY_NUM：评论采集的实际同时在途数不得超过信号量上限
- CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES：作为 max_count 透传给 client
"""

from __future__ import annotations

from types import SimpleNamespace

import config
import pytest

from media_platform.xhs.client import XiaoHongShuClient
from media_platform.xhs.core import XiaoHongShuCrawler


def _bare_xhs_crawler() -> XiaoHongShuCrawler:
    crawler = XiaoHongShuCrawler()
    crawler.xhs_client = SimpleNamespace(proxy=None)
    crawler.user_agent = "limits-test-agent"
    return crawler


@pytest.mark.asyncio
async def test_comments_switch_off_makes_no_api_calls(monkeypatch):
    """评论开关关闭：client 的评论接口一次都不该被调用"""
    monkeypatch.setattr(config, "ENABLE_GET_COMMENTS", False)
    crawler = _bare_xhs_crawler()

    calls = []

    async def fake_get_note_all_comments(*args, **kwargs):
        calls.append(kwargs)
        return []

    crawler.xhs_client.get_note_all_comments = fake_get_note_all_comments

    await crawler.batch_get_note_comments(["note-1", "note-2"], ["t1", "t2"])

    assert calls == [], "评论开关关闭时不应调用评论接口"


@pytest.mark.asyncio
async def test_comments_max_count_passed_to_client(monkeypatch):
    """单条内容评论配额应原样透传给 client 的 max_count"""
    monkeypatch.setattr(config, "ENABLE_GET_COMMENTS", True)
    crawler = _bare_xhs_crawler()

    captured = {}

    async def fake_get_note_all_comments(*args, **kwargs):
        captured.update(kwargs)
        return []

    crawler.xhs_client.get_note_all_comments = fake_get_note_all_comments

    await crawler.batch_get_note_comments(["note-1"], ["t1"])

    assert captured.get("max_count") == config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES


@pytest.mark.asyncio
async def test_sub_comments_switch_off_makes_no_api_calls(monkeypatch):
    """子评论开关关闭：子评论接口一次都不该被调用"""
    monkeypatch.setattr(config, "ENABLE_GET_SUB_COMMENTS", False)
    client = XiaoHongShuClient.__new__(XiaoHongShuClient)

    sub_calls = []

    async def fake_get_note_sub_comments(*args, **kwargs):
        sub_calls.append(kwargs)
        return {"has_more": True, "cursor": "", "comments": [{"comment_id": "x"}]}

    monkeypatch.setattr(client, "get_note_sub_comments", fake_get_note_sub_comments)

    result = await client.get_comments_all_sub_comments(
        comments=[{"id": "root-1", "note_id": "n1",
                   "sub_comment_has_more": True, "sub_comment_cursor": ""}],
        xsec_token="tok",
        crawl_interval=0,
        callback=None,
        max_count=10,
    )

    assert result == [] and sub_calls == [], "子评论开关关闭时不应调用子评论接口"


@pytest.mark.asyncio
async def test_comment_concurrency_bounded_by_semaphore(monkeypatch):
    """评论采集的实际同时在途数不得超过 MAX_CONCURRENCY_NUM"""
    monkeypatch.setattr(config, "ENABLE_GET_COMMENTS", True)
    monkeypatch.setattr(config, "MAX_CONCURRENCY_NUM", 2)
    monkeypatch.setattr(config, "CRAWLER_MAX_SLEEP_SEC", 0)
    crawler = _bare_xhs_crawler()

    in_flight = 0
    peak = 0

    async def fake_get_note_all_comments(*args, **kwargs):
        nonlocal in_flight, peak
        in_flight += 1
        peak = max(peak, in_flight)
        import asyncio
        await asyncio.sleep(0.05)
        in_flight -= 1
        return []

    crawler.xhs_client.get_note_all_comments = fake_get_note_all_comments

    note_ids = [f"note-{i}" for i in range(8)]
    await crawler.batch_get_note_comments(note_ids, ["t"] * len(note_ids))

    assert peak <= config.MAX_CONCURRENCY_NUM, (
        f"评论采集峰值并发 {peak} 超过 MAX_CONCURRENCY_NUM={config.MAX_CONCURRENCY_NUM}"
    )
    assert peak > 1, "并发应确实发生（峰值>1），否则测试没有意义"


@pytest.mark.asyncio
async def test_note_detail_concurrency_bounded_by_semaphore(monkeypatch):
    """详情页并发同样受 MAX_CONCURRENCY_NUM 约束"""
    monkeypatch.setattr(config, "MAX_CONCURRENCY_NUM", 2)
    monkeypatch.setattr(config, "CRAWLER_MAX_SLEEP_SEC", 0)
    monkeypatch.setattr(config, "ENABLE_GET_COMMENTS", False)
    crawler = _bare_xhs_crawler()

    in_flight = 0
    peak = 0

    class FakeClient:
        proxy = None

        async def get_note_by_id(self, note_id, xsec_source, xsec_token):
            nonlocal in_flight, peak
            in_flight += 1
            peak = max(peak, in_flight)
            import asyncio
            await asyncio.sleep(0.05)
            in_flight -= 1
            return {"note_id": note_id, "type": "normal", "image_list": [],
                    "user": {}, "interact_info": {}, "tag_list": []}

    crawler.xhs_client = FakeClient()

    semaphore = __import__("asyncio").Semaphore(config.MAX_CONCURRENCY_NUM)
    tasks = [
        crawler.get_note_detail_async_task(
            note_id=f"n-{i}", xsec_source="pc_search", xsec_token="t", semaphore=semaphore,
        )
        for i in range(8)
    ]
    import asyncio
    await asyncio.gather(*tasks)

    assert peak <= config.MAX_CONCURRENCY_NUM, (
        f"详情页峰值并发 {peak} 超过 MAX_CONCURRENCY_NUM={config.MAX_CONCURRENCY_NUM}"
    )
    assert peak > 1

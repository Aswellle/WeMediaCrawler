# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests\test_comment_quota.py
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

"""评论采集配额回归测试。

max_count 的语义是"单条内容的评论总配额"（一级 + 子评论共享）。
此前子评论翻页不占配额：热门评论的数万条子评论会无视 max_count
一直翻页（实机测试发现）。这里用 mock 的分页接口锁定配额行为。
"""

from __future__ import annotations

import config
import pytest

from media_platform.weibo.client import WeiboClient
from media_platform.xhs.client import XiaoHongShuClient


def _bare_xhs_client() -> XiaoHongShuClient:
    """无需浏览器与网络的最小客户端实例（分页接口全部由测试注入）"""
    return XiaoHongShuClient.__new__(XiaoHongShuClient)


@pytest.mark.asyncio
async def test_xhs_sub_comments_share_quota(monkeypatch):
    """配额被一级评论与子评论共享：总存量不得超过 max_count"""
    monkeypatch.setattr(config, "ENABLE_GET_SUB_COMMENTS", True)
    client = _bare_xhs_client()
    sub_calls = []

    async def fake_root(note_id, xsec_token, cursor=""):
        return {"has_more": True, "cursor": "next",
                "comments": [{"id": f"root-{cursor}-{i}", "note_id": note_id,
                              "sub_comment_has_more": True, "sub_comment_cursor": ""}
                             for i in range(10)]}

    async def fake_sub(note_id, root_comment_id, xsec_token, num=10, cursor=""):
        sub_calls.append(root_comment_id)
        return {"has_more": True, "cursor": "next",
                "comments": [{"comment_id": f"{root_comment_id}-p{cursor}-{i}"}
                             for i in range(10)]}

    monkeypatch.setattr(client, "get_note_comments", fake_root)
    monkeypatch.setattr(client, "get_note_sub_comments", fake_sub)

    stored = []

    async def callback(note_id, comments):
        stored.extend(comments)

    total = await client.get_note_all_comments(
        note_id="n1", xsec_token="tok",
        crawl_interval=0, callback=callback, max_count=10,
    )

    assert len(stored) <= 10, f"回调入库的评论数超配额: {len(stored)}"
    assert len(total) <= 10, f"返回的评论数超配额: {len(total)}"
    assert len(stored) == 10, f"配额应被用满而不是提前放弃: {len(stored)}"


@pytest.mark.asyncio
async def test_xhs_quota_stops_after_sub_comment_fulfillment(monkeypatch):
    """子评论把配额用满后，一级评论翻页随之停止（此前子评论不记账，永不停止）"""
    monkeypatch.setattr(config, "ENABLE_GET_SUB_COMMENTS", True)
    client = _bare_xhs_client()
    root_calls = []

    async def fake_root(note_id, xsec_token, cursor=""):
        root_calls.append(cursor)
        return {"has_more": True, "cursor": f"c{len(root_calls)}",
                "comments": [{"id": f"root-{cursor}", "note_id": note_id,
                              "sub_comment_has_more": True, "sub_comment_cursor": ""}]}

    async def fake_sub(note_id, root_comment_id, xsec_token, num=10, cursor=""):
        return {"has_more": True, "cursor": f"s{cursor}",
                "comments": [{"comment_id": f"{root_comment_id}-{cursor}-{i}"}
                             for i in range(10)]}

    monkeypatch.setattr(client, "get_note_comments", fake_root)
    monkeypatch.setattr(client, "get_note_sub_comments", fake_sub)

    stored = []

    async def callback(note_id, comments):
        stored.extend(comments)

    total = await client.get_note_all_comments(
        note_id="n1", xsec_token="tok",
        crawl_interval=0, callback=callback, max_count=15,
    )

    assert len(stored) == 15, f"总存量应恰好等于配额: {len(stored)}"
    assert len(total) == 15


@pytest.mark.asyncio
async def test_weibo_inline_sub_comments_share_quota(monkeypatch):
    """微博内嵌子评论同样计入并受配额约束"""
    monkeypatch.setattr(config, "ENABLE_GET_SUB_COMMENTS", True)
    client = WeiboClient.__new__(WeiboClient)
    stored = []

    async def callback(note_id, comments):
        stored.extend(comments)

    comment_list = [
        {"id": f"root-{i}", "comments": [{"sub_id": f"{i}-{j}"} for j in range(3)]}
        for i in range(5)
    ]
    subs = await client.get_comments_all_sub_comments(
        "wb1", comment_list, callback, max_count=10,
    )

    # 可用 15 条内嵌子评论（5×3），配额 10 → 应恰好截断到 10
    assert len(subs) == 10, f"内嵌子评论应被截断到配额: {len(subs)}"
    assert len(stored) == 10

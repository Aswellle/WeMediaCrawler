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
from types import SimpleNamespace
from unittest.mock import AsyncMock

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


@pytest.mark.asyncio
async def test_zhihu_sub_comments_share_quota(monkeypatch):
    """知乎一级评论与子评论共享配额（此前完全忽略 max_count，实测 5 配额得 639 条）"""
    from model.m_zhihu import ZhihuComment, ZhihuContent
    from media_platform.zhihu.client import ZhiHuClient

    monkeypatch.setattr(config, "ENABLE_GET_SUB_COMMENTS", True)
    client = ZhiHuClient.__new__(ZhiHuClient)

    content = ZhihuContent(content_id="z1", content_type="article")
    stored = []

    async def callback(comments):
        stored.extend(comments)

    async def fake_root(content_id, content_type, offset, limit):
        return {
            "paging": {"is_end": False, "offset": f"next{offset}"},
            "data": [{"id": f"root-{offset}-{i}"} for i in range(10)],
        }

    async def fake_child(comment_id, offset, limit):
        return {
            "paging": {"is_end": False},
            "data": [{"id": f"{comment_id}-{i}"} for i in range(10)],
        }

    class FakeExtractor:
        def extract_offset(self, paging):
            return paging.get("offset", "")

        def extract_comments(self, content, data):
            return [ZhihuComment(comment_id=item["id"], sub_comment_count=3) for item in data or []]

    client._extractor = FakeExtractor()
    client.get_root_comments = fake_root
    client.get_child_comments = fake_child

    total = await client.get_note_all_comments(
        content=content, crawl_interval=0, callback=callback, max_count=7,
    )

    assert len(stored) == 7, f"配额应恰好用满: {len(stored)}"
    assert len(total) == 7


@pytest.mark.asyncio
async def test_douyin_sub_comments_share_quota(monkeypatch):
    """抖音子评论与一级评论共享配额（实机发现 3 配额抓出数千条子评论）"""
    from media_platform.douyin.client import DouYinClient

    monkeypatch.setattr(config, "ENABLE_GET_SUB_COMMENTS", True)
    client = DouYinClient.__new__(DouYinClient)

    stored = []

    async def callback(aweme_id, comments):
        stored.extend(comments)

    async def fake_root(aweme_id, cursor):
        return {"has_more": False, "cursor": 0,
                "comments": [{"cid": f"c{i}", "reply_comment_total": 5} for i in range(3)]}

    async def fake_sub(aweme_id, comment_id, cursor):
        return {"has_more": True, "cursor": int(cursor or 0) + 1,
                "comments": [{"cid": f"{comment_id}-s{cursor}-{i}"} for i in range(10)]}

    client.get_aweme_comments = fake_root
    client.get_sub_comments = fake_sub

    total = await client.get_aweme_all_comments(
        aweme_id="a1", crawl_interval=0,
        is_fetch_sub_comments=True, callback=callback, max_count=5,
    )

    assert len(stored) == 5, f"配额应恰好用满: {len(stored)}"
    assert len(total) == 5
    # 一级评论 3 条 + 子评论补足到 5；子评论翻页必须停在配额内


@pytest.mark.asyncio
async def test_tieba_sub_comments_share_quota(monkeypatch):
    """贴吧子评论（Playwright 翻页模式）同样受配额约束"""
    from model.m_baidu_tieba import TiebaComment, TiebaNote
    from media_platform.tieba.client import BaiduTieBaClient

    monkeypatch.setattr(config, "ENABLE_GET_SUB_COMMENTS", True)
    monkeypatch.setattr(config, "CRAWLER_MAX_SLEEP_SEC", 0)
    client = BaiduTieBaClient.__new__(BaiduTieBaClient)

    parent = TiebaComment(comment_id="p1", content="c", note_id="n1",
                          note_url="https://tieba/p/1", tieba_id="fid",
                          tieba_name="python", tieba_link="https://tieba/f?kw=python",
                          sub_comment_count=30)
    note = TiebaNote(note_id="n1", title="t", note_url="https://tieba/p/1",
                     tieba_name="python", tieba_link="https://tieba/f?kw=python")

    async def callback(note_id, comments):
        pass

    async def fake_page_comments(post_id, page):
        return [note]

    client._host = "https://tieba.baidu.com"
    client._page_extractor = SimpleNamespace(
        extract_tieba_note_sub_comments=lambda html, parent_comment: [
            TiebaComment(comment_id=f"{parent_comment.comment_id}-{i}", content="s",
                         note_id="n1", note_url="https://tieba/p/1", tieba_id="fid",
                         tieba_name="python", tieba_link="https://tieba/f?kw=python")
            for i in range(10)
        ]
    )
    client.playwright_page = SimpleNamespace(
        goto=AsyncMock(return_value=None),
        content=AsyncMock(return_value="<html></html>"),
    )

    async def fake_get_root(note_id, page):
        return [parent]

    # 直接测子评论方法本身的配额
    result = await client.get_comments_all_sub_comments(
        [parent], crawl_interval=0, callback=callback, max_count=7,
    )

    assert len(result) <= 7, f"子评论数超配额: {len(result)}"

# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests\test_media_summary.py
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

"""媒体目录笔记 CSV 摘要的回归测试。

真实调用 store 的更新函数（含 PII 脱敏），验证媒体目录中出现
summary.csv，且字段与导出数据一致、原始标识不落盘。
"""

from __future__ import annotations

import csv
from pathlib import Path

import config
import pytest

from var import crawler_type_var, source_keyword_var


@pytest.fixture
def summary_env(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(config, "SAVE_DATA_PATH", str(tmp_path))
    monkeypatch.setattr(config, "SAVE_DATA_OPTION", "jsonl")
    monkeypatch.setattr(config, "ENABLE_GET_MEDIA", True)
    monkeypatch.setattr(config, "ENABLE_GET_WORDCLOUD", False)
    crawler_type_var.set("search")
    source_keyword_var.set("summary-test")
    return tmp_path


@pytest.mark.asyncio
async def test_xhs_media_dir_contains_note_summary(summary_env):
    from store import xhs as xhs_store

    note = {
        "note_id": "xhs-summary-1", "type": "normal", "title": "摘要测试", "desc": "描述",
        "user": {"user_id": "xhs-raw-uid-77", "nickname": "摘要用户甲"},
        "interact_info": {"liked_count": "12", "collected_count": "3",
                          "comment_count": "2", "share_count": "1"},
        "image_list": [], "tag_list": [],
    }
    await xhs_store.update_xhs_note(note)

    summary_path = summary_env / "xhs" / "media" / "xhs-summary-1" / "summary.csv"
    assert summary_path.is_file(), f"媒体目录缺少摘要: {summary_path}"

    with open(summary_path, encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1
    row = rows[0]
    assert row["note_id"] == "xhs-summary-1"
    assert row["title"] == "摘要测试"
    assert row["creator_hash"] and row["creator_hash"] != "xhs-raw-uid-77"
    assert "*" in row["nickname"]
    blob = f"{rows[0]}"
    assert "xhs-raw-uid-77" not in blob and "摘要用户甲" not in blob, "原始标识不得进入摘要"


@pytest.mark.asyncio
async def test_summary_skipped_when_media_disabled(summary_env, monkeypatch):
    from store import xhs as xhs_store

    monkeypatch.setattr(config, "ENABLE_GET_MEDIA", False)
    note = {
        "note_id": "xhs-summary-off", "type": "normal", "title": "t", "desc": "d",
        "user": {"user_id": "u", "nickname": "n"},
        "interact_info": {}, "image_list": [], "tag_list": [],
    }
    await xhs_store.update_xhs_note(note)

    media_root = summary_env / "xhs" / "media"
    assert not media_root.exists(), "媒体下载关闭时不应产生媒体目录"


@pytest.mark.asyncio
@pytest.mark.parametrize("store_pkg, factory, cid_key, media_platform, payload", [
    ("douyin", "DouyinStoreFactory", "aweme_id", "dy", {"aweme_id": "dy-sum-1"}),
    ("kuaishou", "KuaishouStoreFactory", "video_id", "ks", None),
    ("bilibili", "BiliStoreFactory", "video_id", "bili", None),
    ("weibo", "WeibostoreFactory", "note_id", "wb", None),
])
async def test_summary_written_for_all_media_platforms(
    summary_env, store_pkg, factory, cid_key, media_platform, payload,
):
    from importlib import import_module

    store = import_module(f"store.{store_pkg}")
    if store_pkg == "douyin":
        content = {
            "aweme_id": "dy-sum-1", "aweme_type": 0, "desc": "d", "create_time": 1,
            "author": {"uid": "raw-1", "nickname": "n"},
            "statistics": {"digg_count": 1, "collect_count": 0,
                           "comment_count": 0, "share_count": 0},
            "video": {"play_addr_h264": {"url_list": ["https://cdn/dy.mp4"]},
                      "raw_cover": {"url_list": ["https://cdn/dy.jpg"]}},
            "music": {"play_url": {"uri": ""}},
        }
    elif store_pkg == "kuaishou":
        content = {
            "type": "video",
            "photo": {"id": "ks-sum-1", "caption": "c", "timestamp": 1,
                      "coverUrl": "https://cdn/ks.jpg", "photoUrl": "https://cdn/ks.mp4"},
            "author": {"id": "raw-2", "name": "n"},
        }
        cid, expected_id = "photo.id", "ks-sum-1"
    elif store_pkg == "bilibili":
        content = {
            "View": {"aid": 999, "bvid": "BV1sum", "title": "t", "desc": "d",
                     "pubdate": 1, "pic": "https://cdn/bili.jpg",
                     "owner": {"mid": 1, "name": "n"},
                     "stat": {"like": 1, "dislike": 0, "view": 1, "favorite": 0,
                              "share": 0, "coin": 0, "danmaku": 0, "reply": 0}},
        }
        cid, expected_id = None, "999"
    else:
        content = {
            "mblog": {"id": "wb-sum-1", "text": "正文",
                      "created_at": "Mon Nov 16 12:00:00 +0800 2026",
                      "user": {"id": "raw-3", "screen_name": "n"},
                      "attitudes_count": 1, "comments_count": 0, "reposts_count": 0},
        }
        cid, expected_id = "mblog.id", "wb-sum-1"

    if store_pkg == "douyin":
        await store.update_douyin_aweme(content)
        expected_id = "dy-sum-1"
    elif store_pkg == "kuaishou":
        await store.update_kuaishou_video(content)
    elif store_pkg == "bilibili":
        await store.update_bilibili_video(content)
    else:
        await store.update_weibo_note(content)

    summary_path = summary_env / media_platform / "media" / expected_id / "summary.csv"
    assert summary_path.is_file(), f"{store_pkg} 的媒体目录缺少摘要: {summary_path}"

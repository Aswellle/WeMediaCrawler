# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests\test_boundary_conditions.py
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

"""边界条件：非法输入、极端值、路径穿越、异常响应、空数据。

这些用例针对「真实生产里会出现但不常发生」的输入，锁定系统
不崩溃、不越过安全边界、不产生脏数据。
"""

from __future__ import annotations

from pathlib import Path

import config
import httpx
import pytest

from media_downloader import MediaDownloader, MediaItem, MediaType
from media_downloader.paths import build_media_dir, sanitize_component
from tests.media_server import DEFAULT_CONTENT, MediaTestServer, start_server


@pytest.fixture(scope="module")
def server():
    srv, _thread = start_server()
    yield srv
    srv.shutdown()
    srv.server_close()


@pytest.fixture(autouse=True)
def _reset(server):
    server.reset()


def _downloader(tmp_path: Path) -> MediaDownloader:
    return MediaDownloader(platform="xhs", base_dir=tmp_path, max_retries=1,
                           retry_base_delay=0, max_candidates=2)


# --------------------------------------------------------------------------- 路径安全


@pytest.mark.parametrize(
    ("raw", "forbidden"),
    [
        ("../../etc/passwd", ".."),
        ("..\\..\\windows\\system32", ".."),
        ("/absolute/path", "/"),
        ("C:\\Windows\\win.ini", ":"),
        ("....//....//x", ".."),
        ("con", None),  # Windows 保留设备名
        ("NUL", None),
        ("", None),
    ],
)
def test_sanitize_component_blocks_traversal(raw, forbidden):
    cleaned = sanitize_component(raw, "fallback")
    assert cleaned not in ("", ".", "..")
    if forbidden:
        assert forbidden not in cleaned
    assert not cleaned.startswith(".")
    assert all(ch.isalnum() or ch in "._-" for ch in cleaned), cleaned


def test_build_media_dir_stays_inside_base(tmp_path):
    base = tmp_path
    for malicious in ["../../escape", "..\\..\\escape", "/root/x"]:
        directory = build_media_dir(base, "xhs", malicious)
        resolved = directory.resolve()
        assert base.resolve() in resolved.parents, f"路径穿越: {resolved}"
        assert resolved.name not in ("", ".", "..")


@pytest.mark.asyncio
async def test_download_with_traversal_content_id_writes_inside_base(tmp_path, server):
    downloader = _downloader(tmp_path / "data")
    item = MediaItem(
        url=server.url("/ok/traversal"),
        media_type=MediaType.IMAGE,
        content_id="../../evil",
        stem="001",
    )
    path = await downloader.download(item)

    assert path is not None
    assert (tmp_path / "data").resolve() in path.resolve().parents
    assert path.stat().st_size == len(DEFAULT_CONTENT)


def test_unicode_and_emoji_content_id_is_sanitized():
    cleaned = sanitize_component("笔记🍜/../x?y", "fallback")
    assert cleaned
    assert "/" not in cleaned and "?" not in cleaned
    assert "🍜" not in cleaned


# --------------------------------------------------------------------------- 媒体下载异常响应


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [400, 403, 404, 429, 500, 502, 503])
async def test_download_never_raises_on_http_errors(tmp_path, server, status):
    downloader = _downloader(tmp_path)
    item = MediaItem(url=server.url(f"/status/{status}"), media_type=MediaType.IMAGE,
                     content_id="err", stem="001")

    assert await downloader.download(item) is None


@pytest.mark.asyncio
async def test_download_rejects_empty_url_and_bad_scheme(tmp_path):
    downloader = _downloader(tmp_path)
    for url in ["", "not-a-url", "ftp://example.com/x.jpg", "//cdn.example.com/x.jpg"]:
        item = MediaItem(url=url, media_type=MediaType.IMAGE, content_id="bad", stem="001")
        assert await downloader.download(item) is None


@pytest.mark.asyncio
async def test_zero_byte_existing_file_is_redownloaded(tmp_path, server):
    downloader = _downloader(tmp_path)
    item = MediaItem(url=server.url("/ok/redownload"), media_type=MediaType.IMAGE,
                     content_id="zero", stem="001")
    target = downloader.build_path(item)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"")  # 损坏的空文件

    path = await downloader.download(item)

    assert path is not None
    assert path.stat().st_size == len(DEFAULT_CONTENT), "0 字节文件应被视为损坏并重下"


@pytest.mark.asyncio
async def test_download_falls_back_to_backup_url(tmp_path, server):
    downloader = _downloader(tmp_path)
    item = MediaItem(
        url=server.url("/status/403"),
        backup_urls=(server.url("/ok/backup"),),
        media_type=MediaType.IMAGE,
        content_id="backup",
        stem="001",
    )

    path = await downloader.download(item)

    assert path is not None and path.stat().st_size == len(DEFAULT_CONTENT)


@pytest.mark.asyncio
async def test_truncated_response_does_not_leave_partial_file(tmp_path, server):
    downloader = _downloader(tmp_path)
    item = MediaItem(url=server.url("/truncated/x?fail=1"), media_type=MediaType.IMAGE,
                     content_id="trunc", stem="001")

    path = await downloader.download(item)

    # 要么完整成功，要么明确失败；不得留下半截成品文件
    if path is not None:
        assert path.stat().st_size == len(DEFAULT_CONTENT)
    assert not list((tmp_path / "xhs" / "media" / "trunc").glob("*.part"))


# --------------------------------------------------------------------------- 空数据 / 缺字段


@pytest.mark.asyncio
async def test_build_media_items_never_raises_on_garbage():
    from media_platform import bilibili, douyin, kuaishou, weibo, xhs

    # bilibili 没有图集提取器（仅封面/DASH/直链构建器），不参与本用例
    for module in (xhs.media, douyin.media, kuaishou.media, weibo.media):
        for garbage in ({}, {"id": None}, {"type": "video", "video": "oops"},
                        {"images": "not-a-list"}, {"image_list": [None, 1, ""]}):
            result = module.build_media_items(garbage)
            assert isinstance(result, list)


@pytest.mark.asyncio
async def test_store_update_ignores_missing_primary_id(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "SAVE_DATA_PATH", str(tmp_path))
    monkeypatch.setattr(config, "SAVE_DATA_OPTION", "jsonl")
    monkeypatch.setattr(config, "ENABLE_GET_MEDIA", False)
    from store import douyin, kuaishou, xhs

    # 缺主键时不得写文件、不得抛异常
    await xhs.update_xhs_note({"title": "无 ID"})
    await douyin.update_douyin_aweme({"desc": "无 ID"})
    await kuaishou.update_kuaishou_video({"photo": {}})

    assert not any(tmp_path.rglob("*.jsonl")), "缺主键的记录不应落盘"


@pytest.mark.asyncio
async def test_empty_keywords_does_not_crash(monkeypatch, tmp_path):
    """KEYWORDS 为空串时搜索循环不得崩溃"""
    from media_platform.xhs.core import XiaoHongShuCrawler

    monkeypatch.setattr(config, "KEYWORDS", "")
    monkeypatch.setattr(config, "CRAWLER_MAX_NOTES_COUNT", 20)
    monkeypatch.setattr(config, "CRAWLER_MAX_SLEEP_SEC", 0)

    crawler = XiaoHongShuCrawler()
    calls = []

    class FakeClient:
        proxy = None

        async def get_note_by_keyword(self, **kwargs):
            calls.append(kwargs)
            return {"has_more": False, "items": []}

    crawler.xhs_client = FakeClient()
    await crawler.search()

    assert len(calls) == 1 and calls[0]["keyword"] == ""


# --------------------------------------------------------------------------- 数值极值与超长文本


def test_very_long_values_are_truncated_by_store(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "SAVE_DATA_PATH", str(tmp_path))
    monkeypatch.setattr(config, "SAVE_DATA_OPTION", "jsonl")
    monkeypatch.setattr(config, "ENABLE_GET_MEDIA", False)
    from store import bilibili

    long_text = "x" * 5000
    content = {"View": {"aid": 1, "bvid": "BV1", "title": long_text, "desc": long_text,
                        "pubdate": 1, "pic": "",
                        "owner": {"mid": 1, "name": "n"},
                        "stat": {"like": 1, "dislike": 0, "view": 1, "favorite": 0,
                                 "share": 0, "coin": 0, "danmaku": 0, "reply": 0}}}
    import asyncio
    asyncio.run(bilibili.update_bilibili_video(content))

    import json
    files = list(tmp_path.rglob("*.jsonl"))
    assert files, "应产生导出文件"
    row = json.loads(files[0].read_text(encoding="utf-8").splitlines()[0])
    assert len(row["title"]) <= 500 and len(row["desc"]) <= 500


def test_extreme_counters_do_not_overflow_store(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "SAVE_DATA_PATH", str(tmp_path))
    monkeypatch.setattr(config, "SAVE_DATA_OPTION", "jsonl")
    monkeypatch.setattr(config, "ENABLE_GET_MEDIA", False)
    from store import xhs

    huge = 10 ** 18
    note = {"note_id": "huge-1", "type": "normal", "title": "t", "desc": "d",
            "user": {"user_id": "u", "nickname": "n"},
            "interact_info": {"liked_count": huge, "collected_count": huge,
                              "comment_count": huge, "share_count": huge},
            "image_list": [], "tag_list": []}
    import asyncio
    asyncio.run(xhs.update_xhs_note(note))

    import json
    row = json.loads(list(tmp_path.rglob("*.jsonl"))[0].read_text(encoding="utf-8").splitlines()[0])
    assert row["liked_count"] == huge


# --------------------------------------------------------------------------- 并发写同一文件


@pytest.mark.asyncio
async def test_concurrent_file_writes_do_not_corrupt_jsonl(monkeypatch, tmp_path):
    import asyncio
    import json

    monkeypatch.setattr(config, "SAVE_DATA_PATH", str(tmp_path))
    monkeypatch.setattr(config, "SAVE_DATA_OPTION", "jsonl")
    monkeypatch.setattr(config, "ENABLE_GET_MEDIA", False)
    from store import xhs

    async def write_one(index: int):
        await xhs.update_xhs_note({
            "note_id": f"c-{index}", "type": "normal", "title": "t", "desc": "d",
            "user": {"user_id": "u", "nickname": "n"},
            "interact_info": {}, "image_list": [], "tag_list": [],
        })

    await asyncio.gather(*[write_one(i) for i in range(30)])

    files = list(tmp_path.rglob("*.jsonl"))
    rows = [json.loads(line) for line in files[0].read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(rows) == 30, f"并发写入丢行: {len(rows)}"
    assert len({row["note_id"] for row in rows}) == 30


# --------------------------------------------------------------------------- 异常响应体


@pytest.mark.asyncio
async def test_download_survives_gzip_and_no_content_range(tmp_path, server):
    downloader = _downloader(tmp_path)
    for path in ["/gzip/g1", "/chunked/c1", "/no-range/r1"]:
        item = MediaItem(url=server.url(path), media_type=MediaType.IMAGE,
                         content_id="resp", stem=path.strip("/").replace("/", "_"))
        path_result = await downloader.download(item)
        assert path_result is not None and path_result.stat().st_size == len(DEFAULT_CONTENT), path


@pytest.mark.asyncio
async def test_download_rejects_206_without_content_range(tmp_path, server):
    """缺失 Content-Range 的 206 响应无法定位片段，应明确失败而不是写坏文件"""
    downloader = _downloader(tmp_path)
    item = MediaItem(url=server.url("/no-content-range/n1"), media_type=MediaType.IMAGE,
                     content_id="no-range", stem="001")

    assert await downloader.download(item) is None
    assert not list((tmp_path / "xhs" / "media" / "no-range").glob("*.part"))


@pytest.mark.asyncio
async def test_download_rejects_wrong_content_range(tmp_path, server):
    """服务端返回错位 Content-Range 时应丢弃片段重下，而不是写入错位数据"""
    downloader = _downloader(tmp_path)
    item = MediaItem(url=server.url("/wrong-range/w1?fail=1"), media_type=MediaType.IMAGE,
                     content_id="range", stem="001")

    result = await downloader.download(item)

    if result is not None:
        assert result.stat().st_size == len(DEFAULT_CONTENT)

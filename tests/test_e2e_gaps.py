# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests\test_e2e_gaps.py
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

"""端到端缺口补测（对应未覆盖清单 #15/#16/#6/#7/#10/#11/#13/#25/#26）。

- #15 重复爬取同一内容在各导出格式下的语义（文件格式追加、SQLite upsert）
- #16 Excel 公式注入防护
- #6  --start 起始页跳过逻辑
- #7  多关键词独立采集轮次
- #10 知乎 detail 按内容类型分发（article/answer/video）
- #11 B 站多分 P 直链：只下最大段并给出不完整提示
- #13 抖音 detail 短链解析贯通
- #25 爬虫运行中重复启动被拒绝
- #26 /ws/logs 连接时回放既有日志
"""

from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import config
import pytest

from var import crawler_type_var, source_keyword_var


def _recorder():
    async def record(*args, **kwargs):
        record.calls.append((args, kwargs))
        return []
    record.calls = []
    return record


def _noop():
    async def noop(*args, **kwargs):
        return []
    return noop


@pytest.fixture
def env(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "SAVE_DATA_PATH", str(tmp_path))
    monkeypatch.setattr(config, "ENABLE_GET_WORDCLOUD", False)
    monkeypatch.setattr(config, "CRAWLER_MAX_SLEEP_SEC", 0)
    monkeypatch.setattr(config, "MAX_CONCURRENCY_NUM", 1)
    monkeypatch.setattr(config, "START_PAGE", 1)
    monkeypatch.setattr(config, "KEYWORDS", "k1")
    monkeypatch.setattr(config, "ENABLE_GET_COMMENTS", False)
    monkeypatch.setattr(config, "ENABLE_GET_MEDIA", False)
    crawler_type_var.set("search")
    source_keyword_var.set("gaps")
    return tmp_path


# --------------------------------------------------------------------------- #15 重复爬取语义


@pytest.mark.asyncio
@pytest.mark.parametrize("save_option", ["csv", "json", "jsonl", "excel"])
async def test_recrawl_appends_in_file_formats(env, monkeypatch, save_option):
    """文件类格式为追加语义：重复爬取同一内容会产生两行（与 db 类 upsert 不同）。

    该用例锁定当前语义，提醒重复运行会积累重复行——去重应在分析侧完成
    或改用 sqlite/db 类导出。
    """
    from store.excel_store_base import ExcelStoreBase
    from store import xhs as xhs_store

    monkeypatch.setattr(config, "SAVE_DATA_OPTION", save_option)
    note = {
        "note_id": "dup-1", "type": "normal", "title": "t", "desc": "d",
        "user": {"user_id": "u", "nickname": "n"},
        "interact_info": {}, "image_list": [], "tag_list": [],
    }
    await xhs_store.update_xhs_note(note)
    await xhs_store.update_xhs_note(note)

    if save_option == "excel":
        ExcelStoreBase.flush_all()
        import openpyxl
        files = list(env.rglob("*.xlsx"))
        ws = openpyxl.load_workbook(files[0])["Contents"]
        data_rows = [r for r in ws.iter_rows(min_row=2, values_only=True) if any(r)]
        assert len(data_rows) == 2, "追加语义：应有两行相同内容"
    else:
        suffix = save_option
        import csv as csv_mod
        files = list(env.rglob(f"*contents*.{suffix}"))
        assert files, f"缺少 {suffix} 导出文件"
        if save_option == "csv":
            rows = list(csv_mod.DictReader(files[0].open(encoding="utf-8-sig")))
        elif save_option == "jsonl":
            rows = [json.loads(l) for l in files[0].read_text(encoding="utf-8").splitlines() if l.strip()]
        else:
            rows = json.loads(files[0].read_text(encoding="utf-8"))
            rows = rows if isinstance(rows, list) else [rows]
        assert len(rows) == 2, f"追加语义：应有两行相同内容，实际 {len(rows)}"
        assert rows[0]["note_id"] == rows[1]["note_id"] == "dup-1"


@pytest.mark.asyncio
async def test_recrawl_upserts_in_sqlite(env, monkeypatch):
    """sqlite 为 upsert 语义：重复爬取同一内容仍是一行（数据最新）"""
    import database.db_session as db_session
    from database import db as database_db
    from store import xhs as xhs_store

    monkeypatch.setattr(config, "SAVE_DATA_OPTION", "sqlite")
    monkeypatch.setattr("database.db_session.sqlite_db_config",
                        {"db_path": str(env / "sqlite.db")})
    db_session._engines.clear()
    await database_db.init_db("sqlite")

    note = {
        "note_id": "dup-2", "type": "normal", "title": "v1", "desc": "d",
        "user": {"user_id": "u", "nickname": "n"},
        "interact_info": {"liked_count": "1", "collected_count": "0",
                          "comment_count": "0", "share_count": "0",
                          "last_update_time": 1},
        "image_list": [], "tag_list": [],
    }
    await xhs_store.update_xhs_note(note)
    note2 = dict(note, title="v2", interact_info={"liked_count": "999",
                  "collected_count": "0", "comment_count": "0",
                  "share_count": "0", "last_update_time": 2})
    await xhs_store.update_xhs_note(note2)

    import sqlalchemy
    engine = db_session.get_async_engine("sqlite")
    async with engine.connect() as conn:
        result = await conn.execute(sqlalchemy.text(
            "SELECT title, liked_count FROM xhs_note"))
        rows = result.mappings().all()
    assert len(rows) == 1, "upsert 语义应只有一行"
    # update_content 只刷新互动计数等字段，标题保持首次入库值（产品语义）
    row = rows[0]
    assert row["title"] == "v1"
    assert row["liked_count"] == "999", f"计数应刷新为最新值: {row['liked_count']}"
    await engine.dispose()
    engine.dispose()


# --------------------------------------------------------------------------- #16 Excel 公式注入


@pytest.mark.asyncio
async def test_excel_formula_injection_neutralized(env, monkeypatch):
    """以 =/+/-/@ 开头的抓取文本写入 Excel 时必须转为字面文本"""
    from store.excel_store_base import ExcelStoreBase
    from store import xhs as xhs_store

    monkeypatch.setattr(config, "SAVE_DATA_OPTION", "excel")
    note = {
        "note_id": "inj-1", "type": "normal",
        "title": '=HYPERLINK("http://evil","click")',
        "desc": "+SUM(1,2)",
        "user": {"user_id": "u", "nickname": "-cmd"},
        "interact_info": {}, "image_list": [], "tag_list": [],
    }
    await xhs_store.update_xhs_note(note)
    ExcelStoreBase.flush_all()

    import openpyxl
    files = list(env.rglob("*.xlsx"))
    ws = openpyxl.load_workbook(files[0])["Contents"]
    header = [c for c in next(ws.iter_rows(min_row=1, max_row=1, values_only=True)) if c]
    for row in ws.iter_rows(min_row=2, values_only=True):
        record = dict(zip(header, row[:len(header)]))
        assert record["title"].startswith("'="), record["title"]
        assert record["desc"].startswith("'+"), record["desc"]
        assert record["nickname"].startswith("'-"), record["nickname"]


# --------------------------------------------------------------------------- #6 --start 起始页


@pytest.mark.asyncio
async def test_start_page_skips_earlier_pages(env, monkeypatch):
    """START_PAGE=2 时第 1 页不得发起任何请求，直接从第 2 页采集"""
    from media_platform.xhs.core import XiaoHongShuCrawler

    monkeypatch.setattr(config, "KEYWORDS", "k1")
    monkeypatch.setattr(config, "START_PAGE", 2)
    monkeypatch.setattr(config, "CRAWLER_MAX_NOTES_COUNT", 40)  # 页 2、3 会采集

    crawler = XiaoHongShuCrawler()
    crawler.xhs_client = SimpleNamespace(proxy=None)
    crawler.user_agent = "gaps-agent"
    requested_pages = []

    async def get_note_by_keyword(**kwargs):
        requested_pages.append(kwargs["page"])
        return {"has_more": True, "items": []}

    crawler.xhs_client.get_note_by_keyword = get_note_by_keyword
    monkeypatch.setattr(crawler, "download_media", _noop())
    monkeypatch.setattr(crawler, "batch_get_note_comments", _noop())

    await crawler.search()

    assert requested_pages == [2, 3], f"应跳过第 1 页直接从第 2 页开始: {requested_pages}"


# --------------------------------------------------------------------------- #7 多关键词


@pytest.mark.asyncio
async def test_multiple_keywords_independent_rounds(env, monkeypatch):
    """逗号分隔多关键词：每个关键词独立一轮，且 source_keyword 跟随当前轮"""
    from media_platform.xhs.core import XiaoHongShuCrawler

    monkeypatch.setattr(config, "KEYWORDS", "川菜,火锅")
    monkeypatch.setattr(config, "CRAWLER_MAX_NOTES_COUNT", 20)

    crawler = XiaoHongShuCrawler()
    crawler.xhs_client = SimpleNamespace(proxy=None)
    crawler.user_agent = "gaps-agent"
    rounds = []

    async def get_note_by_keyword(**kwargs):
        rounds.append((kwargs["keyword"], source_keyword_var.get()))
        return {"has_more": False, "items": []}

    crawler.xhs_client.get_note_by_keyword = get_note_by_keyword
    monkeypatch.setattr(crawler, "download_media", _noop())
    monkeypatch.setattr(crawler, "batch_get_note_comments", _noop())

    await crawler.search()

    assert [kw for kw, _ in rounds] == ["川菜", "火锅"]
    assert all(source == kw for kw, source in rounds), "每轮的 source_keyword 必须与关键词一致"


# --------------------------------------------------------------------------- #10 知乎内容类型分发


@pytest.mark.asyncio
async def test_zhihu_detail_dispatches_by_content_type(env, monkeypatch):
    """article/answer/video 三种 URL 分发到对应的 client 方法并正确入库"""
    from model.m_zhihu import ZhihuContent
    from media_platform.zhihu.core import ZhihuCrawler

    crawler = ZhihuCrawler()
    crawler.zhihu_client = SimpleNamespace(proxy=None, headers={})
    crawler.user_agent = "gaps-agent"
    stored = _recorder()

    crawler.zhihu_client.get_answer_info = AsyncMock(
        return_value=ZhihuContent(content_id="222", content_type="answer"))
    crawler.zhihu_client.get_article_info = AsyncMock(
        return_value=ZhihuContent(content_id="333", content_type="article"))
    crawler.zhihu_client.get_video_info = AsyncMock(
        return_value=ZhihuContent(content_id="444", content_type="zvideo"))
    monkeypatch.setattr("media_platform.zhihu.core.zhihu_store.update_zhihu_content", stored)
    monkeypatch.setattr(crawler, "batch_get_content_comments", _noop())

    monkeypatch.setattr(config, "ZHIHU_SPECIFIED_ID_LIST", [
        "https://www.zhihu.com/question/111/answer/222",
        "https://zhuanlan.zhihu.com/p/333",
        "https://www.zhihu.com/zvideo/444",
    ])

    await crawler.get_specified_notes()

    crawler.zhihu_client.get_answer_info.assert_awaited_once_with("111", "222")
    crawler.zhihu_client.get_article_info.assert_awaited_once_with("333")
    crawler.zhihu_client.get_video_info.assert_awaited_once_with("444")
    assert len(stored.calls) == 3
    assert {call[0][0].content_type for call in stored.calls} == {"answer", "article", "zvideo"}


# --------------------------------------------------------------------------- #11 B 站多分 P 直链


@pytest.mark.asyncio
async def test_bilibili_multisegment_durl_downloads_largest_only(env, monkeypatch, tmp_path):
    """直链被切多段时只下载体积最大的一段，并明确提示文件不完整"""
    import media_downloader.downloader as downloader_module
    import media_platform.bilibili.core as bili_core
    from media_platform.bilibili.core import BilibiliCrawler
    from tests.media_server import DEFAULT_CONTENT, MediaTestServer, start_server

    srv, _thread = start_server()
    try:
        monkeypatch.setattr(bili_core, "is_ffmpeg_available", lambda: False)
        monkeypatch.setattr(config, "ENABLE_GET_MEDIA", True)
        monkeypatch.setattr(config, "SAVE_DATA_PATH", str(tmp_path))
        monkeypatch.setattr(config, "CRAWLER_MAX_SLEEP_SEC", 0)

        crawler = BilibiliCrawler()
        crawler.bili_client = SimpleNamespace(proxy=None, headers={})
        crawler.user_agent = "gaps-agent"

        async def fake_play_url(aid, cid, semaphore, fnval=None):
            return {"durl": [
                {"url": srv.url("/ok/seg-small?ct=video/mp4"), "size": 100},
                {"url": srv.url("/ok/seg-large?ct=video/mp4"), "size": 999999},
            ]}

        monkeypatch.setattr(crawler, "get_video_play_url_task", fake_play_url)

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr("sys.stdout", __import__("io").StringIO())  # 静音日志不影响断言
            await crawler.download_media(
                {"View": {"aid": 1, "cid": 2, "bvid": "BV1multi", "pic": srv.url("/ok/cover")}},
                asyncio.Semaphore(1),
            )

        requested = srv.paths()
        assert any("seg-large" in p for p in requested), "应下载体积最大的分段"
        assert not any("seg-small" in p for p in requested), "小分段不应被下载"

        directory = tmp_path / "bili" / "media" / "BV1multi"
        files = sorted(p.name for p in directory.iterdir())
        assert "video-durl.mp4" in files, files
        assert (directory / "video-durl.mp4").stat().st_size == len(DEFAULT_CONTENT)
    finally:
        srv.shutdown()
        srv.server_close()


# --------------------------------------------------------------------------- #13 抖音短链贯通


@pytest.mark.asyncio
async def test_douyin_detail_resolves_short_url(env, monkeypatch):
    """--specified_id 传入 v.douyin.com 短链时：解析→提取 ID→取详情→入库"""
    from media_platform.douyin.core import DouYinCrawler

    crawler = DouYinCrawler()
    crawler.dy_client = SimpleNamespace(proxy=None, headers={})
    crawler.user_agent = "gaps-agent"
    stored = _recorder()

    resolve_calls = []

    async def resolve_short_url(url):
        resolve_calls.append(url)
        return "https://www.douyin.com/video/7280854932641664319"

    crawler.dy_client.resolve_short_url = resolve_short_url
    crawler.dy_client.get_video_by_id = AsyncMock(return_value={"aweme_id": "7280854932641664319"})
    monkeypatch.setattr(config, "DY_SPECIFIED_ID_LIST", ["https://v.douyin.com/iRABC/"])
    monkeypatch.setattr("media_platform.douyin.core.douyin_store.update_douyin_aweme", stored)
    monkeypatch.setattr(crawler, "download_media", _noop())
    monkeypatch.setattr(crawler, "batch_get_note_comments", _noop())

    await crawler.get_specified_awemes()

    assert resolve_calls == ["https://v.douyin.com/iRABC/"]
    crawler.dy_client.get_video_by_id.assert_awaited_once_with("7280854932641664319")
    assert len(stored.calls) == 1
    assert stored.calls[0][1]["aweme_item"]["aweme_id"] == "7280854932641664319"


# --------------------------------------------------------------------------- #25 重复启动互斥


@pytest.mark.asyncio
async def test_concurrent_crawler_start_rejected(monkeypatch):
    """已有爬虫进程运行时，第二次 /api/crawler/start 必须返回 400"""
    from fastapi.testclient import TestClient

    from api.main import app
    from api.services.crawler_manager import crawler_manager as manager_instance

    fake_process = SimpleNamespace(poll=lambda: None)  # poll()=None 表示进程存活
    monkeypatch.setattr(manager_instance, "start", AsyncMock(side_effect=[True, False]))
    monkeypatch.setattr(manager_instance, "process", fake_process)

    client = TestClient(app)
    payload = {"platform": "xhs", "keywords": "t"}

    first = client.post("/api/crawler/start", json=payload)
    assert first.status_code == 200

    second = client.post("/api/crawler/start", json=payload)
    assert second.status_code == 400
    assert "already running" in second.json()["detail"]


# --------------------------------------------------------------------------- #26 /ws/logs 回放


def test_ws_logs_replays_existing_logs():
    """连接 /ws/logs 时应先回放既有日志（新连接也能看到历史输出）"""
    from fastapi.testclient import TestClient

    from api.main import app
    from api.schemas.crawler import LogEntry
    from api.services.crawler_manager import crawler_manager as manager_instance

    entries = [
        LogEntry(id=1, timestamp="2026-01-01 00:00:00", level="info", message="hello-1"),
        LogEntry(id=2, timestamp="2026-01-01 00:00:01", level="error", message="boom-2"),
    ]

    client = TestClient(app)
    # 注意：包 __init__ 里 `from .crawler_manager import crawler_manager` 使
    # `from ..services import crawler_manager` 拿到的是实例而非子模块；
    # logs 是只读 property，须替换其数据源 _logs
    original = manager_instance._logs
    manager_instance._logs = entries
    try:
        with client.websocket_connect("/api/ws/logs") as ws:
            first = ws.receive_json()
            second = ws.receive_json()
        assert [first["message"], second["message"]] == ["hello-1", "boom-2"]
        assert first["level"] == "info" and second["level"] == "error"
    finally:
        manager_instance._logs = original


# --------------------------------------------------------------------------- 工具


def _noop():
    async def noop(*args, **kwargs):
        return []
    return noop

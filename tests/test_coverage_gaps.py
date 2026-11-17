# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests\test_coverage_gaps.py
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

"""剩余覆盖缺口（按类型分批）：存储正确性 / 编排边界 / 功能能力 / API 进程。

- #18 时间字段异常值（weibo created_at 为 None/非法串时 store 的行为）
- #17 超长内容 ID 在 DB 层（SQLite 不校验长度，MySQL 严格模式会拒绝）
- #19 跨天文件切换（get_current_date 变化时 jsonl/csv 按日期分文件）
- #21 DB 连接池回收后再次写入（SQLAlchemy dispose 后引擎仍可复用）
- #22 输出目录不可创建时（父路径被文件占用）的失败模式
- #20 CRAWLER_MAX_NOTES_COUNT 极大值的翻页终止
- #14 tieba 按贴吧名翻页采集（TIEBA_NAME_LIST 驱动）
- #9  weibo 全文抓取真实路径（isLongText -> 详情接口替换正文）
- #12 xhs 国际版分支（origin_video_key 跳过、master_url 兜底）
- #8  词云生成全链路（jsonl 评论 -> PNG 产出）
- #24 /api/crawler/start 真实子进程生命周期（启动/日志/停止/状态迁移）
- #28 构建产物托管渲染（WEBUI_DIR 指向构建目录后 / 返回前端页）
- #30 Ctrl-C 二次中断强制退出（app_runner 的 _force_stop 语义）
"""

from __future__ import annotations

import asyncio
import json
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock

import config
import pytest
import signal
from pathlib import Path

from tools.time_util import rfc2822_to_timestamp

REPO_ROOT = Path(__file__).resolve().parent.parent
from var import crawler_type_var, source_keyword_var


def _recorder():
    async def record(*args, **kwargs):
        record.calls.append((args, kwargs))
        return []
    record.calls = []
    return record


# --------------------------------------------------------------------------- #18 时间字段异常值


@pytest.mark.parametrize(
    ("created_at", "desc"),
    [
        (None, "缺失时间字段"),
        ("not-a-date", "非法格式"),
        ("", "空字符串"),
    ],
)
def test_weibo_invalid_created_at_behavior(created_at, desc):
    """weibo 时间字段异常时 rfc2822_to_timestamp 的行为：
    None/非法串会抛 ValueError——这是 store 层输入契约的一部分，
    提取层必须保证传入合法值；此处锁定解析函数的失败模式。"""
    if created_at is None:
        with pytest.raises(TypeError):
            rfc2822_to_timestamp(created_at)
    else:
        with pytest.raises(ValueError):
            rfc2822_to_timestamp(created_at)


@pytest.mark.asyncio
async def test_weibo_store_rejects_invalid_time_gracefully(monkeypatch, tmp_path):
    """created_at 异常时 update_weibo_note 抛 ValueError：
    说明脏时间字段会中断该条记录的入库——提取层已保证合法性，
    这里锁定行为以防未来有人静默吞掉（掩盖脏数据）。"""
    import pathlib

    from store import weibo as weibo_store

    monkeypatch.setattr(config, "SAVE_DATA_PATH", str(tmp_path))
    monkeypatch.setattr(config, "SAVE_DATA_OPTION", "jsonl")
    monkeypatch.setattr(config, "ENABLE_GET_MEDIA", False)

    note = {"mblog": {"id": "w-bad-time", "text": "t", "created_at": "not-a-date",
                      "user": {"id": "u", "screen_name": "n"}}}

    with pytest.raises(ValueError):
        await weibo_store.update_weibo_note(note)

    # 合法时间戳正常入库
    note_ok = {"mblog": {"id": "w-ok-time", "text": "t",
                         "created_at": "Mon Nov 16 12:00:00 +0800 2026",
                         "user": {"id": "u", "screen_name": "n"}}}
    await weibo_store.update_weibo_note(note_ok)
    files = list(tmp_path.rglob("*.jsonl"))
    assert files and any("w-ok-time" in f.read_text(encoding="utf-8") for f in files)
    assert not any("w-bad-time" in f.read_text(encoding="utf-8") for f in files)


# --------------------------------------------------------------------------- #17 超长内容 ID


@pytest.mark.asyncio
async def test_overlong_content_id_in_sqlite(monkeypatch, tmp_path):
    """SQLite 不校验 VARCHAR 长度：100 字符 ID 正常入库（MySQL 严格模式会拒绝，
    需在提取层截断——当前 sanitize_component 已有 MAX_COMPONENT_LENGTH 截断
    文件路径部分）。"""
    import sqlalchemy

    import database.db_session as db_session
    from database import db as database_db
    from store import xhs as xhs_store

    monkeypatch.setattr(config, "SAVE_DATA_PATH", str(tmp_path))
    monkeypatch.setattr(config, "SAVE_DATA_OPTION", "sqlite")
    monkeypatch.setattr(config, "ENABLE_GET_MEDIA", False)
    monkeypatch.setattr("database.db_session.sqlite_db_config",
                        {"db_path": str(tmp_path / "sqlite.db")})
    db_session._engines.clear()
    await database_db.init_db("sqlite")

    long_id = "x" * 100  # 超过 XhsNote.note_id 的 String(64)
    note = {"note_id": long_id, "type": "normal", "title": "t", "desc": "d",
            "user": {"user_id": "u", "nickname": "n"},
            "interact_info": {}, "image_list": [], "tag_list": []}
    await xhs_store.update_xhs_note(note)

    engine = db_session.get_async_engine("sqlite")
    async with engine.connect() as conn:
        result = await conn.execute(sqlalchemy.text(
            "SELECT COUNT(*) FROM xhs_note WHERE note_id = :nid"), {"nid": long_id})
        count = result.scalar()
    assert count == 1, "SQLite 不强制 VARCHAR 长度，超长 ID 应完整入库"
    await engine.dispose()


# --------------------------------------------------------------------------- #19 跨天文件切换


@pytest.mark.asyncio
async def test_file_name_rolls_over_at_date_change(monkeypatch, tmp_path):
    """长跑跨天：get_current_date 变化后写入新日期文件，旧文件保留"""
    from store import xhs as xhs_store

    monkeypatch.setattr(config, "SAVE_DATA_PATH", str(tmp_path))
    monkeypatch.setattr(config, "SAVE_DATA_OPTION", "jsonl")
    monkeypatch.setattr(config, "ENABLE_GET_MEDIA", False)

    import tools.async_file_writer as afw

    monkeypatch.setattr(afw.utils, "get_current_date", lambda: "2026-01-01")
    await xhs_store.update_xhs_note({
        "note_id": "day1", "type": "normal", "title": "t", "desc": "d",
        "user": {"user_id": "u", "nickname": "n"},
        "interact_info": {}, "image_list": [], "tag_list": [],
    })

    monkeypatch.setattr(afw.utils, "get_current_date", lambda: "2026-01-02")
    await xhs_store.update_xhs_note({
        "note_id": "day2", "type": "normal", "title": "t", "desc": "d",
        "user": {"user_id": "u", "nickname": "n"},
        "interact_info": {}, "image_list": [], "tag_list": [],
    })

    files = sorted(p.name for p in tmp_path.rglob("*.jsonl"))
    assert any("2026-01-01" in name for name in files), files
    assert any("2026-01-02" in name for name in files), files
    day1 = next(p for p in tmp_path.rglob("*.jsonl") if "2026-01-01" in p.name)
    day2 = next(p for p in tmp_path.rglob("*.jsonl") if "2026-01-02" in p.name)
    assert "day1" in day1.read_text(encoding="utf-8")
    assert "day2" in day2.read_text(encoding="utf-8")
    assert "day1" not in day2.read_text(encoding="utf-8"), "跨天后旧记录不应写入新文件"


# --------------------------------------------------------------------------- #21 DB 连接池回收


@pytest.mark.asyncio
async def test_store_survives_engine_pool_disposal(monkeypatch, tmp_path):
    """引擎池被 dispose（模拟空闲回收/DB 重启）后，再次写入应自动建立新连接"""
    import sqlalchemy

    import database.db_session as db_session
    from database import db as database_db
    from store import xhs as xhs_store

    monkeypatch.setattr(config, "SAVE_DATA_PATH", str(tmp_path))
    monkeypatch.setattr(config, "SAVE_DATA_OPTION", "sqlite")
    monkeypatch.setattr(config, "ENABLE_GET_MEDIA", False)
    monkeypatch.setattr("database.db_session.sqlite_db_config",
                        {"db_path": str(tmp_path / "sqlite.db")})
    db_session._engines.clear()
    await database_db.init_db("sqlite")

    async def write(note_id: str):
        await xhs_store.update_xhs_note({
            "note_id": note_id, "type": "normal", "title": "t", "desc": "d",
            "user": {"user_id": "u", "nickname": "n"},
            "interact_info": {}, "image_list": [], "tag_list": [],
        })

    await write("before-dispose")
    engine = db_session.get_async_engine("sqlite")
    await engine.dispose()  # 模拟连接池被清空/数据库重启

    await write("after-dispose")  # 引擎复用时应重建连接

    async with engine.connect() as conn:
        result = await conn.execute(sqlalchemy.text(
            "SELECT COUNT(*) FROM xhs_note"))
        count = result.scalar()
    assert count == 2, count
    await engine.dispose()


# --------------------------------------------------------------------------- #22 不可写输出目录


@pytest.mark.asyncio
async def test_unwritable_save_path_fails_loudly(monkeypatch, tmp_path):
    """输出目录父路径被文件占用导致 mkdir 失败时：
    存储层直接抛错（数据丢失风险高于静默吞错），错误可定位到路径问题"""
    from store import xhs as xhs_store

    blocked = tmp_path / "blocker"  # 把目录名变成一个文件，使其下的子目录无法创建
    blocked.write_bytes(b"occupied")
    save_path = blocked / "data" / "xhs"

    monkeypatch.setattr(config, "SAVE_DATA_PATH", str(save_path))
    monkeypatch.setattr(config, "SAVE_DATA_OPTION", "jsonl")
    monkeypatch.setattr(config, "ENABLE_GET_MEDIA", False)

    note = {"note_id": "x", "type": "normal", "title": "t", "desc": "d",
            "user": {"user_id": "u", "nickname": "n"},
            "interact_info": {}, "image_list": [], "tag_list": []}

    with pytest.raises(OSError):
        await xhs_store.update_xhs_note(note)


# --------------------------------------------------------------------------- #20 极大数量上限


@pytest.mark.asyncio
async def test_huge_notes_count_terminates_cleanly(monkeypatch):
    """CRAWLER_MAX_NOTES_COUNT=10000：循环按页数终止（500 页后停），不崩溃不无限"""
    from media_platform.xhs.core import XiaoHongShuCrawler

    monkeypatch.setattr(config, "KEYWORDS", "k1")
    monkeypatch.setattr(config, "START_PAGE", 1)
    monkeypatch.setattr(config, "CRAWLER_MAX_NOTES_COUNT", 10000)
    monkeypatch.setattr(config, "CRAWLER_MAX_SLEEP_SEC", 0)

    crawler = XiaoHongShuCrawler()
    crawler.xhs_client = SimpleNamespace(proxy=None)
    crawler.user_agent = "gaps-agent"
    calls = []

    async def get_note_by_keyword(**kwargs):
        calls.append(kwargs["page"])
        return {"has_more": True, "items": []}  # 永远有更多，靠页数上限终止

    crawler.xhs_client.get_note_by_keyword = get_note_by_keyword
    crawler.download_media = _noop_recorder()
    crawler.batch_get_note_comments = _noop_recorder()

    await crawler.search()

    assert len(calls) == 500, f"10000/20=500 页，实际 {len(calls)}"
    assert calls[0] == 1 and calls[-1] == 500


def _noop_recorder():
    async def noop(*args, **kwargs):
        return []
    noop.calls = []
    return noop


# --------------------------------------------------------------------------- #14 tieba 按贴吧名翻页


@pytest.mark.asyncio
async def test_tieba_tieba_name_paged_collection(monkeypatch):
    """TIEBA_NAME_LIST 驱动的按贴吧翻页：每页提取 note_id 后走指定 ID 详情链路"""
    from model.m_baidu_tieba import TiebaNote
    from media_platform.tieba.core import TieBaCrawler

    monkeypatch.setattr(config, "TIEBA_NAME_LIST", ["python"])
    monkeypatch.setattr(config, "TIEBA_SPECIFIED_ID_LIST", [])
    monkeypatch.setattr(config, "CRAWLER_MAX_NOTES_COUNT", 10)
    monkeypatch.setattr(config, "CRAWLER_MAX_SLEEP_SEC", 0)

    crawler = TieBaCrawler()
    crawler.tieba_client = SimpleNamespace(proxy=None)
    crawler.user_agent = "gaps-agent"
    stored, commented = _recorder(), _recorder()
    note = TiebaNote(note_id="tb-p1", title="贴", note_url="https://tieba/p/1",
                     tieba_name="python", tieba_link="https://tieba/f?kw=python")

    async def get_notes_by_tieba_name(**kwargs):
        assert kwargs["tieba_name"] == "python"
        return [note]

    crawler.tieba_client.get_notes_by_tieba_name = get_notes_by_tieba_name
    crawler.tieba_client.get_note_by_id = AsyncMock(return_value=note)
    monkeypatch.setattr("media_platform.tieba.core.tieba_store.update_tieba_note", stored)
    monkeypatch.setattr(crawler, "batch_get_note_comments", commented)

    await crawler.get_specified_tieba_notes()

    assert len(stored.calls) >= 1
    assert stored.calls[0][0][0].note_id == "tb-p1"


# --------------------------------------------------------------------------- #9 weibo 全文抓取


@pytest.mark.asyncio
async def test_weibo_full_text_replaces_truncated_content(monkeypatch):
    """isLongText=True 的微博：经详情接口取全文后替换正文再入库"""
    from media_platform.weibo.core import WeiboCrawler

    monkeypatch.setattr(config, "ENABLE_WEIBO_FULL_TEXT", True)

    crawler = WeiboCrawler()
    crawler.wb_client = SimpleNamespace(proxy=None)
    crawler.user_agent = "gaps-agent"

    truncated = {"mblog": {"id": "w-long", "text": "截断…", "isLongText": True,
                           "created_at": "Mon Nov 16 12:00:00 +0800 2026",
                           "user": {"id": "u", "screen_name": "n"}}}
    full = {"mblog": {"id": "w-long", "text": "完整正文" * 50,
                      "created_at": "Mon Nov 16 12:00:00 +0800 2026",
                      "user": {"id": "u", "screen_name": "n"}}}

    async def get_note_info_by_id(note_id):
        assert note_id == "w-long"
        return full

    crawler.wb_client.get_note_info_by_id = get_note_info_by_id

    result = await crawler.batch_get_notes_full_text([truncated])

    assert len(result) == 1
    assert result[0]["mblog"]["text"].startswith("完整正文"), "正文应被全文替换"


@pytest.mark.asyncio
async def test_weibo_full_text_skips_short_posts(monkeypatch):
    """isLongText=False 的微博不发起详情请求"""
    from media_platform.weibo.core import WeiboCrawler

    monkeypatch.setattr(config, "ENABLE_WEIBO_FULL_TEXT", True)

    crawler = WeiboCrawler()
    crawler.wb_client = SimpleNamespace(proxy=None)
    crawler.wb_client.get_note_info_by_id = AsyncMock(side_effect=AssertionError("短文不应请求详情"))

    short = {"mblog": {"id": "w-short", "text": "短文", "isLongText": False}}
    result = await crawler.batch_get_notes_full_text([short])

    assert result[0]["mblog"]["text"] == "短文"


# --------------------------------------------------------------------------- #12 xhs 国际版


@pytest.mark.asyncio
async def test_xhs_international_skips_origin_video_key(monkeypatch, tmp_path):
    """国际版（rednote）CDN 域名不同：origin_video_key 必须被跳过，
    回退到 stream 的 master_url；国内版则拼接 origin_video_key 优先"""
    from tests.media_server import MediaTestServer, start_server
    from media_platform.xhs.core import XiaoHongShuCrawler
    import media_platform.xhs.media as xhs_media

    srv, _thread = start_server()
    try:
        monkeypatch.setattr(config, "SAVE_DATA_PATH", str(tmp_path))
        monkeypatch.setattr(config, "SAVE_DATA_OPTION", "jsonl")
        monkeypatch.setattr(config, "ENABLE_GET_MEDIA", True)
        monkeypatch.setattr(config, "ENABLE_GET_COMMENTS", False)
        monkeypatch.setattr(config, "CRAWLER_MAX_SLEEP_SEC", 0)
        # 把国内版无水印 CDN 域名钉到本地服务器，使 origin key 路径可离线验证
        monkeypatch.setattr("media_platform.xhs.media.XHS_VIDEO_CDN_HOST",
                            srv.url("/origin"))

        note = {
            "note_id": "xhs-intl-1", "type": "video",
            "image_list": [],
            "video": {
                "consumer": {"origin_video_key": "spec/abc/key123"},
                "media": {"stream": {"h264": [
                    {"master_url": srv.url("/ok/intl-master?ct=video/mp4")}]}},
                "cover": {"url_default": srv.url("/ok/intl-cover")},
            },
        }

        async def run_case(international: bool, note_id: str):
            srv.reset()
            monkeypatch.setattr(config, "XHS_INTERNATIONAL", international)
            crawler = XiaoHongShuCrawler()
            crawler.xhs_client = SimpleNamespace(proxy=None)
            crawler.user_agent = "gaps-agent"
            payload = dict(note, note_id=note_id)
            await crawler.download_media(payload)

        # 国内版：优先拼接 origin_video_key（404 后回退 master，但 origin 请求已发生）
        await run_case(False, "xhs-dom-1")
        paths = srv.paths()
        assert any("/spec/abc/key123" in p for p in paths), paths

        # 国际版：跳过 origin_video_key，直接走 master_url
        await run_case(True, "xhs-intl-1")
        paths = srv.paths()
        assert not any("/spec/abc/key123" in p for p in paths), paths
        assert any("intl-master" in p for p in paths), paths
    finally:
        srv.shutdown()
        srv.server_close()


# --------------------------------------------------------------------------- #8 词云生成


@pytest.mark.asyncio
async def test_wordcloud_generated_from_comment_file(monkeypatch, tmp_path):
    """ENABLE_GET_WORDCLOUD 开启：从 jsonl 评论生成词云图"""
    import json

    from tools.async_file_writer import AsyncFileWriter

    monkeypatch.setattr(config, "ENABLE_GET_WORDCLOUD", True)
    monkeypatch.setattr(config, "ENABLE_GET_COMMENTS", True)
    monkeypatch.setattr(config, "SAVE_DATA_PATH", str(tmp_path))
    monkeypatch.setattr(config, "SAVE_DATA_OPTION", "jsonl")

    writer = AsyncFileWriter(platform="xhs", crawler_type="search")
    words = ["爬虫", "数据采集", "自媒体", "小红书", "Python"]
    for i in range(30):
        await writer.write_to_jsonl(
            {"content": words[i % len(words)], "nickname": f"n{i}"},
            item_type="comments",
        )

    await writer.generate_wordcloud_from_comments()

    pngs = list((tmp_path / "xhs" / "words").glob("*.png"))
    assert pngs, f"词云图片应生成: {sorted(p.name for p in (tmp_path / 'xhs').rglob('*'))}"
    assert pngs[0].stat().st_size > 0


# --------------------------------------------------------------------------- #24 真实子进程生命周期


@pytest.mark.asyncio
async def test_crawler_manager_real_process_lifecycle(monkeypatch):
    """启动真实子进程：状态迁移 idle->running->stopping->idle，日志被采集，停止后进程退出"""
    import sys

    from api.services.crawler_manager import crawler_manager

    manager = crawler_manager
    original_command = manager._build_command
    original_logs = manager._logs

    def fake_build_command(cfg):
        # 用无害命令替代真实爬虫，验证进程编排本身
        return [sys.executable, "-c",
                "print('SMOKE-STARTED', flush=True); import time; time.sleep(60)"]

    manager._build_command = fake_build_command
    manager._logs = []
    try:
        from api.schemas.crawler import CrawlerStartRequest
        started = await manager.start(
            CrawlerStartRequest(platform="xhs", keywords="t", headless=True))
        assert started is True
        assert manager.status == "running"
        assert manager.process and manager.process.poll() is None

        # 等子进程输出被读取
        for _ in range(40):
            if any("SMOKE-STARTED" in log.message for log in manager.logs):
                break
            await asyncio.sleep(0.25)
        assert any("SMOKE-STARTED" in log.message for log in manager.logs), \
            [log.message for log in manager.logs][-5:]

        stopped = await manager.stop()
        assert stopped is True
        assert manager.status == "idle"
        assert manager.process.poll() is not None, "停止后子进程必须退出"
        assert manager.current_config is None
    finally:
        manager._build_command = original_command
        manager._logs = original_logs
        if manager.process and manager.process.poll() is None:
            manager.process.kill()


@pytest.mark.asyncio
async def test_manager_start_failure_sets_error_status(monkeypatch, tmp_path):
    """可执行文件不存在导致 Popen 抛错时：状态置 error 且返回 False"""
    from api.schemas.crawler import CrawlerStartRequest
    from api.services.crawler_manager import crawler_manager

    manager = crawler_manager
    original_command = manager._build_command
    original_logs = manager._logs
    missing_exe = tmp_path / "missing-executable.exe"
    manager._build_command = lambda cfg: [str(missing_exe)]
    manager._logs = []
    try:
        started = await manager.start(
            CrawlerStartRequest(platform="xhs", keywords="t"))
        assert started is False
        assert manager.status == "error"
    finally:
        manager._build_command = original_command
        manager._logs = original_logs


# --------------------------------------------------------------------------- #28 构建产物托管渲染


def test_webui_static_serving_from_build_dir(monkeypatch):
    """WEBUI_DIR 指向构建产物目录时，/ 返回前端页面"""
    from fastapi.testclient import TestClient

    from api.main import WEBUI_DIR, app

    build_dir = REPO_ROOT / "gh-pages-dist"
    if not (build_dir / "index.html").exists():
        pytest.skip("构建产物不存在（gh-pages-dist/），跳过静态托管验证")

    monkeypatch.setattr("api.main.WEBUI_DIR", str(build_dir))
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    body = response.text
    assert "<div id=\"root\">" in body or "assets/" in body, "应返回前端入口 HTML"


# --------------------------------------------------------------------------- #30 Ctrl-C 语义


def test_cleanup_timeout_does_not_hang():
    """清理超时（cleanup_timeout_seconds）必须生效，不能无限等待"""
    import asyncio

    from tools.app_runner import run

    async def slow_cleanup():
        await asyncio.sleep(60)

    async def quick_main():
        return

    # cleanup 60s 但超时阈值 0.1s：run 必须在远小于 60s 内返回
    import time
    started = time.monotonic()
    run(quick_main, slow_cleanup, cleanup_timeout_seconds=0.1)
    elapsed = time.monotonic() - started
    assert elapsed < 10, f"清理超时未生效，耗时 {elapsed:.1f}s"


def test_single_ctrl_c_graceful_shutdown():
    """第一次 Ctrl-C：on_first_interrupt -> 取消主任务 -> 清理 -> 正常退出(0)

    Windows 下父进程无法向子进程投递可被 app_runner 处理的信号
    （SIGTERM 会变成 TerminateProcess，CTRL_C_EVENT 会波及整个控制台），
    因此由子进程内 signal.raise_signal 自触发，直达注册的处理器。"""
    import os
    import subprocess
    import textwrap

    child_script = textwrap.dedent(f"""
        import asyncio, signal, sys, threading, time
        sys.path.insert(0, r"{REPO_ROOT}")
        from tools.app_runner import run

        async def main():
            print("APP-STARTED", flush=True)
            await asyncio.sleep(60)

        async def cleanup():
            print("CLEANUP-DONE", flush=True)

        def first_interrupt():
            print("FIRST-INTERRUPT", flush=True)

        def raise_later():
            time.sleep(0.8)
            signal.raise_signal(signal.SIGINT)

        threading.Thread(target=raise_later, daemon=True).start()
        run(main, cleanup, cleanup_timeout_seconds=5, on_first_interrupt=first_interrupt)
    """)
    script_path = tmp_dir_marker() / "ctrl_c_child.py"
    script_path.write_text(child_script, encoding="utf-8")

    process = subprocess.Popen(
        [sys.executable, str(script_path)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    try:
        output = process.communicate(timeout=30)[0]
        assert process.returncode == 0, f"优雅退出应为 0: {process.returncode} | {output}"
        assert "FIRST-INTERRUPT" in output, output
        assert "CLEANUP-DONE" in output, output
        assert "Received interrupt signal" in output, output
    finally:
        if process.poll() is None:
            process.kill()


def test_double_ctrl_c_force_exit():
    """清理窗口内第二次 Ctrl-C：os._exit(130) 强制退出，清理不完成"""
    import os
    import subprocess
    import textwrap

    child_script = textwrap.dedent(f"""
        import asyncio, signal, sys, threading, time
        sys.path.insert(0, r"{REPO_ROOT}")
        sys.stdout.reconfigure(line_buffering=True)  # os._exit 不会刷新缓冲
        from tools.app_runner import run

        async def main():
            print("APP-STARTED", flush=True)
            await asyncio.sleep(60)

        async def cleanup():
            print("CLEANUP-STARTED", flush=True)
            await asyncio.sleep(20)
            print("CLEANUP-DONE", flush=True)

        def raise_twice():
            time.sleep(0.8)
            signal.raise_signal(signal.SIGINT)
            time.sleep(1.0)
            signal.raise_signal(signal.SIGINT)

        threading.Thread(target=raise_twice, daemon=True).start()
        run(main, cleanup, cleanup_timeout_seconds=30)
    """)
    script_path = tmp_dir_marker() / "double_ctrl_c_child.py"
    script_path.write_text(child_script, encoding="utf-8")

    process = subprocess.Popen(
        [sys.executable, str(script_path)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    try:
        output = process.communicate(timeout=40)[0]
        assert process.returncode == 130, f"二次中断应强制退出 130: {process.returncode} | {output}"
        assert "force exit" in output, output
        assert "CLEANUP-DONE" not in output, "强制退出不应完成清理"
    finally:
        if process.poll() is None:
            process.kill()


def tmp_dir_marker() -> Path:
    import tempfile
    d = Path(tempfile.mkdtemp(prefix="mc-signal-"))
    return d


# --------------------------------------------------------------------------- 工具


def _noop_recorder():
    async def noop(*args, **kwargs):
        return []
    noop.calls = []
    return noop

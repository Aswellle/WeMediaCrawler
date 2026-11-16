# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests\test_store_export_matrix.py
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

"""导出格式 × 平台的真实写入矩阵。

对每个平台执行真实的 ``update_<platform>_*`` 存储函数（含 PII 脱敏），
覆盖全部本地可用的导出格式并回读校验：

- 文件格式：csv / json / jsonl / excel（真实文件写入 + 回读）
- 数据库：sqlite（真实驱动）、db=MySQL 与 postgres（服务可达时走真实驱动，
  否则注入 sqlite 引擎验证同一套 Db 存储业务逻辑）、mongodb（服务可达时验证）
- PII 断言：creator_hash 必须等于原始 ID 的匿名哈希，昵称必须脱敏，
  原始 ID / 昵称不得出现在任何落盘记录中
"""

from __future__ import annotations

import csv
import json
import socket
import os
from pathlib import Path

import config
import pytest
import sqlalchemy

import database.db_session as db_session
from database import db as database_db
from database.models import Base
from tools.user_hash import anonymize_user_id, mask_nickname
from var import crawler_type_var, source_keyword_var

MYSQL_PORT = int(os.getenv("MATRIX_MYSQL_PORT", "3307"))
POSTGRES_PORT = int(os.getenv("MATRIX_POSTGRES_PORT", "5433"))
MONGO_PORT = int(os.getenv("MATRIX_MONGO_PORT", "27017"))

PLATFORMS = ["xhs", "dy", "ks", "bili", "wb", "tieba", "zhihu"]

# 各存储实现的落盘目录名（AsyncFileWriter/ExcelStoreBase 的 platform 参数）
_FILE_DIR = {"xhs": "xhs", "dy": "douyin", "ks": "kuaishou", "bili": "bili",
             "wb": "weibo", "tieba": "tieba", "zhihu": "zhihu"}
_EXCEL_DIR = {"xhs": "xhs", "dy": "douyin", "ks": "kuaishou", "bili": "bilibili",
              "wb": "weibo", "tieba": "tieba", "zhihu": "zhihu"}
# 内容类文件的 item_type（B 站内容按 videos 命名，其余平台为 contents）
_CONTENT_ITEM_TYPE = {"bili": "videos"}


def _port_open(host: str, port: int) -> bool:
    sock = socket.socket()
    sock.settimeout(1.0)
    try:
        sock.connect((host, port))
        return True
    except OSError:
        return False
    finally:
        sock.close()


# --------------------------------------------------------------------------- fixtures


@pytest.fixture
def storage_env(monkeypatch, tmp_path: Path):
    """隔离存储环境：落盘指向临时目录、ContextVar 就位、引擎缓存清空"""
    monkeypatch.setattr(config, "SAVE_DATA_PATH", str(tmp_path))
    monkeypatch.setattr(config, "ENABLE_GET_WORDCLOUD", False)
    monkeypatch.setattr(config, "CRAWLER_MAX_SLEEP_SEC", 0)
    crawler_type_var.set("search")
    source_keyword_var.set("matrix-test")
    db_session._engines.clear()
    yield tmp_path
    db_session._engines.clear()
    from store.excel_store_base import ExcelStoreBase
    ExcelStoreBase._instances.clear()


# --------------------------------------------------------------------------- 平台用例


def _build_case(platform: str) -> dict:
    raw_uid, raw_nick = {
        "xhs": ("xhs-raw-uid-1", "小红书用户甲"),
        "dy": ("dy-raw-uid-1", "抖音用户甲"),
        "ks": ("ks-raw-uid-1", "快手用户甲"),
        "bili": ("333", "B站UP主甲"),
        "wb": ("wb-raw-uid-1", "微博用户甲"),
        "tieba": ("tieba-raw-uid-1", "贴吧用户甲"),
        "zhihu": ("zhihu-raw-uid-1", "知乎用户甲"),
    }[platform]
    c_uid, c_nick = {
        "xhs": ("xhs-raw-uid-2", "小红书评论用户乙"),
        "dy": ("dy-raw-uid-2", "抖音评论用户乙"),
        "ks": ("ks-raw-uid-2", "快手评论用户乙"),
        "bili": ("444", "B站评论用户乙"),
        "wb": ("wb-raw-uid-2", "微博评论用户乙"),
        "tieba": ("tieba-raw-uid-2", "贴吧评论用户乙"),
        "zhihu": ("zhihu-raw-uid-2", "知乎评论用户乙"),
    }[platform]

    case = {
        "raw_ids": (raw_uid, c_uid),
        "raw_nicks": (raw_nick, c_nick),
        "creator_hash": anonymize_user_id(raw_uid),
        "comment_hash": anonymize_user_id(c_uid),
    }

    if platform == "xhs":
        from store import xhs as store

        case.update({
            "tables": ("xhs_note", "xhs_note_comment"),
            "content_id": "xhs-mtx-1",
            "content": {
                "note_id": "xhs-mtx-1", "type": "normal", "title": "矩阵标题", "desc": "矩阵描述",
                "user": {"user_id": raw_uid, "nickname": raw_nick},
                "interact_info": {"liked_count": "12", "collected_count": "3",
                                  "comment_count": "2", "share_count": "1"},
                "time": 1700000000, "last_update_time": 1700000000,
                "image_list": [], "tag_list": [], "ip_location": "上海",
            },
            "update_note": store.update_xhs_note,
            "comment_id": "c-xhs-1",
            "comment": {
                "id": "c-xhs-1", "create_time": 1700000001, "content": "评论内容",
                "user_info": {"user_id": c_uid, "nickname": c_nick},
                "sub_comment_count": 0, "like_count": 3, "pictures": [], "target_comment": {},
            },
            "update_comment": store.update_xhs_note_comment,
        })
    elif platform == "dy":
        from store import douyin as store

        case.update({
            "tables": ("douyin_aweme", "douyin_aweme_comment"),
            "content_id": "dy-mtx-1",
            "content": {
                "aweme_id": "dy-mtx-1", "aweme_type": 0, "desc": "抖音矩阵", "create_time": 1700000000,
                "author": {"uid": raw_uid, "nickname": raw_nick},
                "statistics": {"digg_count": 5, "collect_count": 1, "comment_count": 2, "share_count": 0},
                "video": {"play_addr_h264": {"url_list": ["https://cdn.example/dy.mp4"]},
                          "raw_cover": {"url_list": ["https://cdn.example/dy.jpg"]}},
                "music": {"play_url": {"uri": "https://cdn.example/music.mp3"}},
            },
            "update_note": store.update_douyin_aweme,
            "comment_id": "c-dy-1",
            "comment": {
                "aweme_id": "dy-mtx-1", "cid": "c-dy-1", "create_time": 1700000001, "text": "评论内容",
                "user": {"uid": c_uid, "nickname": c_nick},
                "reply_comment_total": 0, "digg_count": 1, "reply_id": "0", "image_list": [],
            },
            "update_comment": store.update_dy_aweme_comment,
        })
    elif platform == "ks":
        from store import kuaishou as store

        case.update({
            "tables": ("kuaishou_video", "kuaishou_video_comment"),
            "content_id": "ks-mtx-1",
            "content": {
                "type": "video",
                "photo": {"id": "ks-mtx-1", "caption": "快手矩阵", "timestamp": 1700000000,
                          "realLikeCount": 9, "viewCount": 99,
                          "coverUrl": "https://cdn.example/ks.jpg",
                          "photoUrl": "https://cdn.example/ks.mp4"},
                "author": {"id": raw_uid, "name": raw_nick},
            },
            "update_note": store.update_kuaishou_video,
            "comment_id": "c-ks-1",
            "comment": {
                "comment_id": "c-ks-1", "author_id": c_uid, "author_name": c_nick,
                "content": "评论内容", "timestamp": 1700000001, "commentCount": 0,
            },
            "update_comment": store.update_ks_video_comment,
        })
    elif platform == "bili":
        from store import bilibili as store

        case.update({
            "tables": ("bilibili_video", "bilibili_video_comment"),
            "content_id": "111",
            "content": {
                "View": {"aid": 111, "bvid": "BV1mtx", "title": "B站矩阵", "desc": "描述",
                         "pubdate": 1700000000, "pic": "https://cdn.example/bili.jpg",
                         "owner": {"mid": int(raw_uid), "name": raw_nick},
                         "stat": {"like": 3, "dislike": 0, "view": 100, "favorite": 1,
                                  "share": 2, "coin": 4, "danmaku": 5, "reply": 6}},
            },
            "update_note": store.update_bilibili_video,
            # bilibili 评论以 rpid 作为 comment_id 落库
            "comment_id": "1",
            "comment": {
                "rpid": 1, "parent": 0, "ctime": 1700000001,
                "content": {"message": "评论内容"},
                "member": {"mid": int(c_uid), "uname": c_nick},
                "like": 2, "rcount": 0,
            },
            "update_comment": store.update_bilibili_video_comment,
        })
    elif platform == "wb":
        from store import weibo as store

        case.update({
            "tables": ("weibo_note", "weibo_note_comment"),
            "content_id": "wb-mtx-1",
            "content": {
                "mblog": {"id": "wb-mtx-1", "text": "<p>微博正文</p>",
                          "created_at": "Mon Nov 16 12:00:00 +0800 2026",
                          "user": {"id": raw_uid, "screen_name": raw_nick},
                          "attitudes_count": 1, "comments_count": 2, "reposts_count": 3},
            },
            "update_note": store.update_weibo_note,
            "comment_id": "c-wb-1",
            "comment": {
                "id": "c-wb-1", "text": "评论内容",
                "created_at": "Mon Nov 16 13:00:00 +0800 2026",
                "user": {"id": c_uid, "screen_name": c_nick},
                "like_count": 1, "total_number": 0, "rootid": "0",
            },
            "update_comment": store.update_weibo_note_comment,
        })
    elif platform == "tieba":
        from model.m_baidu_tieba import TiebaComment, TiebaNote
        from store import tieba as store

        case.update({
            "tables": ("tieba_note", "tieba_comment"),
            "content_id": "tieba-mtx-1",
            "content": TiebaNote(
                note_id="tieba-mtx-1", title="贴吧矩阵", note_url="https://tieba.example.com/p/1",
                tieba_name="python", tieba_link="https://tieba.example.com/f?kw=python",
                creator_hash=anonymize_user_id(raw_uid), user_nickname=mask_nickname(raw_nick),
                total_replay_num=2,
            ),
            "update_note": store.update_tieba_note,
            "comment_id": "c-tb-1",
            "comment": TiebaComment(
                comment_id="c-tb-1", content="评论内容", note_id="tieba-mtx-1",
                note_url="https://tieba.example.com/p/1", tieba_id="python",
                tieba_name="python", tieba_link="https://tieba.example.com/f?kw=python",
                creator_hash=anonymize_user_id(c_uid), user_nickname=mask_nickname(c_nick),
            ),
            "update_comment": store.update_tieba_note_comment,
        })
    elif platform == "zhihu":
        from model.m_zhihu import ZhihuComment, ZhihuContent
        from store import zhihu as store

        case.update({
            "tables": ("zhihu_content", "zhihu_comment"),
            "content_id": "zhihu-mtx-1",
            "content": ZhihuContent(
                content_id="zhihu-mtx-1", content_type="article", content_text="知乎正文",
                content_url="https://www.zhihu.example.com/question/1/answer/1",
                title="知乎矩阵", creator_hash=anonymize_user_id(raw_uid),
                user_nickname=mask_nickname(raw_nick),
            ),
            "update_note": store.update_zhihu_content,
            "comment_id": "c-zh-1",
            "comment": ZhihuComment(
                comment_id="c-zh-1", content="评论内容", content_id="zhihu-mtx-1",
                content_type="article", creator_hash=anonymize_user_id(c_uid),
                user_nickname=mask_nickname(c_nick),
            ),
            # 注意：知乎的评论更新函数只接收评论对象本身
            "update_comment": store.update_zhihu_content_comment,
            "comment_signature": "single",
        })
    return case


async def _store_case(case: dict) -> None:
    """调用真实的存储更新函数（内容 + 评论）"""
    await case["update_note"](case["content"])
    if case.get("comment_signature") == "single":
        # 知乎的评论更新函数只接收评论对象本身
        await case["update_comment"](case["comment"])
    else:
        await case["update_comment"](case["content_id"], case["comment"])


def _assert_no_raw_pii(record: dict, raw_ids: tuple, raw_nicks: tuple) -> None:
    blob = json.dumps(record, ensure_ascii=False, default=str)
    for raw in raw_ids + raw_nicks:
        assert raw not in blob, f"原始标识泄漏进落盘记录: {raw} -> {blob[:400]}"


def _assert_content_pii(record: dict, case: dict) -> None:
    assert record.get("creator_hash") == case["creator_hash"], (
        f"creator_hash 应为原始 ID 的 16 位哈希: {record.get('creator_hash')}"
    )
    _assert_no_raw_pii(record, case["raw_ids"][:1], case["raw_nicks"][:1])


def _assert_comment_pii(record: dict, case: dict) -> None:
    _assert_no_raw_pii(record, case["raw_ids"], case["raw_nicks"])
    assert "*" in str(record.get("nickname") or record.get("user_nickname", "")), (
        f"评论昵称应已脱敏: {record.get('nickname') or record.get('user_nickname')}"
    )


# --------------------------------------------------------------------------- 文件格式


def _read_file_rows(tmp_path: Path, platform: str, fmt: str, item_type: str) -> list[dict]:
    directory = tmp_path / _FILE_DIR[platform] / fmt
    # bili 的 csv 存储用 videos 命名而 json/jsonl 用 contents，两种命名都接受
    candidates = list(dict.fromkeys([item_type, "contents", "videos"]))
    files: list[Path] = []
    for candidate in candidates:
        files = sorted(directory.glob(f"search_{candidate}_*.{fmt}"))
        if files:
            break
    assert files, (
        f"缺少导出文件: {directory}/search_{item_type}_*.{fmt} "
        f"(目录: {sorted(p.name for p in directory.iterdir()) if directory.exists() else '不存在'})"
    )
    path = files[0]
    if fmt == "csv":
        with open(path, encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))
    if fmt == "jsonl":
        with open(path, encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    if fmt == "json":
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, list) else [data]
    raise AssertionError(f"未支持的格式 {fmt}")


@pytest.mark.asyncio
@pytest.mark.parametrize("fmt", ["csv", "json", "jsonl"])
@pytest.mark.parametrize("platform", PLATFORMS)
async def test_file_export_formats(storage_env, platform, fmt, monkeypatch):
    """csv/json/jsonl：真实写入后回读，校验内容与 PII 脱敏"""
    monkeypatch.setattr(config, "SAVE_DATA_OPTION", fmt)
    case = _build_case(platform)
    await _store_case(case)

    contents = _read_file_rows(storage_env, platform, fmt, _CONTENT_ITEM_TYPE.get(platform, "contents"))
    comments = _read_file_rows(storage_env, platform, fmt, "comments")
    assert len(contents) == 1 and len(comments) == 1
    _assert_content_pii(contents[0], case)
    _assert_comment_pii(comments[0], case)


@pytest.mark.asyncio
@pytest.mark.parametrize("platform", PLATFORMS)
async def test_excel_export(storage_env, platform, monkeypatch):
    """excel：真实写入 workbook，flush 后用 openpyxl 回读"""
    from store.excel_store_base import ExcelStoreBase

    monkeypatch.setattr(config, "SAVE_DATA_OPTION", "excel")
    case = _build_case(platform)
    await _store_case(case)
    ExcelStoreBase.flush_all()

    files = sorted((storage_env / _EXCEL_DIR[platform]).glob("*.xlsx"))
    assert files, f"缺少 excel 导出文件: {storage_env / _EXCEL_DIR[platform]}"
    import openpyxl

    workbook = openpyxl.load_workbook(files[0])
    sheet = workbook["Contents"]
    rows = list(sheet.iter_rows(values_only=True))
    header = [cell for cell in rows[0] if cell is not None]
    records = [dict(zip(header, row[:len(header)])) for row in rows[1:] if any(row)]
    assert len(records) == 1
    _assert_content_pii(records[0], case)

    c_rows = list(workbook["Comments"].iter_rows(values_only=True))
    c_header = [cell for cell in c_rows[0] if cell is not None]
    c_records = [dict(zip(c_header, row[:len(c_header)])) for row in c_rows[1:] if any(row)]
    assert len(c_records) == 1
    _assert_comment_pii(c_records[0], case)


# --------------------------------------------------------------------------- 数据库格式


async def _create_tables_on(engine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def _fetch_rows(engine, table: str) -> list[dict]:
    async with engine.connect() as conn:
        result = await conn.execute(sqlalchemy.text(f"SELECT * FROM {table}"))
        return [dict(row) for row in result.mappings().all()]


@pytest.mark.asyncio
@pytest.mark.parametrize("platform", PLATFORMS)
async def test_sqlite_export(storage_env, platform, monkeypatch):
    """sqlite：真实 aiosqlite 驱动 + ORM 建表 + 存储写入 + 回读"""
    monkeypatch.setattr(config, "SAVE_DATA_OPTION", "sqlite")
    monkeypatch.setattr(
        "database.db_session.sqlite_db_config",
        {"db_path": str(storage_env / "sqlite_tables.db")},
    )
    await database_db.init_db("sqlite")

    case = _build_case(platform)
    await _store_case(case)

    engine = db_session.get_async_engine("sqlite")
    content_rows = await _fetch_rows(engine, case["tables"][0])
    comment_rows = await _fetch_rows(engine, case["tables"][1])
    assert len(content_rows) == 1 and len(comment_rows) == 1
    _assert_content_pii(content_rows[0], case)
    _assert_comment_pii(comment_rows[0], case)


@pytest.mark.asyncio
@pytest.mark.parametrize("db_type", ["db", "postgres"])
@pytest.mark.parametrize("platform", PLATFORMS)
async def test_db_store_business_logic(storage_env, platform, db_type, monkeypatch):
    """db(MySQL)/postgres 的存储实现走 get_session -> ORM 的业务逻辑，
    与驱动无关。服务不可达时注入 sqlite 引擎验证同一套代码路径。"""
    monkeypatch.setattr(config, "SAVE_DATA_OPTION", db_type)
    engine = sqlalchemy.ext.asyncio.create_async_engine(
        f"sqlite+aiosqlite:///{storage_env / f'{db_type}.db'}"
    )
    db_session._engines[db_type] = engine
    await _create_tables_on(engine)

    case = _build_case(platform)
    await _store_case(case)

    content_rows = await _fetch_rows(engine, case["tables"][0])
    comment_rows = await _fetch_rows(engine, case["tables"][1])
    assert len(content_rows) == 1 and len(comment_rows) == 1
    _assert_content_pii(content_rows[0], case)
    _assert_comment_pii(comment_rows[0], case)
    # 验证 upsert 语义：重复写入同一内容 ID 应更新而非新增
    await case["update_note"](case["content"])
    content_rows = await _fetch_rows(engine, case["tables"][0])
    assert len(content_rows) == 1, "重复写入应更新已有记录而不是新增"
    await engine.dispose()


# --------------------------------------------------------------------------- 真实数据库服务


@pytest.mark.skipif(not _port_open("127.0.0.1", MYSQL_PORT), reason="临时 MySQL 服务未运行")
@pytest.mark.asyncio
@pytest.mark.parametrize("platform", PLATFORMS)
async def test_real_mysql_export(storage_env, platform, monkeypatch):
    """真实 MySQL（asyncmy 驱动）：建库建表 + 写入 + 回读"""
    monkeypatch.setattr(config, "SAVE_DATA_OPTION", "db")
    monkeypatch.setattr(
        "database.db_session.mysql_db_config",
        {"user": "root", "password": "", "host": "127.0.0.1",
         "port": MYSQL_PORT, "db_name": "media_crawler_matrix"},
    )
    await database_db.init_db("db")

    case = _build_case(platform)
    await _store_case(case)

    engine = db_session.get_async_engine("db")
    content_rows = await _fetch_rows(engine, case["tables"][0])
    comment_rows = await _fetch_rows(engine, case["tables"][1])
    assert len(content_rows) == 1 and len(comment_rows) == 1
    _assert_content_pii(content_rows[0], case)
    _assert_comment_pii(comment_rows[0], case)


@pytest.mark.skipif(not _port_open("127.0.0.1", POSTGRES_PORT), reason="临时 PostgreSQL 服务未运行")
@pytest.mark.asyncio
@pytest.mark.parametrize("platform", PLATFORMS)
async def test_real_postgres_export(storage_env, platform, monkeypatch):
    """真实 PostgreSQL（asyncpg 驱动）：建库建表 + 写入 + 回读"""
    monkeypatch.setattr(config, "SAVE_DATA_OPTION", "postgres")
    monkeypatch.setattr(
        "database.db_session.postgres_db_config",
        {"user": "postgres", "password": "123456", "host": "127.0.0.1",
         "port": POSTGRES_PORT, "db_name": "media_crawler_matrix"},
    )
    await database_db.init_db("postgres")

    case = _build_case(platform)
    await _store_case(case)

    engine = db_session.get_async_engine("postgres")
    content_rows = await _fetch_rows(engine, case["tables"][0])
    comment_rows = await _fetch_rows(engine, case["tables"][1])
    assert len(content_rows) == 1 and len(comment_rows) == 1
    _assert_content_pii(content_rows[0], case)
    _assert_comment_pii(comment_rows[0], case)


# --------------------------------------------------------------------------- mongodb


def test_mongodb_factory_wiring(storage_env):
    """MongoDB 服务不在本机时，至少验证工厂装配与实现接口完整"""
    from store.xhs import XhsStoreFactory

    config.SAVE_DATA_OPTION = "mongodb"
    store = XhsStoreFactory.create_store()
    assert store is not None
    for method in ("store_content", "store_comment"):
        assert hasattr(store, method)


@pytest.mark.skipif(not _port_open("127.0.0.1", MONGO_PORT), reason="MongoDB 服务未运行")
@pytest.mark.asyncio
@pytest.mark.parametrize("platform", ["xhs", "dy", "bili"])
async def test_real_mongodb_export(storage_env, platform, monkeypatch):
    """真实 MongoDB（motor 驱动）：upsert 写入 + find_one 回读 + PII 校验"""
    from database.mongodb_store_base import MongoDBConnection

    content_key = {"xhs": "note_id", "dy": "aweme_id", "bili": "video_id"}[platform]
    package_name = {"xhs": "xhs", "dy": "douyin", "bili": "bilibili"}[platform]
    factory_name = {"xhs": "XhsStoreFactory", "dy": "DouyinStoreFactory",
                    "bili": "BiliStoreFactory"}[platform]

    monkeypatch.setattr(config, "SAVE_DATA_OPTION", "mongodb")
    monkeypatch.setattr(
        "database.mongodb_store_base.db_config.mongodb_config",
        {"host": "127.0.0.1", "port": MONGO_PORT, "user": "",
         "password": "", "db_name": "media_crawler_matrix"},
    )
    # 重置单例连接，确保连到测试实例（_client 在实例属性上，须取实例重置）
    mongo_conn = MongoDBConnection()
    if mongo_conn._client is not None:
        mongo_conn._client.close()
    mongo_conn._client = None
    mongo_conn._db = None

    case = _build_case(platform)
    await _store_case(case)

    from importlib import import_module
    store = getattr(import_module(f"store.{package_name}"), factory_name).create_store()

    content_row = await store.mongo_store.find_one(
        "contents", {content_key: case["content_id"]}
    )
    assert content_row, f"{platform} 内容应写入 MongoDB"
    _assert_content_pii(content_row, case)

    comment_row = await store.mongo_store.find_one(
        "comments", {"comment_id": case["comment_id"]}
    )
    assert comment_row, f"{platform} 评论应写入 MongoDB"
    _assert_comment_pii(comment_row, case)

    # upsert 语义：重复写入不产生第二条
    await case["update_note"](case["content"])
    collection = await store.mongo_store.get_collection("contents")
    count = await collection.count_documents({content_key: case["content_id"]})
    assert count == 1, "重复写入应更新而非新增"

    mongo_conn._client.close()
    mongo_conn._client = None
    mongo_conn._db = None

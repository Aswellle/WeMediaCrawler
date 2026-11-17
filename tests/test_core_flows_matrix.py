# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests\test_core_flows_matrix.py
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

"""跨平台业务流程矩阵：search / detail / creator 三条主链路。

用假 client 返回平台真实结构的最小数据，把 store 与媒体下载替换成记录器，
验证「入口方法 -> client 调用 -> 入库 -> 媒体 -> 评论」的编排顺序与次数。
不访问任何真实平台。
"""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import config
import pytest

from media_platform.bilibili.core import BilibiliCrawler
from media_platform.douyin.core import DouYinCrawler
from media_platform.kuaishou.core import KuaishouCrawler
from media_platform.tieba.core import TieBaCrawler
from media_platform.weibo.core import WeiboCrawler
from media_platform.xhs.core import XiaoHongShuCrawler
from media_platform.zhihu.core import ZhihuCrawler
from var import crawler_type_var, source_keyword_var


@pytest.fixture
def flow_env(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "SAVE_DATA_PATH", str(tmp_path))
    monkeypatch.setattr(config, "SAVE_DATA_OPTION", "jsonl")
    monkeypatch.setattr(config, "ENABLE_GET_MEDIA", True)
    monkeypatch.setattr(config, "ENABLE_GET_COMMENTS", True)
    monkeypatch.setattr(config, "ENABLE_GET_SUB_COMMENTS", True)
    monkeypatch.setattr(config, "CRAWLER_MAX_SLEEP_SEC", 0)
    monkeypatch.setattr(config, "MAX_CONCURRENCY_NUM", 1)
    monkeypatch.setattr(config, "START_PAGE", 1)
    monkeypatch.setattr(config, "KEYWORDS", "矩阵测试")
    crawler_type_var.set("search")
    source_keyword_var.set("矩阵测试")
    return tmp_path


def _recorder():
    async def record(*args, **kwargs):
        record.calls.append((args, kwargs))
        return []
    record.calls = []
    return record


def _shell(cls, client_attr: str):
    crawler = cls()
    setattr(crawler, client_attr, SimpleNamespace(proxy=None, headers={}))
    crawler.user_agent = "flow-matrix-agent"
    return crawler


# --------------------------------------------------------------------------- xhs


@pytest.mark.asyncio
async def test_xhs_search_flow(flow_env, monkeypatch):
    crawler = _shell(XiaoHongShuCrawler, "xhs_client")
    stored, downloaded, commented = _recorder(), _recorder(), _recorder()

    async def get_note_by_keyword(**kwargs):
        return {"has_more": True,
                "items": [{"id": "n1", "model_type": "note",
                           "xsec_token": "tok", "xsec_source": "pc_search"}]}

    async def get_note_by_id(note_id, xsec_source, xsec_token):
        return {"note_id": note_id, "type": "normal", "image_list": [],
                "user": {}, "interact_info": {}, "tag_list": []}

    crawler.xhs_client.get_note_by_keyword = get_note_by_keyword
    crawler.xhs_client.get_note_by_id = get_note_by_id
    crawler.xhs_client.get_note_by_id_from_html = AsyncMock(return_value=None)
    monkeypatch.setattr("media_platform.xhs.core.xhs_store.update_xhs_note", stored)
    monkeypatch.setattr(crawler, "download_media", downloaded)
    monkeypatch.setattr(crawler, "batch_get_note_comments", commented)

    await crawler.search()

    assert len(stored.calls) == 1 and stored.calls[0][0][0]["note_id"] == "n1"
    assert len(downloaded.calls) == 1
    assert len(commented.calls) == 1 and commented.calls[0][0][0] == ["n1"]


@pytest.mark.asyncio
async def test_xhs_detail_flow(flow_env, monkeypatch):
    crawler = _shell(XiaoHongShuCrawler, "xhs_client")
    stored, downloaded, commented = _recorder(), _recorder(), _recorder()

    crawler.xhs_client.get_note_by_id = AsyncMock(
        return_value={"note_id": "note-detail-1", "type": "normal", "image_list": [],
                      "user": {}, "interact_info": {}, "tag_list": []}
    )
    monkeypatch.setattr(
        config, "XHS_SPECIFIED_NOTE_URL_LIST",
        ["https://www.xiaohongshu.com/explore/note-detail-1?xsec_token=t&xsec_source=pc_search"],
    )
    monkeypatch.setattr("media_platform.xhs.core.xhs_store.update_xhs_note", stored)
    monkeypatch.setattr(crawler, "download_media", downloaded)
    monkeypatch.setattr(crawler, "batch_get_note_comments", commented)

    await crawler.get_specified_notes()

    assert len(stored.calls) == 1
    assert stored.calls[0][0][0]["note_id"] == "note-detail-1"
    assert len(downloaded.calls) == 1
    assert len(commented.calls) == 1


@pytest.mark.asyncio
async def test_xhs_creator_flow(flow_env, monkeypatch):
    crawler = _shell(XiaoHongShuCrawler, "xhs_client")
    stored, downloaded, commented = _recorder(), _recorder(), _recorder()

    crawler.xhs_client.get_creator_info = AsyncMock(return_value={"basic_info": {}})

    async def xhs_all_notes(**kwargs):
        notes = [{"note_id": "n1", "xsec_token": "t"}]
        await kwargs["callback"](notes)
        return notes

    crawler.xhs_client.get_all_notes_by_creator = xhs_all_notes
    crawler.xhs_client.get_note_by_id = AsyncMock(
        return_value={"note_id": "n1", "type": "normal", "image_list": [],
                      "user": {}, "interact_info": {}, "tag_list": []}
    )
    crawler.xhs_client.get_note_by_id_from_html = AsyncMock(return_value=None)
    monkeypatch.setattr(
        config, "XHS_CREATOR_ID_LIST",
        ["https://www.xiaohongshu.com/user/profile/abc?xsec_token=t&xsec_source=pc_search"],
    )
    monkeypatch.setattr("media_platform.xhs.core.xhs_store.update_xhs_note", stored)
    monkeypatch.setattr("media_platform.xhs.core.xhs_store.save_creator", _recorder())
    monkeypatch.setattr(crawler, "download_media", downloaded)
    monkeypatch.setattr(crawler, "batch_get_note_comments", commented)

    await crawler.get_creators_and_notes()

    assert len(stored.calls) == 1, "创作者笔记应入库"
    assert len(downloaded.calls) == 1
    assert len(commented.calls) == 1


# --------------------------------------------------------------------------- douyin


@pytest.mark.asyncio
async def test_douyin_search_flow(flow_env, monkeypatch):
    crawler = _shell(DouYinCrawler, "dy_client")
    stored, downloaded, commented = _recorder(), _recorder(), _recorder()

    async def search_info_by_keyword(**kwargs):
        return {"data": [{"aweme_info": {"aweme_id": "a1"}}],
                "has_more": 0, "extra": {"logid": "log-1"}}

    crawler.dy_client.search_info_by_keyword = search_info_by_keyword
    monkeypatch.setattr("media_platform.douyin.core.douyin_store.update_douyin_aweme", stored)
    monkeypatch.setattr(crawler, "download_media", downloaded)
    monkeypatch.setattr(crawler, "batch_get_note_comments", commented)

    await crawler.search()

    assert len(stored.calls) >= 1
    assert any(call[1]["aweme_item"]["aweme_id"] == "a1" for call in stored.calls)
    assert len(downloaded.calls) >= 1
    assert len(commented.calls) >= 1


@pytest.mark.asyncio
async def test_douyin_detail_flow(flow_env, monkeypatch):
    crawler = _shell(DouYinCrawler, "dy_client")
    stored, downloaded, commented = _recorder(), _recorder(), _recorder()

    crawler.dy_client.get_video_by_id = AsyncMock(return_value={"aweme_id": "a1"})
    monkeypatch.setattr(config, "DY_SPECIFIED_ID_LIST", ["7280854932641664319"])
    monkeypatch.setattr("media_platform.douyin.core.douyin_store.update_douyin_aweme", stored)
    monkeypatch.setattr(crawler, "download_media", downloaded)
    monkeypatch.setattr(crawler, "batch_get_note_comments", commented)

    await crawler.get_specified_awemes()

    assert len(stored.calls) == 1
    assert len(downloaded.calls) == 1
    assert len(commented.calls) == 1


@pytest.mark.asyncio
async def test_douyin_creator_flow(flow_env, monkeypatch):
    crawler = _shell(DouYinCrawler, "dy_client")
    stored, downloaded, commented = _recorder(), _recorder(), _recorder()

    crawler.dy_client.get_user_info = AsyncMock(return_value={"user": {"sec_uid": "sec1"}})
    crawler.dy_client.get_video_by_id = AsyncMock(return_value={"aweme_id": "a1"})

    async def dy_all_posts(**kwargs):
        posts = [{"aweme_id": "a1"}]
        callback = kwargs.get("callback")
        if callback:
            await callback(posts)
        return posts

    crawler.dy_client.get_all_user_aweme_posts = dy_all_posts
    monkeypatch.setattr(config, "DY_CREATOR_ID_LIST", ["MS4wLjABAAAAsec1"])
    monkeypatch.setattr("media_platform.douyin.core.douyin_store.update_douyin_aweme", stored)
    monkeypatch.setattr("media_platform.douyin.core.douyin_store.save_creator", _recorder())
    monkeypatch.setattr(crawler, "download_media", downloaded)
    monkeypatch.setattr(crawler, "batch_get_note_comments", commented)

    await crawler.get_creators_and_videos()

    assert len(stored.calls) >= 1
    assert len(downloaded.calls) >= 1


# --------------------------------------------------------------------------- kuaishou


@pytest.mark.asyncio
async def test_kuaishou_search_flow(flow_env, monkeypatch):
    crawler = _shell(KuaishouCrawler, "ks_client")
    stored, downloaded, commented = _recorder(), _recorder(), _recorder()

    crawler.ks_client.search_info_by_keyword_v2 = AsyncMock(
        return_value={"result": 1, "feeds": [{"photo": {"id": "v1"}}],
                      "searchSessionId": "s1"}
    )
    monkeypatch.setattr("media_platform.kuaishou.core.kuaishou_store.update_kuaishou_video", stored)
    monkeypatch.setattr(crawler, "download_media", downloaded)
    monkeypatch.setattr(crawler, "batch_get_video_comments", commented)

    await crawler.search()

    assert len(stored.calls) == 1
    assert stored.calls[0][1]["video_item"]["photo"]["id"] == "v1"
    assert len(downloaded.calls) == 1
    assert len(commented.calls) == 1


@pytest.mark.asyncio
async def test_kuaishou_detail_flow(flow_env, monkeypatch):
    crawler = _shell(KuaishouCrawler, "ks_client")
    stored, downloaded, commented = _recorder(), _recorder(), _recorder()

    crawler.ks_client.get_video_info = AsyncMock(
        return_value={"visionVideoDetail": {"photo": {"id": "v1"}, "author": {"id": "u1"}}}
    )
    monkeypatch.setattr(config, "KS_SPECIFIED_ID_LIST", ["3xabc123"])
    monkeypatch.setattr("media_platform.kuaishou.core.kuaishou_store.update_kuaishou_video", stored)
    monkeypatch.setattr(crawler, "download_media", downloaded)
    monkeypatch.setattr(crawler, "batch_get_video_comments", commented)

    await crawler.get_specified_videos()

    assert len(stored.calls) == 1
    assert len(downloaded.calls) == 1


@pytest.mark.asyncio
async def test_kuaishou_creator_flow(flow_env, monkeypatch):
    crawler = _shell(KuaishouCrawler, "ks_client")
    stored, downloaded, commented = _recorder(), _recorder(), _recorder()

    crawler.ks_client.get_creator_info = AsyncMock(return_value={"userProfile": {"ownerCount": {}}})
    crawler.ks_client.get_video_info = AsyncMock(
        return_value={"visionVideoDetail": {"photo": {"id": "v1"}, "author": {"id": "u1"}}}
    )

    async def ks_all_videos(**kwargs):
        videos = [{"photo": {"id": "v1"}, "author": {"id": "u1"}}]
        callback = kwargs.get("callback")
        if callback:
            await callback(videos)
        return videos

    crawler.ks_client.get_all_videos_by_creator = ks_all_videos
    monkeypatch.setattr(config, "KS_CREATOR_ID_LIST", ["3xcreator"])
    monkeypatch.setattr("media_platform.kuaishou.core.kuaishou_store.update_kuaishou_video", stored)
    monkeypatch.setattr("media_platform.kuaishou.core.kuaishou_store.save_creator", _recorder())
    monkeypatch.setattr(crawler, "download_media", downloaded)
    monkeypatch.setattr(crawler, "batch_get_video_comments", commented)

    await crawler.get_creators_and_videos()

    assert len(stored.calls) >= 1
    assert len(downloaded.calls) >= 1


# --------------------------------------------------------------------------- bilibili


@pytest.mark.asyncio
async def test_bilibili_search_flow(flow_env, monkeypatch):
    crawler = _shell(BilibiliCrawler, "bili_client")
    stored, downloaded, commented = _recorder(), _recorder(), _recorder()

    crawler.bili_client.search_video_by_keyword = AsyncMock(
        return_value={"result": [{"aid": 1, "bvid": "BV1"}]}
    )
    crawler.bili_client.get_video_info = AsyncMock(
        return_value={"View": {"aid": 1, "cid": 2, "bvid": "BV1", "pic": ""}}
    )
    monkeypatch.setattr("media_platform.bilibili.core.bilibili_store.update_bilibili_video", stored)
    monkeypatch.setattr("media_platform.bilibili.core.bilibili_store.update_up_info", _recorder())
    monkeypatch.setattr(crawler, "download_media", downloaded)
    monkeypatch.setattr(crawler, "batch_get_video_comments", commented)

    await crawler.search()

    # 全局 CRAWLER_MAX_NOTES_COUNT 可能被先前的平台测试抬高，页数不固定；
    # 这里只断言编排发生（每页都会入库/下载）
    assert len(stored.calls) >= 1
    assert len(downloaded.calls) >= 1
    assert len(commented.calls) == 1


@pytest.mark.asyncio
async def test_bilibili_detail_flow(flow_env, monkeypatch):
    crawler = _shell(BilibiliCrawler, "bili_client")
    stored, downloaded, commented = _recorder(), _recorder(), _recorder()

    crawler.bili_client.get_video_info = AsyncMock(
        return_value={"View": {"aid": 7, "cid": 8, "bvid": "BV7", "pic": ""}}
    )
    monkeypatch.setattr(config, "BILI_SPECIFIED_ID_LIST", ["BV7"])
    monkeypatch.setattr("media_platform.bilibili.core.bilibili_store.update_bilibili_video", stored)
    monkeypatch.setattr("media_platform.bilibili.core.bilibili_store.update_up_info", _recorder())
    monkeypatch.setattr(crawler, "download_media", downloaded)
    monkeypatch.setattr(crawler, "batch_get_video_comments", commented)

    await crawler.get_specified_videos(["BV7"])

    assert len(stored.calls) == 1
    assert len(downloaded.calls) == 1


@pytest.mark.asyncio
async def test_bilibili_creator_flow(flow_env, monkeypatch):
    crawler = _shell(BilibiliCrawler, "bili_client")
    stored, downloaded, commented = _recorder(), _recorder(), _recorder()

    crawler.bili_client.get_creator_info = AsyncMock(return_value={"name": "up"})
    crawler.bili_client.get_creator_videos = AsyncMock(
        return_value={"list": {"vlist": [{"bvid": "BV1"}]}, "page": {"count": 1}}
    )
    crawler.bili_client.get_creator_all_dynamics = AsyncMock(return_value=[])
    crawler.bili_client.get_video_info = AsyncMock(
        return_value={"View": {"aid": 1, "cid": 2, "bvid": "BV1", "pic": ""}}
    )
    dynamics = _recorder()
    monkeypatch.setattr(
        "media_platform.bilibili.core.bilibili_store.batch_update_bilibili_creator_dynamics",
        dynamics,
    )
    monkeypatch.setattr("media_platform.bilibili.core.bilibili_store.update_bilibili_video", stored)
    monkeypatch.setattr("media_platform.bilibili.core.bilibili_store.update_up_info", _recorder())
    monkeypatch.setattr(crawler, "download_media", downloaded)
    monkeypatch.setattr(crawler, "batch_get_video_comments", commented)

    # 创作者主页详情（creator_info -> dynamics）
    await crawler.get_all_creator_details(["12345"])
    # 创作者视频列表（详情 -> 入库 -> 媒体 -> 评论）
    await crawler.get_creator_videos(12345)

    assert len(stored.calls) >= 1, "创作者视频应入库"
    assert len(downloaded.calls) >= 1


# --------------------------------------------------------------------------- weibo


@pytest.mark.asyncio
async def test_weibo_search_flow(flow_env, monkeypatch):
    crawler = _shell(WeiboCrawler, "wb_client")
    stored, downloaded, commented = _recorder(), _recorder(), _recorder()

    crawler.wb_client.get_note_by_keyword = AsyncMock(
        return_value={"cards": [{"card_type": 9, "mblog": {
            "id": "w1", "text": "正文",
            "created_at": "Mon Nov 16 12:00:00 +0800 2026"}}]}
    )
    monkeypatch.setattr("media_platform.weibo.core.weibo_store.update_weibo_note", stored)
    crawler.batch_get_notes_full_text = AsyncMock(side_effect=lambda notes: notes)
    monkeypatch.setattr(crawler, "download_media", downloaded)
    monkeypatch.setattr(crawler, "batch_get_notes_comments", commented)

    await crawler.search()

    # 全局 CRAWLER_MAX_NOTES_COUNT 可能被先前平台测试抬高，页数不固定；
    # 这里断言每页的编排都发生了（入库 + 下载）
    assert len(stored.calls) >= 1
    assert len(downloaded.calls) >= 1


@pytest.mark.asyncio
async def test_weibo_detail_flow(flow_env, monkeypatch):
    crawler = _shell(WeiboCrawler, "wb_client")
    stored, downloaded, commented = _recorder(), _recorder(), _recorder()

    crawler.wb_client.get_note_info_by_id = AsyncMock(
        return_value={"mblog": {"id": "w1", "text": "正文"}}
    )
    monkeypatch.setattr(config, "WEIBO_SPECIFIED_ID_LIST", ["w1"])
    monkeypatch.setattr("media_platform.weibo.core.weibo_store.update_weibo_note", stored)
    monkeypatch.setattr(crawler, "download_media", downloaded)
    monkeypatch.setattr(crawler, "batch_get_notes_comments", commented)

    await crawler.get_specified_notes()

    assert len(stored.calls) == 1
    assert len(downloaded.calls) == 1


@pytest.mark.asyncio
async def test_weibo_creator_flow(flow_env, monkeypatch):
    crawler = _shell(WeiboCrawler, "wb_client")
    stored, downloaded, commented = _recorder(), _recorder(), _recorder()

    crawler.wb_client.get_creator_info_by_id = AsyncMock(
        return_value={"userInfo": {"id": "u1", "screen_name": "n"}}
    )
    async def wb_all_notes(**kwargs):
        notes = [{"mblog": {"id": "w1", "text": "正文"}}]
        await kwargs["callback"](notes)
        return notes

    crawler.wb_client.get_all_notes_by_creator_id = wb_all_notes
    crawler.batch_get_notes_full_text = AsyncMock(side_effect=lambda notes: notes)
    monkeypatch.setattr(config, "WEIBO_CREATOR_ID_LIST", ["u1"])
    monkeypatch.setattr("media_platform.weibo.core.weibo_store.batch_update_weibo_notes", stored)
    monkeypatch.setattr("media_platform.weibo.core.weibo_store.save_creator", _recorder())
    monkeypatch.setattr(crawler, "download_media", downloaded)
    monkeypatch.setattr(crawler, "batch_get_notes_comments", commented)

    await crawler.get_creators_and_notes()

    assert len(stored.calls) >= 1
    assert len(downloaded.calls) >= 1


# --------------------------------------------------------------------------- tieba


@pytest.mark.asyncio
async def test_tieba_search_flow(flow_env, monkeypatch):
    from model.m_baidu_tieba import TiebaNote

    crawler = _shell(TieBaCrawler, "tieba_client")
    stored, commented = _recorder(), _recorder()
    note = TiebaNote(note_id="tb1", title="贴", note_url="https://tieba/p/1",
                     tieba_name="python", tieba_link="https://tieba/f?kw=python")

    crawler.tieba_client.get_notes_by_keyword = AsyncMock(return_value=[note])
    crawler.tieba_client.get_note_by_id = AsyncMock(return_value=note)
    monkeypatch.setattr("media_platform.tieba.core.tieba_store.update_tieba_note", stored)
    monkeypatch.setattr(crawler, "batch_get_note_comments", commented)

    await crawler.search()

    assert len(stored.calls) >= 1
    assert stored.calls[0][0][0].note_id == "tb1"


@pytest.mark.asyncio
async def test_tieba_detail_flow(flow_env, monkeypatch):
    from model.m_baidu_tieba import TiebaNote

    crawler = _shell(TieBaCrawler, "tieba_client")
    stored, commented = _recorder(), _recorder()
    note = TiebaNote(note_id="tb1", title="贴", note_url="https://tieba/p/1",
                     tieba_name="python", tieba_link="https://tieba/f?kw=python")

    crawler.tieba_client.get_note_by_id = AsyncMock(return_value=note)
    monkeypatch.setattr(config, "TIEBA_SPECIFIED_ID_LIST", ["tb1"])
    monkeypatch.setattr(config, "TIEBA_NAME_LIST", [])
    monkeypatch.setattr("media_platform.tieba.core.tieba_store.update_tieba_note", stored)
    monkeypatch.setattr(crawler, "batch_get_note_comments", commented)

    await crawler.get_specified_notes()

    assert len(stored.calls) == 1


# --------------------------------------------------------------------------- zhihu


@pytest.mark.asyncio
async def test_zhihu_search_flow(flow_env, monkeypatch):
    from model.m_zhihu import ZhihuContent

    crawler = _shell(ZhihuCrawler, "zhihu_client")
    stored, commented = _recorder(), _recorder()

    crawler.zhihu_client.get_note_by_keyword = AsyncMock(
        return_value=[ZhihuContent(content_id="z1", content_type="article")]
    )
    monkeypatch.setattr("media_platform.zhihu.core.zhihu_store.update_zhihu_content", stored)
    monkeypatch.setattr(crawler, "batch_get_content_comments", commented)

    await crawler.search()

    assert len(stored.calls) == 1
    assert stored.calls[0][0][0].content_id == "z1"
    assert len(commented.calls) == 1


@pytest.mark.asyncio
async def test_zhihu_detail_flow(flow_env, monkeypatch):
    from model.m_zhihu import ZhihuContent

    crawler = _shell(ZhihuCrawler, "zhihu_client")
    stored, commented = _recorder(), _recorder()

    crawler.zhihu_client.get_article_info = AsyncMock(
        return_value=ZhihuContent(content_id="z1", content_type="article")
    )
    monkeypatch.setattr(config, "ZHIHU_SPECIFIED_ID_LIST",
                        ["https://zhuanlan.zhihu.com/p/123"])
    monkeypatch.setattr("media_platform.zhihu.core.zhihu_store.update_zhihu_content", stored)
    monkeypatch.setattr(crawler, "batch_get_content_comments", commented)

    await crawler.get_specified_notes()

    assert len(stored.calls) == 1


@pytest.mark.asyncio
async def test_zhihu_creator_flow(flow_env, monkeypatch):
    from model.m_zhihu import ZhihuContent

    crawler = _shell(ZhihuCrawler, "zhihu_client")
    stored, commented = _recorder(), _recorder()

    from model.m_zhihu import ZhihuCreator

    crawler.zhihu_client.get_creator_info = AsyncMock(
        return_value=ZhihuCreator(creator_hash="abc", user_nickname="n***")
    )

    async def zh_all_answers(**kwargs):
        contents = [ZhihuContent(content_id="z1", content_type="answer")]
        callback = kwargs.get("callback")
        if callback:
            await callback(contents)
        return contents

    crawler.zhihu_client.get_all_anwser_by_creator = zh_all_answers
    monkeypatch.setattr(config, "ZHIHU_CREATOR_URL_LIST",
                        ["https://www.zhihu.com/people/abc"])
    monkeypatch.setattr("media_platform.zhihu.core.zhihu_store.update_zhihu_content", stored)
    monkeypatch.setattr("media_platform.zhihu.core.zhihu_store.save_creator", _recorder())
    monkeypatch.setattr(crawler, "batch_get_content_comments", commented)

    await crawler.get_creators_and_notes()

    assert len(stored.calls) >= 1

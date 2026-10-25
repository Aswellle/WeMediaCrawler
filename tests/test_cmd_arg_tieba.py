# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests\test_cmd_arg_tieba.py
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

import config
import pytest
from cmd_arg import parse_cmd
from media_platform.tieba import TieBaCrawler


@pytest.mark.asyncio
async def test_tieba_detail_cli_sets_specified_ids():
    await parse_cmd(
        [
            "--platform",
            "tieba",
            "--type",
            "detail",
            "--specified_id",
            "https://tieba.baidu.com/p/10451142633,9835114923",
        ]
    )

    assert config.TIEBA_SPECIFIED_ID_LIST == ["10451142633", "9835114923"]


@pytest.mark.asyncio
async def test_tieba_creator_cli_sets_creator_urls():
    await parse_cmd(
        [
            "--platform",
            "tieba",
            "--type",
            "creator",
            "--creator_id",
            "tb.1.example,https://tieba.baidu.com/home/main?id=tb.1.raw",
        ]
    )

    assert config.TIEBA_CREATOR_URL_LIST == [
        "https://tieba.baidu.com/home/main?id=tb.1.example",
        "https://tieba.baidu.com/home/main?id=tb.1.raw",
    ]


@pytest.mark.asyncio
async def test_tieba_detail_reads_runtime_specified_ids(monkeypatch):
    crawler = TieBaCrawler()
    seen_note_ids = []

    async def fake_get_note_detail(note_id, semaphore):
        seen_note_ids.append(note_id)
        return None

    async def fake_batch_get_comments(note_details):
        return None

    monkeypatch.setattr(config, "TIEBA_SPECIFIED_ID_LIST", ["10451142633"])
    monkeypatch.setattr(crawler, "get_note_detail_async_task", fake_get_note_detail)
    monkeypatch.setattr(crawler, "batch_get_note_comments", fake_batch_get_comments)

    await crawler.get_specified_notes()

    assert seen_note_ids == ["10451142633"]

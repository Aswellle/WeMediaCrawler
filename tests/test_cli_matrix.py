# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests\test_cli_matrix.py
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

"""CLI 使用方式全矩阵：平台 × 类型 × 登录 × 存储 × 开关，以及非法输入。

目标是锁定「所有使用方式都能正确落到 config，非法输入都被明确拒绝」。
不发起任何网络请求。
"""

from __future__ import annotations

import config
import pytest
import typer

from cmd_arg import parse_cmd

PLATFORMS = ["xhs", "dy", "ks", "bili", "wb", "tieba", "zhihu"]
TYPES = ["search", "detail", "creator"]
LOGIN_TYPES = ["qrcode", "phone", "cookie"]
SAVE_OPTIONS = ["csv", "db", "json", "jsonl", "sqlite", "excel", "postgres", "mongodb"]


@pytest.fixture(autouse=True)
def _restore_config():
    """parse_cmd 直接改写 config 模块全局，测试后整体还原，避免污染其它用例"""
    snapshot = {
        name: value for name, value in vars(config).items()
        if not name.startswith("__") and not callable(value) and not isinstance(value, type)
    }
    yield
    for name, value in snapshot.items():
        setattr(config, name, value)


@pytest.mark.asyncio
@pytest.mark.parametrize("platform", PLATFORMS)
@pytest.mark.parametrize("crawler_type", TYPES)
async def test_platform_type_combinations_parse(platform, crawler_type):
    """7 平台 × 3 采集类型：全部组合都能解析并写入 config"""
    args = await parse_cmd(["--platform", platform, "--type", crawler_type])

    assert config.PLATFORM == platform
    assert config.CRAWLER_TYPE == crawler_type
    assert args.platform == platform
    assert args.type == crawler_type


@pytest.mark.asyncio
@pytest.mark.parametrize("save_option", SAVE_OPTIONS)
async def test_all_save_options_accepted(save_option):
    await parse_cmd(["--save_data_option", save_option])

    assert config.SAVE_DATA_OPTION == save_option


@pytest.mark.asyncio
@pytest.mark.parametrize("login_type", LOGIN_TYPES)
async def test_all_login_types_accepted(login_type):
    await parse_cmd(["--lt", login_type])

    assert config.LOGIN_TYPE == login_type


@pytest.mark.asyncio
async def test_all_switches_together_apply():
    """评论/子评论/媒体/无头/代理 同时开启时逐项落到 config"""
    args = await parse_cmd([
        "--platform", "xhs", "--type", "search",
        "--get_comment", "true",
        "--get_sub_comment", "yes",
        "--get_media", "1",
        "--headless", "y",
        "--enable_ip_proxy", "true",
        "--ip_proxy_pool_count", "3",
        "--ip_proxy_provider_name", "static",
        "--static_proxy_url", "http://user:pass@127.0.0.1:8888",
        "--crawler_max_notes_count", "7",
        "--max_comments_count_singlenotes", "9",
        "--max_concurrency_num", "2",
        "--save_data_option", "sqlite",
        "--save_data_path", "./tmp-out",
    ])

    assert config.ENABLE_GET_COMMENTS is True
    assert config.ENABLE_GET_SUB_COMMENTS is True
    assert config.ENABLE_GET_MEDIA is True
    assert config.HEADLESS is True and config.CDP_HEADLESS is True
    assert config.ENABLE_IP_PROXY is True
    assert config.IP_PROXY_POOL_COUNT == 3
    assert config.IP_PROXY_PROVIDER_NAME == "static"
    assert config.STATIC_PROXY_URL == "http://user:pass@127.0.0.1:8888"
    assert config.CRAWLER_MAX_NOTES_COUNT == 7
    assert config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES == 9
    assert config.MAX_CONCURRENCY_NUM == 2
    assert config.SAVE_DATA_OPTION == "sqlite"
    assert config.SAVE_DATA_PATH == "./tmp-out"
    assert args.get_media is True and args.get_comment is True


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("platform", "config_attr"),
    [
        ("xhs", "XHS_SPECIFIED_NOTE_URL_LIST"),
        ("dy", "DY_SPECIFIED_ID_LIST"),
        ("ks", "KS_SPECIFIED_ID_LIST"),
        ("bili", "BILI_SPECIFIED_ID_LIST"),
        ("wb", "WEIBO_SPECIFIED_ID_LIST"),
        ("zhihu", "ZHIHU_SPECIFIED_ID_LIST"),
    ],
)
async def test_specified_id_csv_parsing_trims_and_drops_empty(platform, config_attr):
    await parse_cmd([
        "--platform", platform, "--type", "detail",
        "--specified_id", "  id-1 , ,id-2,  ",
    ])

    assert getattr(config, config_attr) == ["id-1", "id-2"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("platform", "config_attr"),
    [
        ("xhs", "XHS_CREATOR_ID_LIST"),
        ("dy", "DY_CREATOR_ID_LIST"),
        ("ks", "KS_CREATOR_ID_LIST"),
        ("bili", "BILI_CREATOR_ID_LIST"),
        ("wb", "WEIBO_CREATOR_ID_LIST"),
        ("zhihu", "ZHIHU_CREATOR_URL_LIST"),
    ],
)
async def test_creator_id_csv_parsing_trims_and_drops_empty(platform, config_attr):
    await parse_cmd([
        "--platform", platform, "--type", "creator",
        "--creator_id", " https://example.com/u/1 , ,2 ",
    ])

    assert getattr(config, config_attr) == ["https://example.com/u/1", "2"]


@pytest.mark.asyncio
async def test_keywords_passthrough_with_unicode_and_emoji():
    keyword = "美食🍜,川菜, test keyword "
    await parse_cmd(["--keywords", keyword])

    assert config.KEYWORDS == keyword


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "argv",
    [
        ["--platform", "nope"],
        ["--type", "nope"],
        ["--lt", "nope"],
        ["--save_data_option", "nope"],
        ["--init_db", "nope"],
    ],
)
async def test_invalid_enum_values_rejected(argv):
    with pytest.raises((typer.BadParameter, Exception)) as exc_info:
        await parse_cmd(argv)
    # click/typer 的 BadParameter 会带出可读的候选值列表
    assert "not one of" in str(exc_info.value) or "Invalid" in str(exc_info.value)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("option", "value"),
    [
        ("--max_concurrency_num", "0"),
        ("--max_concurrency_num", "-1"),
        ("--crawler_max_notes_count", "0"),
        ("--crawler_max_notes_count", "-5"),
        ("--max_comments_count_singlenotes", "0"),
        ("--start", "0"),
        ("--start", "-3"),
        ("--ip_proxy_pool_count", "0"),
    ],
)
async def test_numeric_lower_bounds_rejected(option, value):
    """0 并发会永久死锁、负数会崩溃或静默 0 条，必须被拒绝"""
    with pytest.raises(Exception) as exc_info:
        await parse_cmd([option, value])
    assert "must be >=" in str(exc_info.value)


@pytest.mark.asyncio
@pytest.mark.parametrize("raw", ["maybe", "2", "", "yesplease"])
async def test_invalid_boolean_rejected(raw):
    with pytest.raises(Exception):
        await parse_cmd(["--get_media", raw])


@pytest.mark.asyncio
async def test_boolean_aliases_for_switches():
    for raw, expected in [("yes", True), ("y", True), ("t", True), ("1", True),
                          ("no", False), ("n", False), ("f", False), ("0", False)]:
        await parse_cmd(["--get_comment", raw, "--get_sub_comment", raw, "--headless", raw])
        assert config.ENABLE_GET_COMMENTS is expected
        assert config.ENABLE_GET_SUB_COMMENTS is expected
        assert config.HEADLESS is expected

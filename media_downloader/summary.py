# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/media_downloader/summary.py
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

"""媒体目录内的笔记 CSV 摘要。

每个 ``{SAVE_DATA_PATH}/{platform}/media/{content_id}/`` 目录附带一份
``summary.csv``（单行），浏览媒体文件时不必回到导出文件就能知道这条
媒体属于什么内容。字段来自 store 层已脱敏的落盘 dict，不在本模块
重复做任何 PII 处理。
"""

from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Mapping, Optional

import aiofiles
import config

from .paths import build_media_dir

logger = logging.getLogger("MediaCrawler.media_downloader")

SUMMARY_FILE_NAME = "summary.csv"


async def write_note_summary(
    platform: str,
    content_id,
    fields: Mapping,
    base_dir: Optional[Path] = None,
) -> Optional[Path]:
    """把单条笔记的摘要写入其媒体目录，返回写入路径。

    :param platform: 媒体目录名（与 MediaDownloader 的 platform 一致：xhs/dy/ks/bili/wb）
    :param content_id: 内容 ID，决定媒体目录
    :param fields: store 层构建的已脱敏落盘 dict（键为 CSV 列名）
    :param base_dir: 测试可覆盖根目录；默认取 ``config.SAVE_DATA_PATH`` 或 ``data``
    :return: 写入的文件路径；媒体下载关闭或无可写字段时返回 None
    """
    if not fields:
        return None
    if not config.ENABLE_GET_MEDIA:
        # 媒体下载关闭时不产生媒体目录，摘要无处安放
        return None

    root = Path(base_dir) if base_dir is not None else Path(
        getattr(config, "SAVE_DATA_PATH", "") or "data"
    )
    directory = build_media_dir(root, platform, content_id)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / SUMMARY_FILE_NAME

    try:
        async with aiofiles.open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(fields.keys()))
            await writer.writeheader()
            await writer.writerow(dict(fields))
    except OSError as exc:
        logger.warning("[summary] 写入笔记摘要失败 %s: %s", path, exc)
        return None
    return path

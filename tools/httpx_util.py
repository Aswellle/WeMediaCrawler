# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tools\httpx_util.py
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

import httpx
import config


def make_async_client(**kwargs) -> httpx.AsyncClient:
    """创建统一配置的 httpx.AsyncClient。

    从配置文件读取 DISABLE_SSL_VERIFY（默认 False，即开启 SSL 验证）。
    仅在使用企业代理、Burp、mitmproxy 等中间人代理时才需将其设为 True。
    """
    kwargs.setdefault("verify", not getattr(config, "DISABLE_SSL_VERIFY", False))
    return httpx.AsyncClient(**kwargs)

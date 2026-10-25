# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests\test_static_proxy_provider.py
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

import pytest

import config
from proxy.proxy_ip_pool import StaticProxyProvider, create_ip_pool
from proxy.types import ProviderNameEnum


def test_default_proxy_provider_remains_existing_provider():
    assert config.IP_PROXY_PROVIDER_NAME == ProviderNameEnum.KUAI_DAILI_PROVIDER.value
    assert config.IP_PROXY_POOL_COUNT == 2
    assert config.STATIC_PROXY_URL == ""


@pytest.mark.asyncio
async def test_static_proxy_provider_parses_proxy_url(monkeypatch):
    monkeypatch.setattr(config, "STATIC_PROXY_URL", "http://user:p%40ss@example.com:8080")

    proxies = await StaticProxyProvider().get_proxy(1)

    assert len(proxies) == 1
    proxy = proxies[0]
    assert proxy.ip == "example.com"
    assert proxy.port == 8080
    assert proxy.user == "user"
    assert proxy.password == "p@ss"
    assert proxy.protocol == "http://"
    assert proxy.expired_time_ts is not None


@pytest.mark.asyncio
async def test_static_proxy_provider_rejects_invalid_url(monkeypatch):
    monkeypatch.setattr(config, "STATIC_PROXY_URL", "http://your_home_domain:port")

    proxies = await StaticProxyProvider().get_proxy(1)

    assert proxies == []


@pytest.mark.asyncio
async def test_static_proxy_pool_disables_validation(monkeypatch):
    monkeypatch.setattr(config, "IP_PROXY_PROVIDER_NAME", ProviderNameEnum.STATIC_PROVIDER.value)
    monkeypatch.setattr(config, "STATIC_PROXY_URL", "https://example.com:8443")

    pool = await create_ip_pool(ip_pool_count=2, enable_validate_ip=True)

    assert pool.enable_validate_ip is False
    assert len(pool.proxy_list) == 1
    assert pool.proxy_list[0].protocol == "https://"

# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tools\user_hash.py
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

# Copyright (c) 2025 relakkes@gmail.com
#
# 本文件为 MediaCrawler 教学版的一部分。
# 出于教学与防骚扰定位，爬取结果中不保留任何可定位到真人的用户个人信息
# （用户 ID、IP 归属地、头像、主页链接、签名、性别等一律不采集；
# 昵称保留但做中间脱敏）。本模块提供匿名化与脱敏工具。
import hashlib


def anonymize_user_id(user_id) -> str:
    """把原始用户 ID 转成匿名哈希，用于内容/评论记录的创作者分组，
    不暴露真实身份。返回 sha256 截断 16 位的十六进制串。"""
    if user_id is None:
        return ""
    s = str(user_id).strip()
    if not s:
        return ""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def mask_nickname(name) -> str:
    """昵称中间脱敏：首尾各保留 1 字，中间替换为星号。
    - 长度 <= 1：返回 "*"
    - 长度 == 2：首字 + "*"
    - 长度 >= 3：首字 + "***" + 尾字
    这样既保留教学分析所需的内容归属语义，又无法据昵称定位到真人。
    """
    if name is None:
        return ""
    s = str(name)
    if len(s) <= 1:
        return "*"
    if len(s) == 2:
        return s[0] + "*"
    return s[0] + "***" + s[-1]

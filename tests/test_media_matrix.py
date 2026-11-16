# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests\test_media_matrix.py
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

"""媒体获取组合矩阵测试。

补齐 ``test_media_core_integration.py`` 未覆盖的组合：
- 微博图集与转发微博的媒体归属
- kuaishou / weibo / bilibili 的 ENABLE_GET_MEDIA 关闭分支
- B 站 DASH 真实 ffmpeg 合流（不 mock merge，验证产出可用 ffmpeg 校验）
"""

from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

import config
import pytest

from media_platform.bilibili.core import BilibiliCrawler
from media_platform.kuaishou.core import KuaishouCrawler
from media_platform.weibo.core import WeiboCrawler
from tests.media_server import DEFAULT_CONTENT, MediaTestServer, start_server

FFMPEG = shutil.which("ffmpeg")
FFPROBE = shutil.which("ffprobe")


@pytest.fixture(scope="module")
def server():
    srv, _thread = start_server()
    yield srv
    srv.shutdown()
    srv.server_close()


@pytest.fixture(autouse=True)
def _reset_server(server: MediaTestServer):
    server.reset()


@pytest.fixture(autouse=True)
def _media_config(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(config, "ENABLE_GET_MEDIA", True)
    monkeypatch.setattr(config, "SAVE_DATA_PATH", str(tmp_path))
    monkeypatch.setattr(config, "CRAWLER_MAX_SLEEP_SEC", 0)


def media_dir(tmp_path: Path, platform: str, content_id: str) -> Path:
    return tmp_path / platform / "media" / content_id


def assert_downloaded(directory: Path, filename: str) -> Path:
    path = directory / filename
    assert path.is_file(), f"缺少文件 {path}，目录内容: {sorted(p.name for p in directory.iterdir())}"
    assert path.stat().st_size == len(DEFAULT_CONTENT)
    return path


# --------------------------------------------------------------------------- weibo


@pytest.mark.asyncio
async def test_weibo_core_downloads_numbered_images(server, tmp_path, monkeypatch):
    """普通微博的多张配图应按序号落盘，且不重复下载封面。

    生产实现会把图床地址改写为 i1.wp.com 图片代理（防盗链），
    测试把代理前缀钉到本地服务器，保留改写逻辑的真实路径。
    """
    origin = server.url("/ok/x").rsplit("/ok/", 1)[0]
    monkeypatch.setattr("media_platform.weibo.media.WEIBO_IMAGE_AGENT_HOST", f"{origin}/ok/")
    mblog = {
        "id": "wb-matrix-images",
        "pics": [
            {"url": server.url("/ok/wb-img-1")},
            {"url": server.url("/ok/wb-img-2")},
            {"url": server.url("/ok/wb-img-3")},
        ],
    }
    crawler = WeiboCrawler()
    crawler.wb_client = SimpleNamespace(proxy=None, headers={})

    await crawler.download_media(mblog)

    directory = media_dir(tmp_path, "wb", "wb-matrix-images")
    assert_downloaded(directory, "001.jpg")
    assert_downloaded(directory, "002.jpg")
    assert_downloaded(directory, "003.jpg")
    assert not (directory / "cover.jpg").exists()


@pytest.mark.asyncio
async def test_weibo_core_downloads_media_from_retweeted_status(server, tmp_path):
    """纯转发微博（顶层无媒体）应取原博媒体，目录按转发帖自身 id 组织"""
    mblog = {
        "id": "wb-retweet-root",
        "retweeted_status": {
            "id": "wb-origin-post",
            "page_info": {
                "type": "video",
                "page_pic": {"url": server.url("/ok/wb-rt-cover")},
                "media_info": {"mp4_hd_mp4": server.url("/ok/wb-rt-video?ct=video/mp4")},
            },
        },
    }
    crawler = WeiboCrawler()
    crawler.wb_client = SimpleNamespace(proxy=None, headers={})

    await crawler.download_media(mblog)

    # 目录归属转发帖 id，媒体取自原博
    directory = media_dir(tmp_path, "wb", "wb-retweet-root")
    assert_downloaded(directory, "cover.jpg")
    assert_downloaded(directory, "video.mp4")
    assert not media_dir(tmp_path, "wb", "wb-origin-post").exists()


# --------------------------------------------------------------------------- 开关关闭分支


@pytest.mark.asyncio
@pytest.mark.parametrize("platform", ["ks", "wb", "bili"])
async def test_media_switch_off_downloads_nothing(server, tmp_path, monkeypatch, platform):
    """xhs/dy 的关闭分支已在 test_live_photo_switch_and_pairing_through_core 覆盖，
    这里补齐 ks/wb/bili：关闭后既不发请求也不建目录"""
    monkeypatch.setattr(config, "ENABLE_GET_MEDIA", False)
    payloads = {
        "ks": {"photo": {"id": "ks-off", "photoUrl": server.url("/ok/ks-off-video"),
                         "coverUrl": server.url("/ok/ks-off-cover")}},
        "wb": {"id": "wb-off", "pics": [{"url": server.url("/ok/wb-off-img")}]},
        "bili": {"View": {"aid": 1, "cid": 2, "bvid": "BV1off", "pic": server.url("/ok/bili-off-cover")}},
    }
    crawlers = {
        "ks": (KuaishouCrawler, "ks_client", {}),
        "wb": (WeiboCrawler, "wb_client", {}),
        "bili": (BilibiliCrawler, "bili_client", {}),
    }
    cls, attr, headers = crawlers[platform]
    crawler = cls()
    setattr(crawler, attr, SimpleNamespace(proxy=None, headers=headers))

    semaphore = asyncio.Semaphore(1) if platform == "bili" else None
    if platform == "bili":
        async def boom_play_url(*args, **kwargs):  # 开关关闭时甚至不应请求 playurl
            raise AssertionError("ENABLE_GET_MEDIA=False 时不应请求 playurl")
        monkeypatch.setattr(crawler, "get_video_play_url_task", boom_play_url)
        await crawler.download_media(payloads[platform], semaphore)
    else:
        await crawler.download_media(payloads[platform])

    assert server.request_count == 0
    assert not media_dir(tmp_path, platform, {
        "ks": "ks-off", "wb": "wb-off", "bili": "BV1off",
    }[platform]).exists()


# --------------------------------------------------------------------------- bilibili 真实合流


def _generate_tiny_streams(tmp_path: Path) -> tuple[bytes, bytes]:
    """用本机 ffmpeg 生成最小可用的 h264 视频轨与 aac 音轨"""
    assert FFMPEG, "本机未安装 ffmpeg"
    video = tmp_path / "gen_video.mp4"
    audio = tmp_path / "gen_audio.m4a"
    subprocess.run(
        [FFMPEG, "-y", "-loglevel", "error",
         "-f", "lavfi", "-i", "testsrc=duration=0.5:size=128x96:rate=10",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-video_track_timescale", "10000",
         str(video)],
        check=True,
    )
    subprocess.run(
        [FFMPEG, "-y", "-loglevel", "error",
         "-f", "lavfi", "-i", "sine=frequency=440:duration=0.5",
         "-c:a", "aac", str(audio)],
        check=True,
    )
    return video.read_bytes(), audio.read_bytes()


@pytest.mark.asyncio
async def test_bilibili_dash_real_ffmpeg_merge(server, tmp_path):
    """端到端真实合流：不 mock merge 与 ffmpeg 探测，
    验证 core 编排 -> 两轨下载 -> ffmpeg 合流 -> 产出可校验的 video.mp4"""
    video_bytes, audio_bytes = _generate_tiny_streams(tmp_path)
    server.contents.update({"dash-real-v": video_bytes, "dash-real-a": audio_bytes})

    crawler = BilibiliCrawler()
    crawler.bili_client = SimpleNamespace(proxy=None, headers={})

    async def fake_play_url(aid, cid, semaphore, fnval=None):
        return {
            "dash": {
                "video": [{"id": 80, "codecid": 7,
                           "base_url": server.url("/ok/dash-real-v?ct=video/mp4")}],
                "audio": [{"id": 30280,
                           "base_url": server.url("/ok/dash-real-a?ct=audio/mp4")}],
            }
        }

    crawler.get_video_play_url_task = fake_play_url

    video_item = {"View": {"aid": 1, "cid": 2, "bvid": "BV1realmerge",
                           "pic": server.url("/ok/bili-real-cover")}}
    await crawler.download_media(video_item, asyncio.Semaphore(1))

    output = media_dir(tmp_path, "bili", "BV1realmerge") / "video.mp4"
    assert output.is_file() and output.stat().st_size > 0, "DASH 合流产物 video.mp4 应存在"

    # 用 ffprobe 校验产物确实是可播放的 mp4，且包含视频轨与音频轨
    probe = subprocess.run(
        [FFPROBE, "-v", "error", "-show_streams", "-of", "json", str(output)],
        capture_output=True, text=True, check=True,
    )
    streams = json.loads(probe.stdout)["streams"]
    codecs = {stream["codec_type"] for stream in streams}
    assert codecs == {"video", "audio"}, f"合流产物应含视频轨与音频轨，实际: {codecs}"

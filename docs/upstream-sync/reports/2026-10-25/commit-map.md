# Commit Map（上游提交映射）— 2026-10-25

- 同步范围：`076dcba978b1..8f583999006d`（upstream/main，2026-07-16 → 2026-10-15，共 38 个提交）
- 移植载体：分支 `upstream-recon2`（逐提交补丁重建，blob SHA 与上游 HEAD 全量校验一致）→ 三方合并提交 `2576d018`
- 类别规则遵循 `docs/Impl/WeMediaCrawler_上游同步与抓取恢复实施方案.md` §2.3

## A. 平台抓取 / 解析 / 签名 / 分页 / 登录态（全部移植）

| 上游 SHA | 日期 | 标题 | 二改落点 | 测试 | 决定 |
|---|---|---|---|---|---|
| `17f66121e0fc` | 07-24 | fix: 升级 xhshow 至 0.2.0, 移除 GET 签名猴子补丁 | `pyproject.toml`/`requirements.txt`/`uv.lock`（xhshow>=0.2.0）、`media_platform/xhs/playwright_sign.py`（删除 fork 自带的 `_patch_xhshow_a3_hash` monkey patch） | 既有签名路径由 `tests/test_xhs_*` 覆盖；`uv sync --locked` 后 `playwright_sign` 导入验证通过（0.2.0 实装） | 直接移植。fork 的 monkey patch 是对 xhshow 0.1.9 GET a3_hash bug（Cloxl/xhshow#104）的本地修复，上游 0.2.0 原生修复后成为双保险且有内部分 API 漂移风险，按上游移除 |
| `04631ba8e451` | 07-30 | fix(weibo): 修复 RFC2822 时间转换丢弃时区偏移导致时间戳晚 8 小时 | `tools/time_util.py` | 上游新增时间测试随合并带入（tools 相关断言） | 直接移植 |
| `2e558f135264` | 08-03 | fix(kuaishou): 支持网页端 REST 接口签名请求 | `media_platform/kuaishou/{client,core}.py` | `tests/test_kuaishou_url_parse.py` 等 | 直接移植 |
| `02294b9ea45b` | 08-03 | style(kuaishou): 优化终端日志输出为条目摘要 | `media_platform/kuaishou/core.py` | 无（日志展示） | 直接移植 |
| `071c8c0acaec` | 08-05 | fix(kuaishou): 降低服务端限流概率并支持限流退避重试 | `media_platform/kuaishou/{client,core}.py` | `tests/test_kuaishou_unavailable_video.py` | 直接移植（重试次数有上限、每次重新签名，符合"不规避平台限制"约束：退避后仍受限则抛错终止） |
| `17c6d386b8bc` | 08-08 | fix(bilibili): 修复缺失置顶评论 | `media_platform/bilibili/core.py` | `tests/test_bilibili_client_comments.py` | 直接移植 |
| `6937b1273853` | 08-11 | 修复小红书原始响应错误分类与重复重试 | `media_platform/xhs/{client,exception}.py`（新增 `PlatformAccessError`、原始响应 JSON 错误分类、300011 安全限制、401/403/429 直接抛不可重试异常） | `tests/test_xhs_raw_response_errors.py`、`tests/test_xhs_core_access_error.py` | 直接移植。**这是 xhs 采集链路的核心可靠性修复**（见 target-platform-diagnosis.md） |
| `508abc504f0a` | 08-11 | 补全小红书响应与重试回归测试 | `tests/test_xhs_raw_response_errors.py` 等 | 同上 | 直接移植 |
| `d594c20c13f4` | 08-11 | fix(xhs,bilibili): 修复访问受限异常击穿与评论采集边界问题 | `media_platform/xhs/core.py`（gather 批次内单条访问受限不再击穿整批）、`media_platform/bilibili/{core,client}.py` | `tests/test_xhs_core_access_error.py`、`tests/test_bilibili_client_comments.py` | 直接移植 |
| `9cfc1485774b` | 09-18 | fix(bili): 兼容首页新版 header 的登录入口选择器 | `media_platform/bilibili/login.py` | `tests/test_bilibili_login_state.py` | 直接移植 |
| `c03ab60aac59` | 09-18 | fix(bili): 登录态判定改为校验 cookie 有效性，避免静默降级到 480P | `media_platform/bilibili/{login,client}.py` | `tests/test_bilibili_login_state.py` | 直接移植 |
| `eec25bb0a027` | 09-18 | fix(xhs): 适配上游 EF* 分档，修复视频只下到封面 | `media_platform/xhs/media.py` | `tests/test_media_extractors.py` | 直接移植（随媒体架构原子迁移） |
| `281b445f5290` | 09-18 | chore(xhs): 更新 XHS_SPECIFIED_NOTE_URL_LIST 示例笔记 | `config/xhs_config.py` | 无 | 直接移植（示例 URL 更新） |
| `cf513e70a13a` | 09-18 | fix(dy): 补上 detail 接口的 uifid/verifyFp 风控参数 | `media_platform/douyin/{client,core}.py` | `tests/test_douyin_aweme_detail_params.py` | 直接移植 |
| `1e1ae64cb424` | 09-18 | fix(ks): 视频不可用时 photo 为 null 导致整轮爬取崩溃 | `media_platform/kuaishou/{client,core}.py` | `tests/test_kuaishou_unavailable_video.py` | 直接移植 |
| `c7e6c9fdc097` | 09-18 | feat(ks): 支持分享短链 /f/<token> 形式的视频输入 | `media_platform/kuaishou/help.py` | `tests/test_kuaishou_url_parse.py` | 直接移植 |
| `8ecfa31de22c` | 09-18 | chore(ks): 示例配置改用分享短链并补上支持的输入形式 | `config/ks_config.py` | 无 | 直接移植 |
| `380b426000aa` | 09-19 | fix(dy): 补上 ArgusSecurityPlugin 要求的 x-tt-argus 请求头 | `media_platform/douyin/client.py` | `tests/test_douyin_argus_header.py` | 直接移植 |

## B. 统一媒体下载器（原子迁移，`0ca7b29cf075`）

| 上游 SHA | 日期 | 标题 | 二改落点 | 测试 |
|---|---|---|---|---|
| `0ca7b29cf075` | 09-17 | feat(media): 重构媒体下载，支持 xhs/dy/ks/bili/wb 五平台 | 新增 `media_downloader/{__init__,downloader,ffmpeg,paths,types}.py`；新增 `media_platform/{xhs,douyin,kuaishou,bilibili,weibo}/media.py`；`base/base_crawler.py` 移除旧 AbstractStoreImage/Video 接口；**删除旧实现** `store/{xhs,douyin,bilibili,weibo}/*_store_media.py`（kuaishou 本就无媒体存储）；`cmd_arg/arg.py` 新增 `--get_media`；`config/base_config.py` `ENABLE_GET_MEIDAS`→`ENABLE_GET_MEDIA`；`api/schemas/crawler.py` 新增 `enable_media`；`api/services/crawler_manager.py` 传 `--get_media`；WebUI types/store/api/panel/i18n 补齐 | `tests/test_media_downloader.py`、`test_media_extractors.py`、`test_media_ffmpeg.py`、`test_media_core_integration.py`、`test_cmd_arg_media.py`（e2e 默认跳过） |

迁移完整性核对：
- 旧标识 `ENABLE_GET_MEIDAS` 全仓 grep = 0 处残留；
- 旧 `store/*/*_store_media.py` 与 `client.get_note_media()`（xhs）等旧媒体 GET 路径全部删除，无双实现并存；
- tieba/zhihu 无 media.py、无媒体宣称，符合上游边界；
- WebUI `enable_media` 从 fork 版 `CrawlerConfigPanel.tsx`（合并时保留二改布局后手工补入开关，样式沿用二改设计）→ `crawlerStore`/`types`/`lib/api.ts` → API schema → manager `--get_media` → CLI → `config.ENABLE_GET_MEDIA` 全链贯通；
- `tests/test_api_limits.py::test_crawler_manager_passes_media_switch`、`test_api_schema_exposes_media_switch_default_off` 验证契约；
- ffmpeg 可选可诊断（本机已装，测试实际跑通；`is_available()` 为 False 时报错降级）。

## C. Merge 提交（3 个，recon 中为空操作）

| 上游 SHA | 标题 | 处理 |
|---|---|---|
| `1779dde9725f` | Merge PR #950（weibo RFC2822） | 其内容 = `04631ba8e451`，已单独应用；recon 重建时跳过，最终树校验证明无遗漏 |
| `7fd42cf4481f` | Merge PR #957（bilibili top） | 其内容 = `17c6d386b8bc`，同上 |
| `3c25521bbb53` | Merge PR #958（xhs raw response） | 其内容 = `6937b1273853` + `508abc504f0a`，同上 |

## D. README / 文档 / 展示类（16 个，评估后不采纳代码外内容）

`0625e01a6bc7`、`e6e863a1d323`、`2a8063a9f2ec`、`439509782cc2`、`5665a271ef15`、`d6f7c5bb906b`、`60e66f2a9258`、`bf28178082bc`、`83c638b9d1b4`、`5d547f45862c`、`93c405f89a8b`、`098cae5a0002`、`e9dd17a16338`、`156c602c8d68`、`19c956c96272`、`8f583999006d`（07-16 → 10-15，内容均为 README 赞助商/星标图/Pro 介绍/文档措辞）。

- **决定：不覆盖二改 README。** 合并冲突按 `--ours` 解决（保留二改品牌、部署地址与文案）。
- 与代码行为相关的事实已随代码注释/配置说明带入（如媒体下载支持平台 xhs/dy/ks/bili/wb 的说明位于 `config/base_config.py` 注释与 WebUI 提示文案，与实际实现一致——tieba/zhihu 未宣称媒体支持）。
- 其涉及上游推广/赞助的表述与二改产品无关，记录为"评估过，无需移植"。

## E. 依赖与锁文件

| 文件 | 变化 | 验证 |
|---|---|---|
| `pyproject.toml` / `requirements.txt` | `xhshow>=0.1.9` → `>=0.2.0` | `uv lock --check` 通过；`uv sync --locked` 通过（清华镜像 403 为暂时性，重试成功）；0.2.0 实装后全量测试通过 |
| `uv.lock` | 随上游（xhshow 0.2.0 等） | 同上 |

## F. 测试文件清单（随合并带入的上游新测试）

`tests/test_xhs_core_access_error.py`、`test_xhs_raw_response_errors.py`、`test_douyin_argus_header.py`、`test_douyin_aweme_detail_params.py`、`test_kuaishou_unavailable_video.py`、`test_kuaishou_url_parse.py`、`test_bilibili_client_comments.py`、`test_bilibili_login_state.py`、`test_cmd_arg_media.py`、`test_media_downloader.py`、`test_media_extractors.py`、`test_media_ffmpeg.py`、`test_media_core_integration.py`、`test_media_e2e.py`（默认跳过）+ fixture 服务器 `tests/media_server.py`。

等价改写 1 处：`test_media_ffmpeg.py::test_merge_kills_subprocess_when_cancelled` 的 Windows 分支（原实现依赖 `/bin/sh`+`pgrep`，详见 test-report.md）。

## G. 二改侧保护核对（合并后确认仍在）

- `api/main.py`：fork 的 CORS 中间件（本轮已收紧为 allow-list）、phone 登录选项 ✓
- `api/schemas/crawler.py`：fork 的 `cdp_auto_launch` ✓；`api/services/crawler_manager.py`：`MEDIACRAWLER_CDP_CONNECT_EXISTING` 环境变量联动 ✓
- `config/base_config.py`：`MEDIACRAWLER_CDP_CONNECT_EXISTING` 环境变量覆盖 ✓（与上游 `ENABLE_GET_MEDIA` 重命名共存于同一文件）
- WebUI：fork 的组件结构、品牌、i18n、vite 配置、GitHub Pages 工作流、Dockerfile/.dockerignore/railway.json/RAILWAY_DEPLOY.md、CLAUDE.md 全部保留 ✓
- LICENSE：NON-COMMERCIAL LEARNING LICENSE 1.1 未改动 ✓

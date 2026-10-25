# Release Notes（草稿）— 2026-10-25

> 本文件是建议的下一版发行说明草稿，**未发布**。按项目约束：创建 PR、push、发版需人工审查后执行。
> 版本评估：仓库当前无 git tag、无既定发版节奏（pyproject `0.1.0` / webui `1.0.0`，二者不同步）。
> 本轮为"上游同步 + 采集链路修复 + 媒体功能引入"的功能级变更，若启用版本号建议 **pyproject 0.1.0 → 0.2.0**（minor：新增媒体下载能力），webui 版本一并对齐；是否发版由维护者决定。

---

## WeMediaCrawler 0.2.0（草稿）

### Highlights

- **同步上游 NanmiCoder/MediaCrawler main（2026-07-16 → 2026-10-15，38 个提交）**，覆盖小红书/抖音/快手/B站/微博的请求契约、错误分类、限流退避、评论边界与登录态判定修复。
- **媒体下载功能端到端引入**：统一 `media_downloader/` + 五平台 `media.py` 适配器 + WebUI 开关（`--get_media` / `enable_media` / `ENABLE_GET_MEDIA`）。支持 xhs / dy / ks / bili / wb（tieba、zhihu 数据结构无媒体字段，不支持，UI 有明确提示）。旧 `store/*/*_store_media.py` 已移除，避免双实现。
- **WebUI/API 启动链路修复**：`start.ps1` 不再指向已失效的旧项目路径，后端端口统一为 8083（与 `webui/vite.config.ts` 代理一致）。
- **安全**（代码评审后强化）：
  - API CORS 从"反射任意 Origin + 凭证"收紧为 allow-list（本机开发来源 + 同源 + `MEDIACRAWLER_CORS_EXTRA_ORIGINS` 显式扩展），预检头放行前端必发的 `ngrok-skip-browser-warning`；
  - WebSocket（`/api/ws/logs`、`/api/ws/status`）握手增加同一 Origin allow-list 校验（防跨站 WebSocket 劫持读取日志/状态）；
  - 启动日志对 `--cookies` 参数值脱敏（日志会经 WS 广播并重放，Cookie 不再进入日志面）；
  - `start.ps1`/`stop.ps1` 纳入版本跟踪：项目根自动定位、端口 8083 与 vite 代理一致、ngrok 路径参数化（`MEDIACRAWLER_NGROK_EXE`）、公网隧道改为 `-Tunnel` 显式开启（API 无认证，默认不再暴露公网）。公网部署（ngrok/Railway）时请用环境变量声明允许的跨域来源。

### 平台修复明细（来自上游，均已带回归测试）

- 小红书：原始响应错误分类（IP 限制 300012 / 安全限制 300011 / 笔记不存在 / 业务错误），401/403/429 不再无谓重试；批次内单条访问受限不再击穿整轮；签名升级 xhshow 0.2.0 并移除本地 monkey patch；视频媒体适配 EF\* 清晰度分档（不再只下封面）。
- 抖音：detail 请求补 `uifid/verifyFp` 风控参数；补 `x-tt-argus` 请求头。
- 快手：网页端 REST 接口签名；限流退避重试（有限次数、重新签名）；`/f/<token>` 分享短链输入；不可用视频 `photo=null` 不再使整轮崩溃。
- B 站：置顶评论不再缺失；最大评论数/子评论循环边界；登录态改为校验 Cookie 有效性（避免静默降级 480P）；兼容首页新版登录入口选择器；DASH 合流依赖可选 ffmpeg（缺失可诊断）。
- 微博：RFC2822 时间戳时区偏移修复（不再整体偏移 8 小时）。

### Fixed

- 隐私回归测试在 Windows/Git Bash 下的误报（grep 路径解析问题改为 Python 原生扫描，断言不变）。
- ffmpeg 合流取消-孤儿进程回归测试的 Windows 兼容（等价改写，断言不变）。
- CORS allow-list（详见安全项）。

### Upgrade Notes

- 配置项 `ENABLE_GET_MEIDAS` 更名为 `ENABLE_GET_MEDIA`（全仓无旧拼写残留）。若你从旧版 `.env` 或脚本注入该配置，请同步改名。
- 媒体文件新目录约定：`{SAVE_DATA_PATH 或 data}/{platform}/media/{内容ID}/`。旧版 `store/*/*_store_media.py` 的输出路径不再生成。
- B 站 DASH 合流需要本机 ffmpeg（可选；缺失时明确报错并降级，不隐式安装）。

### Known Issues / 未验证

- 本轮离线测试全绿（tests/ 314 passed），但 **7 个平台均未做在线烟雾测试**（需扫码登录/人工在场），上表平台修复以离线回归 + 上游测试为准。
- `test/` 遗留套件需要本机 Redis/Mongo 等服务，无服务环境下属预期失败。
- WebUI API 目前无认证机制；公网部署建议配合反代认证或跟进上游 PR #974/#975 的访问边界与日志脱敏方案。

### Full Changelog

- 二改侧：`22fbcc60...fix/crawler-recovery-and-upstream-sync`（合并提交 `2576d018`，其后 `672a98c2`、`fcf387ce`、`eb5f1d8a`）
- 上游侧：`076dcba978b1...8f583999006d`（38 个提交清单见 `commit-map.md`）

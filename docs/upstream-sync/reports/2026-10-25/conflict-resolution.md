# Conflict Resolution（冲突解决记录）— 2026-10-25

## 合并方式

- 三方合并：`git merge upstream-recon2 --no-ff`，merge-base `076dcba978b1`。
- `upstream-recon2` = 上游 main HEAD 的逐提交重建（作者/日期/说明保留，树经 blob SHA 全量校验）。
- 自动合并成功：`api/schemas/crawler.py`、`api/services/crawler_manager.py`、`config/base_config.py`、`cmd_arg/arg.py`、`base/base_crawler.py`、全部 `media_platform/`、`store/`、`tools/`、`tests/`、`pyproject.toml`、`uv.lock`、WebUI types/store/lib/i18n 等 72 个文件。
- 人工冲突：4 个文件（下表）。

## 冲突逐条记录

| 文件 | 冲突原因 | 解决方式 | 语义核对 |
|---|---|---|---|
| `README.md` | 上游 16 个 README/赞助商提交 vs 二改品牌重写 | `--ours`（保留二改） | 二改品牌名 WeMediaCrawler、部署文案、GitHub Pages/Railway 说明完整保留；上游赞助商内容按方案 §2.3"展示类"规则不采纳 |
| `README_en.md` | 同上 | `--ours` | 同上 |
| `README_es.md` | 同上 | `--ours` | 同上 |
| `webui/src/components/config/CrawlerConfigPanel.tsx` | 上游在基线版面板上加了 `enable_media` 复选框（+17 行）；二改对整个面板做了重写（登录方式建议、Cookie 指引、ParsedIdList 等） | `--ours` 保留二改面板，**随后手工移植功能字段**：lucide 导入加 `Image as ImageIcon`，在"子评论"与"无头模式"之间按二改的样式约定（`id="field-enableMedia"`、cyber-* class、`min-w-0 flex-1` 结构）插入媒体开关，i18n 键 `field.downloadMedia`/`downloadMediaHint` 由上游提交自动合并进入两个 locale 文件 | 开关读写 `config.enable_media`，与 `crawlerStore`/`types/crawler.ts`/`lib/api.ts`/后端 schema/manager/CLI 全链同名同型；`npm run build`（含 tsc -b）通过；未覆盖二改任何布局与交互 |

## 自动合并结果的逐项核对（抽查重点）

| 文件 | 核对项 | 结果 |
|---|---|---|
| `config/base_config.py` | 上游 `ENABLE_GET_MEIDAS`→`ENABLE_GET_MEDIA` 重命名 + 二改 `MEDIACRAWLER_CDP_CONNECT_EXISTING` 环境变量覆盖 | 两者共存（:113 与 :83-85），旧拼写全仓 grep = 0 |
| `api/schemas/crawler.py` | 上游 `enable_media` 字段 + 二改 `cdp_auto_launch` | 共存（:74 与 :79） |
| `api/services/crawler_manager.py` | 上游 `--get_media` + 二改 `cdp_auto_launch`→env 联动 | 共存（:232 与 start() 内 env 构造） |
| `cmd_arg/arg.py` | `--get_media` 注册、bool 解析、默认值取 `config.ENABLE_GET_MEDIA` | `main.py --help` 实测可见参数 |
| `media_platform/xhs/client.py` | 上游错误分类重写与二改无改动（基线一致） | 直接取上游，无二改特性丢失（`XHS_INTERNATIONAL` 为基线已有功能，client 中海外域名切换逻辑随上游版本保留） |
| `store/*` | 旧 `*_store_media.py` 删除、`__init__.py` 媒体分发移除 | 无双实现；`store/xhs/` 仅剩 `__init__.py`、`_store_impl.py` |
| `tests/` | 上游 14 个新测试 + fixture `media_server.py` 进入；二改 14 个既有测试未动 | 全量 314 过 1 跳 |

## 未使用的上游内容（明确记录）

- 上游 README 系列与 `docs/static/images/` 赞助商图片（合并自动带入树中，但 README 冲突以 ours 解决后，README 引用的上游图片变更随 ours 生效；`docs/static/images` 中上游新增的赞助商图未引用、不构成行为差异）。
- 上游 `docs/proxylane/`、赞助商落地页文档（不采纳）。

## 合并后纠偏提交（非冲突，属诊断修复）

| 提交 | 内容 |
|---|---|
| `672a98c2` | CORS allow-list 化（替换 fork 原有的反射任意 Origin 中间件——该中间件在本轮安全审计中被判定为不适合公网暴露的 API）、`tests/test_no_user_info.py` 去除 subprocess grep 依赖（Windows 误报）、新增 `tests/test_api_cors.py`。注意：该提交说明当时误称包含 `start.ps1` 修复，实际 start.ps1/stop.ps1 直到评审修复提交才纳入跟踪（见下一条） |
| `fcf387ce` | `tests/test_media_ffmpeg.py` 取消-孤儿进程用例的 Windows 等价分支 |
| `eb5f1d8a` | pre-commit 钩子自动补齐版权头与空白规范化（上游新文件进入二改仓库后需符合其头文件规范） |

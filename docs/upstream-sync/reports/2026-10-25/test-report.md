# Test Report（测试报告）— 2026-10-25

环境：Windows 10 (10.0.22631) / Git Bash / Python 3.11 (uv) / Node（webui）。所有命令实际执行，结果如实记录。

## 1. 现代测试套件 `tests/`（主套件）

| 命令 | 结果 |
|---|---|
| `./.venv/Scripts/python.exe -m pytest tests/ -q`（合并后、修复前） | **1 failed, 313 passed, 1 skipped**（首轮基线为 1 failed, 76 passed——当时套件尚小） |
| `./.venv/Scripts/python.exe -m pytest tests/ -q`（最终，提交 `eb5f1d8a` 后复跑两次） | **314 passed, 1 skipped, 1 warning** |

- 唯一 skipped：`tests/test_media_e2e.py:59` — `真实平台测试，设置 MEDIA_E2E=1 后运行`（上游设计为手动门控，非静默跳过）。
- 修复过程中实际失败的用例及处置：
  1. `test_no_user_info.py::test_store_no_forbidden_dict_keys`（合并前后都失败）— 根因：测试以 Windows 反斜杠路径调用 MSYS grep，路径被错误解析后递归扫描整个仓库（命中 .venv）。**不是隐私回归**。修复为 Python 原生源码扫描（`672a98c2`），断言语义不变，修复后该文件 11/11 通过。
  2. `test_media_ffmpeg.py::test_merge_kills_subprocess_when_cancelled`（合并引入）— 根因：上游实现为 POSIX 专属（`/bin/sh` + `exec` + `pgrep`），Windows 报 `OSError [WinError 193]`。按方案"允许等价改写"处理：保留 POSIX 分支不动，新增 Windows 分支（patch `create_subprocess_exec` 生成记录 PID 的单进程 python 睡眠子进程，取消后用 `OpenProcess(SYNCHRONIZE)` 断言进程消失）。断言强度不变（仍验证"取消不留下孤儿 ffmpeg 进程"），`fcf387ce`，修复后该文件 5/5 通过。

新增测试（本轮编写）：
- `tests/test_api_cors.py`：6 个用例覆盖 CORS allow-list（本地开发来源放行、同源放行、任意来源拒绝、预检拒绝、`MEDIACRAWLER_CORS_EXTRA_ORIGINS` 环境变量），全部通过。

## 2. 遗留测试套件 `test/`（服务依赖）

| 命令 | 结果 |
|---|---|
| `./.venv/Scripts/python.exe -m pytest test/ -q` | **6 failed, 9 passed, 8 skipped, 4 subtests passed** |

- 6 个失败全部是 `redis.exceptions...` 连接类错误（`test_proxy_ip_pool.py` 2 项、`test_redis_cache.py` 3 项等）——本机无 Redis 服务，属环境性失败，与 AGENTS.md 对该目录"需要活 Redis/Mongo/代理"的记载一致。**非本轮回归**（合并前同样无法通过，无 Redis 可用）。
- 未为本轮搭建 Redis 服务重跑（方案允许记录环境限制；如需完整验证可在有 Redis 的环境执行）。

## 3. API/CLI 契约验证（离线，全部通过）

| 验证 | 方式 | 结果 |
|---|---|---|
| manager 命令构造 | 实例化 `CrawlerManager()._build_command(CrawlerStartRequest(...))` | 输出含 `--platform/--lt/--type/--save_data_option/--keywords/--get_comment/--get_sub_comment/--headless`，与 cmd_arg 注册一致 |
| 媒体开关契约 | `tests/test_api_limits.py::test_crawler_manager_passes_media_switch`、`test_api_schema_exposes_media_switch_default_off` | 通过 |
| CLI 参数 | `main.py --help` | `--get_media`（"Whether to download media files (cover/video/images)"）与 `--get_comment` 等可见 |
| API 进程内可启动 | `tests/test_api_limits.py` 以 TestClient 实际调用 `/api/crawler/*` 路由 | 通过 |
| WebUI 类型链 | `webui/src/types/crawler.ts`/`crawlerStore.ts`/`lib/api.ts`/i18n 键与后端 schema 同名同型 | grep 实证 + 构建通过 |

## 4. 依赖与锁文件

| 命令 | 结果 |
|---|---|
| `uv lock --check` | 通过（Resolved 92 packages，锁文件与 pyproject 一致） |
| `uv sync --locked` | **首次失败**：清华镜像对 `xhshow-0.2.0` wheel 返回 403；重试后**通过**（Checked 90 packages）。过程中曾临时从官方 PyPI 安装 0.2.0 验证代码兼容，最终环境由锁文件同步就位 |
| xhshow 实装版本 | 0.2.0；`from media_platform.xhs import playwright_sign` 导入验证通过（monkey patch 已移除） |

## 5. 静态检查

| 命令 | 结果 |
|---|---|
| `pre-commit run --all-files`（两轮） | 第二轮 **9/9 hooks Passed**。第一轮自动修复：为上游新带来的 31 个文件补版权头、行尾/文件尾规范化（符合仓库头文件规范，见 `eb5f1d8a`） |
| `mypy` | **未执行**——mypy 未在 pyproject 依赖中声明、venv 中未安装，文档中的 `uv run mypy .` 实际不可用（`program not found`）。未为运行检查而擅自添加依赖；建议后续将 mypy 加入 dev 依赖后再启用 |

## 6. 前端构建

| 命令 | 结果 |
|---|---|
| `cd webui && npm ci` | 成功（esbuild postinstall 待 allow-scripts 白名单警告，不影响构建） |
| `cd webui && npm run build`（`tsc -b && vite build`） | **成功**：1836 modules，输出 `gh-pages-dist/`（index 1.06 kB / css 51.16 kB / js 549.01 kB），仅 chunk>500kB 提示（与合并前一致，非回归） |

## 7. 真实平台烟雾测试

**未执行。** 阻塞点：xhs qrcode 需人工扫码、本机无 xhs 登录态；dy 旧登录态已 3 个月未用且 CDP 会拉起真实浏览器，无人值守不满足"手动触发 + 低频 + 用户授权样本"约束。具体建议命令见 target-platform-diagnosis.md §5。**因此所有 7 个平台均标记为"未在线验证"。**

## 8. 汇总门槛核对（方案 §7.3）

- [x] 离线回归全绿（tests/ 314 过）
- [x] API schema / manager / CLI / config / WebUI 契约测试通过
- [x] 旧媒体实现与新媒体下载器无双调用（旧文件删除、旧标识 0 残留）
- [x] uv.lock / npm lockfile / 构建输出一致
- [x] 二改 WebUI 自定义、部署文件保留；CORS 收紧有回归测试
- [ ] 目标平台受控在线烟雾测试 —— **未执行（用户不在场），未声称恢复**
- [x] 未删除任何既有测试；仅有的测试改动为修复环境误报与平台等价分支（断言未弱化）

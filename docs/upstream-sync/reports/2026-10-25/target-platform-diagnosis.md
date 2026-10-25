# 目标平台采集链路诊断报告 — 2026-10-25

## 1. 目标平台判定（含不确定性声明）

| 证据 | 内容 | 指向 |
|---|---|---|
| `config/base_config.py` | `PLATFORM="xhs"`、`CRAWLER_TYPE="search"`、`KEYWORDS="编程副业,编程兼职"`、`LOGIN_TYPE="qrcode"`、`SAVE_DATA_OPTION="jsonl"`、`ENABLE_CDP_MODE=True` | xhs search |
| `browser_data/` | 仅存在 `cdp_dy_user_data_dir`（2026-07-14）、`dy_user_data_dir`（2026-07-13），**无 xhs 登录态**；时间距今 3 个月以上 | 历史上实际跑过的是抖音 |
| `data/` | 空。无任何 jsonl/csv/db 产物 | 本目录内无成功落盘记录 |
| 日志 | 仓库内无日志文件 | — |
| `start.ps1`（未跟踪用户脚本） | 后端入口 `uvicorn api.main:app`，WebUI 驱动使用方式 | 真实入口是 WebUI→API→CLI |

**结论（待用户确认）：** 静态证据不足以断言"当前实际目标平台"。配置指向 xhs search（但与上游默认值相同，可能是未改过的默认），浏览器登录态指向 dy（但停留在 7 月中旬）。二者都不是"现在正在失败的任务"的直接证据。以下诊断覆盖两个平台的共性问题与已证实的环境阻断点；**目标平台的最终确认与在线验证需要用户补充信息**（见 §6）。

## 2. 已证实的问题（按数据流分层，附证据）

### L0. 启动入口层（阻断级，已修复）
- **`start.ps1` 指向不存在的目录** `$projectRoot = "D:\Git-Clone\SRC\MediaCrawler"`——仓库已改名 WeMediaCrawler，该路径下无项目。用此脚本启动时后端进程 WorkingDirectory 无效，`/api/health` 检查必失败，脚本 `exit 1`。**如果用户经此脚本使用 WebUI，这就是"页面能操作但抓取不工作"的最直接解释之一**（WebUI 静态页在 GitHub Pages 可打开，但后端从未起来）。
  - 证据：`ls D:/Git-Clone/SRC/MediaCrawler` → 不存在；脚本内容见 git 历史（未跟踪文件）。
  - 修复：`$projectRoot` 改为从脚本自身位置推导（评审后发现 672a98c2 提交说明误称包含此修复，实际随评审修复提交 `start.ps1`/`stop.ps1` 纳入版本跟踪时落地）。
- **端口三处不一致**：start.ps1 后端 9090，`webui/vite.config.ts` 代理 `/api`→`localhost:8083`，CLAUDE.md 写 8080。即使后端起来，vite dev 前端也连不上。
  - 修复：start.ps1 统一为 8083（与受版本控制的 vite 代理一致）；stop.ps1 原本就清理 8083，无需改。

### L1. 前端请求层 / L2. API 任务层
- 合并前：`api/schemas/crawler.py`、`crawler_manager._build_command()` 无 `enable_media`/`--get_media`；WebUI 也无媒体开关（方案文档所述"二改前端已有 enable_media 控件"经核实**不成立**——fork 的 `CrawlerConfigPanel.tsx` 从未包含该控件）。媒体功能在 fork 中端到端缺失，而非仅契约断裂。
- 合并后：全链贯通（commit-map.md §B）。离线契约测试通过（`test_crawler_manager_passes_media_switch` 等）。
- WebUI→API 的结构化采集参数（platform/keywords/get_comment 等）合并前后契约完整：`CrawlerStartRequest` 字段与 `_build_command()` 输出逐项对应（本轮离线实测命令行构造正确）。

### L3. CLI/配置层
- `cmd_arg/arg.py` 合并前无 `--get_media`；`config/base_config.py` 用拼写错误的 `ENABLE_GET_MEIDAS`。
- 合并后 `--get_media` 注册且默认值取自 `config.ENABLE_GET_MEDIA`（`main.py --help` 实测可见）；旧拼写全仓 0 残留。

### L4. Crawler Factory / L5. 平台 core 层（xhs）
- fork 的 `media_platform/xhs/core.py` 在 gather 批次中，单条笔记访问受限（IPBlockError 等）会**击穿整个批次**；`get_creators_and_notes` 遇访问受限直接中断整轮。
- 上游 `d594c20c13f4`/`6937b1273853` 修复：访问受限异常隔离为跳过单条 + 明确日志（含"建议降低采集频率、更换 IP 或检查账号状态"提示），批次内其余结果保留。已随合并移植，`tests/test_xhs_core_access_error.py` 离线回归通过。

### L6. 平台 client 层（xhs）——最可能的采集故障根因
fork 的 `XiaoHongShuClient.request()`（合并前）：
- 471/461 验证码分支外，直接 `data["success"]` 判定；`data["code"]` 非预期值时走 `else` 分支甚至可能 `KeyError`（响应体没有 code/success 字段时）；
- IP 限制（code 300012）抛 `IPBlockError` 但**重试装饰器未排除它**，tenacity 会继续重试 3 次（对限流重试=放大风控风险）；
- 不识别 300011（账号安全限制）、401/403/429 等访问控制信号；
- 响应为非 JSON（如被风控拦截返回 HTML）时 `response.json()` 直接抛异常，错误信息无分类。

上游 `6937b1273853` + `d594c20c13f4` 修复（已移植）：原始响应先解析分类（IP 限制/安全限制/笔记不存在/业务错误各归各类）、401/403/429 与 300011 抛不可重试的 `PlatformAccessError`、tenacity `retry_if_not_exception_type` 排除不可重试异常。**当 XHS 风控策略变化返回新错误形态时，旧代码的症状正是"静默 0 条/异常重试/整批失败"，与新代码行为可区分、可记录。** 这与本轮无法取得线上日志的现状互为印证，但**不能据此断言这就是用户遇到的唯一故障**——只能证明旧实现对平台错误契约的覆盖明显不足且无测试。

### L7. 签名层（xhs）
- fork：xhshow 0.1.9 + 本地 monkey patch（`_patch_xhshow_a3_hash`，修 GET a3_hash bug，xhshow#104）。当前环境实测：0.1.9 安装在位、`xhshow.core.crypto.CryptoProcessor` 可导入、patch 生效路径可加载——**签名链本身在当前环境未坏**。
- 但该 patch 依赖 xhshow 内部类结构，`pyproject` 约束 `>=0.1.9` 允许解析到 0.2.x——一旦升级，patch 的行为假设失效（上游 0.2.0 已原生修复该 bug，patch 属于双保险且可能与新实现叠加）。上游 `17f66121e0fc` 升级 0.2.0 并删除 patch，已移植，实装验证导入正常。

### L8. 持久化层
- `store/xhs/`、`database/` 合并前后无二改改动；上游未改持久化 schema（除媒体文件路径新目录约定）。
- 隐私回归测试（`test_no_user_info.py` 等 11 项）合并后全部通过。

### L9. 展示层
- WebUI 数据浏览（DataExplorer）属二改自有功能，合并保留；API `/api/data` 路由未受上游影响。

## 3. 最小修复范围（本轮实际执行）

1. `start.ps1` 路径与端口修复——恢复用户启动入口（脚本随评审修复提交纳入版本跟踪；`672a98c2` 提交说明曾误称包含此项）。
2. 三方合并带入 xhs/dy/ks/bili/wb 全部可靠性修复与新媒体架构（`2576d018`）。
3. CORS 收紧（`672a98c2`）——修复"任意网页可经浏览器驱动公网暴露的 API"问题（ngrok 场景实证相关；评审修复后 start.ps1 隧道改为 opt-in `-Tunnel` 参数）。
4. 测试健壮性修复（`672a98c2`、`fcf387ce`）。

## 4. 未确定项（明确标注）

- 用户当前真实使用的平台/采集类型/入口：**待用户确认**（xhs search 为配置推断，dy 为历史痕迹）。
- 合并前线上故障的直接触发点（登录失效？风控 461/471？签名失败？）：无日志无数据，**无法回溯性断言**，仅能给出上述代码级缺陷清单。
- 在线验证：**未执行**（阻塞点见 §5）。

## 5. 在线烟雾测试阻塞点（如实记录，未执行的测试不写成通过）

- xhs/qrcode 登录需人工扫码；本机无 xhs 登录态。
- dy 有 7 月旧登录态，大概率已过期；且 CDP 模式会拉起真实浏览器窗口，无人值守不满足"手动触发"约束。
- 按方案约束：访问受限/验证码不做无限重试，不擅自放大流量。

**建议的用户验证步骤（单并发、单页、关闭媒体）：**

```bash
uv run main.py --platform xhs --lt qrcode --type search --keywords "编程副业" \
  --crawler_max_notes_count 3 --get_comment false --get_media false
# 成功标准：data/xhs/jsonl/ 出现 ≥1 条记录，note_id 与页面可见内容一致
```

## 6. 根因小结

- **可证实并已修复**：启动脚本失效 + 端口不一致（阻断 WebUI 驱动路径）；媒体功能端到端缺失；xhs 错误处理/重试策略落后于上游（平台错误契约覆盖不足）；CORS 通配。
- **高度疑似但无直接证据**：xhs search 在风控错误形态变化时的静默失败/重试风暴。
- **未证实**：登录态失效、账号级安全限制等需要在线才能确认的假设——不做断言。

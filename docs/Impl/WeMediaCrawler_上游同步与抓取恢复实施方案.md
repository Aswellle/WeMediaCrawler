# WeMediaCrawler 上游同步与抓取链路恢复实施方案

> **用途：** 交给 Codex / Claude Code 等 AI 编程代理，作为一次性恢复任务和后续持续同步任务的执行规范。  
> **基准核查日期：** 2026-10-25  
> **上游仓库：** <https://github.com/NanmiCoder/MediaCrawler>  
> **二改仓库：** <https://github.com/Aswellle/WeMediaCrawler>

---

## 0. 执行摘要与现状判断

本任务不是“把上游 main 合并进来”这么简单，而是同时解决两个目标：

1. **恢复目标平台的真实采集链路。** 必须定位从前端/API/CLI 到平台 crawler、API client、数据解析和持久化的断点。不能把“程序启动成功”“浏览器打开成功”或“日志显示完成”视为抓取成功。
2. **建立可重复、可审计的上游同步机制。** 将上游每次新增的代码改进、功能、缺陷修复和依赖更新引入二改项目，同时保护二改项目的 WebUI、品牌、部署适配和用户体验改进。

### 0.1 已确认的仓库快照

| 项目 | 核查结果 |
|---|---|
| 上游当前主分支 | `NanmiCoder/MediaCrawler`, `main`, HEAD `8f583999006d`（2026-10-15） |
| 二改当前主分支 | `Aswellle/WeMediaCrawler`, `main`, HEAD `22fbcc6013d4`（2026-10-02） |
| 已确认的共同历史基线 | `076dcba978b1`（上游 2026-07-01 附近的版本） |
| 自共同基线后上游新增提交 | **38 个**；应以执行时重新 fetch 得到的实际 SHA 为准 |
| 当前主要风险 | 二改项目保留旧的平台/媒体实现，同时又有自定义 WebUI 和部署改动；抓取层及 API/UI 参数契约已落后于上游 |

**重要说明：** 上述 SHA 和提交数量是本方案编写时的在线核查快照，不是永久常量。Agent 每次启动任务都必须重新获取上游和二改仓库的 HEAD，再生成本轮同步清单。

### 0.2 已发现的具体差异与风险

1. **平台抓取核心存在版本差异。** `media_platform/xhs/`、`douyin/`、`kuaishou/`、`bilibili/`、`weibo/` 的 client/core 等路径与上游当前版本不同。上游近期有多个实际影响请求参数、响应错误分类、登录状态判断、评论分页和限流处理的修复。
2. **媒体下载架构已经重构。** 上游新增 `media_downloader/`，并为小红书、抖音、快手、B 站和微博增加 `media_platform/<platform>/media.py`；旧版 `store/*/*_store_media.py` 及 client 内媒体 GET 方法被移除。二改仓库仍保留旧存储媒体文件，不能仅复制少量新文件，否则容易出现双实现、配置未生效或调用链断裂。
3. **WebUI 与后端之间存在可确认的参数契约缺口。** 二改的 `webui/src/components/config/CrawlerConfigPanel.tsx` 已经渲染 `enable_media` 控件，但二改 `api/schemas/crawler.py` 没有 `enable_media` 字段，`api/services/crawler_manager.py` 也没有把 `--get_media` 传给 CLI；二改 `config/base_config.py` 仍使用拼写错误的 `ENABLE_GET_MEIDAS`，而上游改为 `ENABLE_GET_MEDIA`。这会导致媒体下载开关 UI、API、CLI 和配置之间不一致。
4. **回归测试没有跟上游同步。** 上游新增了针对小红书原始响应错误、访问限制、抖音请求参数、快手 URL/不可用视频、B 站登录状态/评论、媒体下载器和端到端媒体流程的测试。二改需要引入或等价重建这些回归测试，不能只迁移生产代码。
5. **二改前端确实有独立价值，不能被覆盖。** 例如 `CrawlerConfigPanel.tsx` 在二改中有登录方式建议、Cookie 指引和额外交互，二改还包含品牌名、静态前端部署、Railway/Docker 相关配置、可访问性修复及部署文档。必须保留这些产品层改动，并用三方差异解决同路径冲突。
6. **部署安全需单独审计。** 二改历史中有“允许所有来源”的 CORS 修复提交。Agent 必须检查当前 `api/main.py` 的实际中间件与部署暴露面，不能把 `Access-Control-Allow-Origin: *` 当成无条件正确的永久方案；如果 API 可公网访问、提供爬取控制或回传采集数据，应同时评估认证、授权、来源限制和敏感数据暴露。

这些发现可以解释为什么“页面能操作，但抓取功能不工作/部分平台失效”可能是版本漂移导致的，但**不能仅凭静态差异断言是哪一个平台的哪一行代码导致当前线上故障**。第一阶段必须根据当前配置、实际任务输入和脱敏运行日志复现故障。

---

## 1. 任务边界与不可破坏的约束

### 1.1 最终目标

- 修复用户实际使用的目标平台采集流程；随后对所有声明支持的平台执行回归矩阵。
- 从上游同步缺失的功能、bug 修复、依赖和测试。
- 保留二改项目独有的 WebUI/UX、应用名称、前端静态部署、后端部署、启动说明及用户自定义配置。
- 建立以后每次上游有新提交时可以重复执行的流程，形成“拉取上游—分类差异—合并—测试—审查—发布”的闭环。
- 每轮最终给出变更映射、测试证据、未解决风险与回滚点。

### 1.2 禁止操作

Agent **不得**：

- 直接在 `main` 上试验合并、未经确认自动发布，或执行 `git push --force`。
- 直接以整个上游仓库覆盖二改仓库；也不得因为路径冲突而简单选择 `--theirs` 或 `--ours`。
- 为了让测试通过而删除二改 WebUI 功能、API 扩展、部署文件或现有测试。
- 只更新代码而漏掉 `pyproject.toml`、`uv.lock`、`requirements.txt`、API schema、CLI 参数、WebUI 类型和 i18n。
- 在日志、测试 fixture、提交说明或报告中输出完整 Cookie、访问令牌、账号标识、`.env` 内容或私人数据。
- 把验证码/登录验证/平台访问限制当成需要不断重试规避的错误；遇到访问限制应明确分类、降低请求或停止，并遵守平台政策和用户授权范围。
- 在真实平台上跑大规模抓取、并发压力测试或 CI 高频访问。
- 在没有查阅仓库 `LICENSE` 的情况下删除版权声明、改动许可证或默认假定代码可用于商业场景。上游 README 声明项目使用 `NON-COMMERCIAL LEARNING LICENSE 1.1`，需要保留并遵守现有授权限制。

### 1.3 默认工程策略

- 采用 **小步提交、可回滚、先复现后修复**。
- 抓取核心和媒体下载重构分开验证；除非依赖明确要求，不要在一个大改动里同时重写 UI、API、所有平台和存储。
- 上游变更是重要参考和优先移植来源，但也必须核查其是否依赖二改目前没有的代码、配置或环境；不能把上游代码视作无需测试的黑盒。
- 任何“全部平台已修复”“完全兼容上游”等声明都必须有可查的测试证据支持。

---

## 2. 第 0 阶段：建立安全工作区与版本地图

### 2.1 建立工作分支

先在本地工作副本执行并记录：

```bash
git status --short
git branch --show-current
git log -1 --format="%H %cs %s"
git remote -v
```

若工作区存在未提交变更，Agent 必须先记录变更文件并保护它们；不可擅自 stash、reset 或覆盖。创建专用分支，例如：

```bash
git switch -c fix/crawler-recovery-and-upstream-sync
```

若本地无 `upstream` remote，再添加；如果已有则只检查地址，不要重复添加：

```bash
git remote add upstream https://github.com/NanmiCoder/MediaCrawler.git
git fetch upstream --prune
```

然后重新获取：

```bash
git rev-parse HEAD
git rev-parse upstream/main
git merge-base HEAD upstream/main
git log --oneline --decorate -20 HEAD
git log --oneline --reverse <LAST_SYNCED_UPSTREAM_SHA>..upstream/main
```

`<LAST_SYNCED_UPSTREAM_SHA>` 必须从同步状态文件读取；第一次执行时，通过 `git merge-base` 和历史提交验证共同祖先，不得仅凭本文件中的 SHA 猜测。若共享历史与预期不同，先输出 Git 图、仓库 remote 和 merge-base 证据，再选择 merge 策略。

### 2.2 新增同步状态文件

在二改项目中新增：

`docs/upstream-sync/STATE.md`

内容至少包括：

- 上游仓库与 branch；
- 上一轮已验证并移植的上游 SHA；
- 本轮开始时上游 SHA；
- 本轮二改基线 SHA；
- 上一轮同步日期、PR/commit 地址；
- 已跳过的变更及原因；
- 未解决冲突/风险。

**只有代码移植、测试及人工审查均完成后，才能把“上一轮已同步 SHA”更新为新 SHA。** 拉取完成不等于同步完成。

### 2.3 形成本轮上游提交清单

先生成按时间正序排列的提交清单：

```bash
git log --oneline --reverse <LAST_SYNCED_UPSTREAM_SHA>..upstream/main
```

逐个检查提交说明、变更文件、diff 和相关测试。至少输出 `docs/upstream-sync/reports/YYYY-MM-DD/commit-map.md`，按以下类别归类：

| 类别 | 处理规则 |
|---|---|
| 平台抓取/解析/签名参数/分页/登录状态 | 必须映射到二改代码，并增加对应回归验证 |
| 共享基础设施/媒体下载/文件路径 | 必须同时检查调用方、配置、API/CLI、存储和平台适配器 |
| 依赖和锁文件 | 检查版本约束、兼容性、锁文件与干净环境安装 |
| 测试 | 移植上游测试或补写等价测试；不得只移植被测代码 |
| WebUI / i18n / 类型 | 保留二改已有体验，在三方差异下移植必要字段与兼容逻辑 |
| README / 文档 / 赞助与展示内容 | 不覆盖二改品牌、部署地址和产品文案；按需吸收与代码真实行为有关的内容 |
| 仅展示类变更 | 明确记录“评估过，无需移植代码”的原因，不能悄悄忽略 |

---

## 3. 第 1 阶段：先复现目标平台故障，不先大面积重构

### 3.1 确认实际目标与复现条件

Agent 应从本地配置、用户当前任务输入、运行日志和 WebUI 请求中确定真实目标平台及采集类型；如果仓库信息仍不能确定，就在执行报告中将其标记为“待用户确认”，不要武断假设目标必然是小红书。

逐项记录：

- 平台代码：`xhs / dy / ks / bili / wb / tieba / zhihu`；
- 采集类型：`search / detail / creator`；
- 输入类型：关键词、分享链接、笔记/视频 URL、内容 ID、创作者主页等；
- 登录类型：二维码、手机或 Cookie；是否确实登录成功；
- 浏览器模式：CDP 或标准 Playwright；浏览器版本；
- 运行入口：CLI、WebUI/API 或部署环境；
- 失败阶段：启动、登录、请求、解析、评论分页、数据写入、媒体下载或前端展示；
- 预期结果：至少一条明确的内容 ID、标题/正文、作者、时间、评论（如启用）及其存储位置。

日志需脱敏：删除 Cookie、token、手机号、账号隐私字段和 URL 中的敏感 query 参数；可保留状态码、平台错误码、接口路径、请求类型、重试次数及异常栈。

### 3.2 用一条受控样本分层定位

只对用户授权且可访问的数据做小规模验证：单账号、单关键词或 1–3 个指定链接、单页、低并发，优先关闭媒体下载与二级评论，先验证最小核心链路。

按以下顺序排查，每一层都必须提供证据：

1. **前端请求层**：浏览器 DevTools Network 中的 API 请求、payload、HTTP 状态和返回体；检查前端类型是否与后端 schema 一致。
2. **API 任务层**：`api/routers/crawler.py`、`api/schemas/crawler.py`、`api/services/crawler_manager.py`。核对任务字段是否被 Pydantic 接受、是否真正传给 CLI、子进程 cwd 和退出码是否正确。
3. **CLI/配置层**：`cmd_arg/arg.py` 是否注册该参数；命令行传入值是否被正确转为布尔值；`config/base_config.py` 和平台配置是否与当前调用保持一致。
4. **Crawler Factory 层**：`main.py` 中平台代码是否映射到正确 crawler；采集类型是否进入预期方法。
5. **平台 crawler 层**：`media_platform/<platform>/core.py` 是否调起搜索/详情/创作者/评论任务；异常是否被吞掉；`asyncio.gather` 是否因单条任务失败而整体丢弃结果；分页停止条件是否正确。
6. **平台 client 层**：`client.py` 中 URL、HTTP 方法、请求头、查询参数、签名/游标、响应状态分类是否与上游当前实现一致；必要时使用脱敏 fixture 建立响应契约测试。
7. **解析和模型层**：响应字段可能缺失、为 `null`、类型变化或为空时是否安全；ID 是否统一为字符串；时间戳和时区是否正确。
8. **持久化层**：`store/`、`database/`、文件输出和数据库 schema 是否接收到数据；检查事务、唯一键、重复数据和异常处理。
9. **展示层**：数据是否已落盘但未被 WebUI/API 数据接口读取；不要把“页面没有显示”误诊为平台没抓到。

在 `docs/upstream-sync/reports/YYYY-MM-DD/target-platform-diagnosis.md` 里写明：根因、证据、最小修复范围、是否可由上游提交直接解决、未确定项。没有证据时使用“疑似”而不是“已确认”。

### 3.3 故障分类与处理原则

| 现象 | 应检查 | 正确行为 |
|---|---|---|
| 登录页面打开但 API 任务失败 | Cookie/登录状态、API 子进程参数、浏览器 context | 输出明确登录状态，不将未登录误报为采集成功 |
| 搜索为空但没有异常 | 搜索接口响应、关键词、分页 token、解析器字段 | 记录原始响应分类和结果条数；禁止静默吞掉解析异常 |
| 分享链接无法解析 | 平台 URL parser、短链重定向及 URL 输入契约 | 加离线测试覆盖支持的 URL 格式；对未知格式给出可操作错误 |
| 单个内容不可用就导致全批失败 | `gather` 异常传播、异常分类、跳过策略 | 可恢复的单条错误应隔离；全局会话失效/限流则停止或退避 |
| 评论重复、漏置顶或分页不停止 | cursor/has_more/next、最大评论数边界、子评论累计 | 限制数量真实生效，停止条件可测且不会无限循环 |
| 任务成功但数据为空 | `store` 回调、字段映射、DB 事务、导出路径 | 必须区分抓到 0 条、解析失败和写入失败 |
| 媒体失败影响主抓取 | 下载器与 crawler 的错误边界 | 媒体失败应单独记录，不能抹掉已成功采集的结构化数据 |
| 出现验证码/封禁/权限错误 | 平台响应、当前登录态与访问授权 | 停止不合理重试，输出清晰原因；不尝试绕过访问控制 |

---

## 4. 第 2 阶段：共享架构与文件迁移映射

### 4.1 核心数据流应保持可追踪

```text
WebUI
  -> api/schemas/crawler.py (请求字段/校验)
  -> api/routers/crawler.py
  -> api/services/crawler_manager.py (构造子进程 CLI)
  -> cmd_arg/arg.py (解析参数)
  -> config/base_config.py + config/<platform>_config.py
  -> main.py / CrawlerFactory
  -> media_platform/<platform>/core.py
  -> media_platform/<platform>/client.py
  -> 响应解析/字段规范化
  -> store/<platform>/ + database/
  -> API 数据路由 / 文件导出 / WebUI 展示
```

媒体下载（启用时）应作为独立支路：

```text
platform core
  -> media_platform/<platform>/media.py (解析平台媒体地址/类型)
  -> media_downloader/ (流式传输、有限重试、文件校验、路径安全、可选 ffmpeg)
  -> {SAVE_DATA_PATH 或 data}/{platform}/media/{content_id}/
```

每次迁移都要核对箭头两端的接口，禁止只把某个目录复制过来。

### 4.2 已确认上游迁移映射表

| 功能域 | 上游当前实现/变更 | 二改必须完成的工作 |
|---|---|---|
| 共享 crawler 基类 | `base/base_crawler.py` 移除旧 `AbstractStoreImage/AbstractStoreVideo` 接口 | 搜索所有继承、导入和调用点；若移植统一媒体下载器，必须原子移除旧接口依赖 |
| 小红书 | `media_platform/xhs/{client,core,exception,playwright_sign}.py` 有更新；增加 `media_platform/xhs/media.py` | 移植平台访问错误分类、重试和评论边界修复；检查签名依赖；媒体功能转向新 adapter，不保留双套媒体 GET 逻辑 |
| 抖音 | `media_platform/douyin/{client,core}.py` 有请求参数/头部修复；新增 `media.py` | 重点核对详情接口 `uifid/verifyFp`、上游 `x-tt-argus` 请求头修复及对应测试；不要自行发明上游未支持的绕过逻辑 |
| 快手 | `client.py/core.py/help.py` 更新；新增 URL/不可用视频测试与 `media.py` | 移植签名 REST 请求、分享短链 `/f/<token>` 解析、`photo is null` 安全处理、限流退避与重新生成签名；避免重试时复用过期签名 |
| 哔哩哔哩 | `client.py/core.py/login.py` 更新；新增评论、登录态测试和 `media.py` | 真实验证 Cookie 是否有效，避免只根据页面选择器判断登录；检查置顶评论和评论数量上限；核对 DASH/直链降级与画质逻辑 |
| 微博 | `core.py` 更新；新增 `media.py`；`tools/time_util.py` 时区修复 | 验证 RFC2822 时间戳按时区偏移转换，`create_time` 与 `create_date_time` 表示同一时刻 |
| 贴吧 / 知乎 | 当前上游媒体下载功能说明不支持这两个平台 | 不为支持媒体下载而虚构媒体字段；保留原有结构化采集测试 |
| CLI 配置 | `cmd_arg/arg.py` 新增 `--get_media`；`config/base_config.py` 将旧拼写改为 `ENABLE_GET_MEDIA` | 统一参数名、布尔值、默认值与帮助信息；查找旧 `ENABLE_GET_MEIDAS` 引用并完成兼容/迁移 |
| API contract | `api/schemas/crawler.py` 新增 `enable_media`；`api/services/crawler_manager.py` 将其转为 `--get_media` | 二改已有媒体 checkbox 必须通过 schema、manager、CLI 直到 config 真正生效；测试 API payload 到命令行的端到端字段映射 |
| 统一媒体下载器 | 新增 `media_downloader/{downloader,ffmpeg,paths,types}.py` | 整体迁移并使用上游测试覆盖；检查路径穿越、临时文件、断点续传、Content-Range/长度校验、扩展名白名单、超时和有限重试 |
| 存储层 | 移除 `store/{xhs,douyin,bilibili,weibo}/*_store_media.py` 旧媒体实现 | 只有在所有平台 adapter 已接入并通过测试后才能删除旧代码；保留数据文件路径兼容或提供迁移说明 |
| 依赖 | `pyproject.toml`、`requirements.txt`、`uv.lock` 随上游变化 | 统一依赖声明与锁文件；在干净环境进行同步安装，不允许只改一个依赖文件 |
| 测试 | 上游新增多个 unit/contract/integration 测试 | 必须迁移或补写测试；不要以暂时跳过测试、放宽断言或删除测试来通过 CI |
| WebUI | `CrawlerConfigPanel.tsx`、crawler store/types、API、i18n 配置字段变化 | 保留二改布局和登录指引，移植功能字段并补齐中英文文案、类型与错误提示；不可整文件覆盖二改组件 |

---

## 5. 第 3 阶段：上游重点提交的移植与验证清单

执行时应重新读这些提交的完整 diff，并以本轮实际 upstream history 为准。以下清单用于优先级排序，不替代提交清单，也不表示这些提交已在二改中完成。

| 上游提交（短 SHA） | 主要内容 | 二改验证重点 |
|---|---|---|
| `17f66121e0fc` | 升级 `xhshow` 至 `0.2.0`，移除 GET 签名 monkey patch | `pyproject.toml` / `uv.lock` / `requirements.txt` 一致；小红书请求签名回归；无 monkey patch 依赖遗漏 |
| `04631ba8e451` | 修复微博 RFC2822 时间戳时区转换 | `astimezone(timezone.utc)` 语义；新加的两条时间测试；跨日数据不偏移 |
| `2e558f135264` | 快手网页端 REST 列表/搜索请求签名适配 | 签名生成、请求参数序列化、错误码分类、空列表翻页终止、URL parser |
| `071c8c0acaec` | 快手限流退避重试与请求间隔抖动 | retry 次数有上限、每次请求重新签名、普通错误不被误认为限流、测试不依赖真实长延时 |
| `17c6d386b8bc` | 修复 B 站置顶评论缺失和最大评论数/子评论循环边界 | 第一页置顶评论只加入一次；`max_count` 到达后确实停止；开启子评论不导致无限循环 |
| `d594c20c13f46c368bfec133de3a4f1a97cd4d79` | 小红书/B 站访问限制与评论采集边界问题 | 区分平台访问错误和可重试错误；批量任务单条失败不击穿整个批次；评论上限行为可测 |
| `0ca7b29cf075` | 新增统一媒体下载器，覆盖 xhs/dy/ks/bili/wb | 同步 `media_downloader/`、五个 `media.py`、配置/API/CLI/WebUI、测试；检查路径安全和失败隔离 |
| `c03ab60aac59` | B 站登录状态改为校验 Cookie 有效性，避免静默降级到低画质 | 登录/未登录/过期 Cookie 的独立测试；不可仅凭 UI 元素宣告登录成功 |
| `9cfc1485774b` | 适配 B 站首页新版登录入口选择器 | selector 失败时的可诊断输出；不能使 Cookie 有效性检查退化为仅检查选择器 |
| `eec25bb0a027` | 修复小红书视频只下载封面，适配 `EF*` 清晰度档位 | 解析视频源 URL/分档的 fixture 测试；确认下载的是媒体本体而非仅封面 |
| `1e1ae64cb424` | 快手视频不可用时 `photo=null` 导致整轮崩溃 | `null`、缺字段、不可用视频三种响应测试；单条不可用不丢失同批有效数据 |
| `c7e6c9fdc097` | 支持快手 `/f/<token>` 分享短链形式 | 所有 README 声明支持的输入形式都有 URL parser 单测 |
| `cf513e70a13a` | 补上抖音 detail 请求所需 `uifid/verifyFp` 参数 | detail 请求参数 fixture；搜索和详情使用各自正确的请求上下文 |
| `380b426000aa` | 补充抖音 `x-tt-argus` 请求头 | 测试明确验证请求头组装；不把敏感完整 token 写进测试日志 |
| `8ecfa31de22c` | 快手示例配置改用分享短链并说明输入形式 | 示例、帮助信息和 parser 行为一致 |

上游近期新增的测试文件还应逐项检查并移植/等价重建：

- `tests/test_xhs_core_access_error.py`
- `tests/test_xhs_raw_response_errors.py`
- `tests/test_douyin_argus_header.py`
- `tests/test_douyin_aweme_detail_params.py`
- `tests/test_kuaishou_unavailable_video.py`
- `tests/test_kuaishou_url_parse.py`
- `tests/test_bilibili_client_comments.py`
- `tests/test_bilibili_login_state.py`
- `tests/test_cmd_arg_media.py`
- `tests/test_media_downloader.py`
- `tests/test_media_extractors.py`
- `tests/test_media_ffmpeg.py`
- `tests/test_media_core_integration.py`
- `tests/test_media_e2e.py`

如果上游测试不适用于二改自己的接口或测试环境，允许等价改写，但必须在报告中说明“为什么不能直接移植、替代测试覆盖何种行为”，不允许直接删除。

---

## 6. 第 4 阶段：实际移植顺序

### Phase A — 修复当前目标平台采集

1. 将故障复现缩到最小样本并存档脱敏日志。
2. 找到该平台对应的上游修复提交和 diff。
3. 优先以最小改动移植请求参数、响应解析、错误分类、分页或登录态修复。
4. 为根因增加离线单测；能用脱敏响应 fixture 的，不用真实平台网络做常规单测。
5. 对同平台的 `search/detail/creator` 及评论路径执行回归，防止一个路径修好、另一个路径仍旧失败。
6. 先确认结构化数据可以稳定写入本地存储，再进入媒体下载与 UI 增强阶段。

**Phase A 结束标准：** 指定目标平台、指定采集类型至少有一条受控成功样本，能核对返回内容 ID，并确认记录已持久化；失败类别可区分，测试可重复执行。

### Phase B — 同步平台级上游修复

按提交时间正序处理上游提交，避免跳过先决依赖。对每个提交记录：

- 原始上游 SHA 与标题；
- 变更文件和目的；
- 二改对应文件；
- 直接移植/适配/不移植的理由；
- 新增/更新测试；
- 执行的命令与结果；
- 剩余风险。

优先完成抓取可靠性问题，再做文档、展示或媒体下载等非核心分支。对上游多提交共同构成一个功能的情况（例如快手签名接口与限流重试），可以作为一个逻辑 PR 一起验证，但必须保留原提交 SHA 的映射记录。

### Phase C — 整体迁移媒体下载架构（原子迁移）

媒体下载重构牵涉共享层、平台 adapter、CLI、配置、API 和 WebUI。按此顺序迁移：

1. 读取上游 `media_downloader/types.py`、`paths.py`、`downloader.py`、`ffmpeg.py` 的接口和测试，先弄清类型、失败类别、路径规则、续传协议和合流行为。
2. 新增共享下载器与其纯函数/单元测试；测试路径穿越保护、非法扩展名、临时文件处理、URL 变更时临时片段失效、HTTP 206 的 `Content-Range` 语义、长度校验、超时和有限重试。
3. 逐个平台迁移 `media_platform/<platform>/media.py`，只让该层决定“下载什么媒体 URL”；共享下载器只负责“安全可靠地写入字节”。不把平台解析逻辑复制到下载器。
4. 将 `config.ENABLE_GET_MEIDAS` 迁移到 `config.ENABLE_GET_MEDIA`，全仓搜索旧标识符并决定是否保留一个短期兼容 alias；兼容 alias 不能造成两个配置值不一致。
5. 将 CLI `--get_media`、API schema `enable_media`、manager 命令构建、WebUI 类型/store/component/i18n 全部连通。
6. 保留旧媒体存储代码作为迁移期兼容时，必须有明确的唯一调用路径，禁止同一帖子经两套实现重复下载；只有全链路测试通过后，才删除旧 `*_store_media.py` 和旧抽象接口。
7. B 站合流依赖 `ffmpeg` 时必须可检测、可选、可诊断。缺少 ffmpeg 应按上游设计降级或报告，不可隐式安装。
8. 媒体下载失败必须与结构化内容采集失败分离；任何失败都不得丢失已成功存储的数据。

**Phase C 结束标准：** CLI、API 和 WebUI 使用同一默认值；启用/关闭开关的测试明确通过；五个支持平台的媒体 adapter 至少通过离线 extractor 测试；下载器、路径安全和可选 ffmpeg 测试通过；贴吧/知乎不会被错误宣称支持媒体下载。

### Phase D — 三方合并并保护二改 UI/部署

在临时分支合并 `upstream/main`，通过真实三方冲突解决，而不是整文件覆盖。需重点检查：

- `webui/src/components/config/CrawlerConfigPanel.tsx`（二改显著扩展，禁止覆盖）；
- `webui/src/App.tsx`、`Sidebar.tsx`、`Terminal.tsx`、`DataExplorer.tsx`、`FileCard.tsx`；
- `webui/src/hooks/useCrawler.ts`、`useWebSocket.ts`；
- `webui/src/lib/api.ts`、`webui/src/store/crawlerStore.ts`、`webui/src/types/crawler.ts`；
- `webui/src/i18n/locales/{zh-CN,en-US}/`；
- `webui/vite.config.ts`、`index.html`、GitHub Pages workflow 与路径前缀；
- `Dockerfile`、`.dockerignore`、`railway.json`、`RAILWAY_DEPLOY.md`；
- `README.md`、`README_en.md`、`README_es.md` 与 VitePress 文档路径。

合并原则：

- **保留二改的产品体验与部署差异**，只移植上游针对新 API 参数、字段、行为或修复的必要代码。
- 文案中平台支持能力与实际实现必须一致，不能将上游媒体支持说明未经核查地复制到二改文档。
- 处理 `webui` 路径和静态托管 base path 时，分别验证 GitHub Pages 与 FastAPI 本地静态服务，不以单一部署环境成功代表全都正常。
- 复核历史中的宽松 CORS 逻辑；如必须允许跨域，应配置明确允许的来源并核查凭证/认证策略，不要将 CORS 当作认证机制。
- 对数据库模型、字段类型、唯一键或存储布局变更，先提供迁移兼容方案与回滚方案，不可在没有备份的情况下删除或重建用户数据。

### Phase E — 依赖锁定、静态检查和打包验证

至少执行：

```bash
uv sync --locked
uv run pytest tests/ -q
uv run pytest test/ -q
uv run python main.py --help
```

如果项目当前测试目录/命令存在差异，先核对 `pyproject.toml` 和 `CLAUDE.md`，调整命令并记录依据，不要静默跳过某个测试目录。

按项目现有工具执行 lint、类型检查和前端构建，例如：

```bash
uv run pre-commit run --all-files
cd webui && npm ci && npm run build
```

如命令未定义，先检查 `pyproject.toml`、`package.json` 与 CI workflow，禁止凭空假设某个 script 存在。所有依赖声明修改后需检查 `uv.lock` 与 npm lockfile；不得只改 `requirements.txt` 或 `package.json`。

### Phase F — 审查并生成交付报告

在以下目录留下本轮证据：

```text
docs/upstream-sync/
├── STATE.md
└── reports/
    └── YYYY-MM-DD/
        ├── commit-map.md
        ├── target-platform-diagnosis.md
        ├── conflict-resolution.md
        ├── test-report.md
        └── release-notes.md
```

交付报告必须逐条说明本轮哪些上游变更已移植、哪些已被二改实现等价覆盖、哪些被有意延后以及理由；明确列出未通过测试。**不能把未执行的验证写成通过。**

---

## 7. 测试设计与验收标准

### 7.1 四层测试体系

**A. 单元测试（不访问真实平台）**

- URL parser：正常链接、分享短链、尾部 query、非法 URL、空输入；
- 响应解析：字段缺失、`null`、空数组、未知枚举、类型变化；
- 请求构造：平台特定参数、必要请求头、查询字段序列化；
- 分页：`has_more`、`cursor`、`next`、空页、重复 ID、最大数量边界；
- 错误分类：登录失效、访问限制、内容不可用、可重试网络错误、不可重试业务错误；
- 时区：`+0800` 等输入对应正确 UTC timestamp；
- 媒体路径/下载器：扩展名白名单、路径穿越、临时文件、Range/206、完整性校验、重试上限、超时和取消。

**B. API/CLI contract 测试（不访问真实平台）**

- 对 `CrawlerStartRequest` 提交 `enable_media`，确认 schema 接收；
- 调用 `CrawlerManager._build_command()`，断言生成 `--get_media true/false`；
- CLI 解析 `--get_media` 为 bool，默认值与配置一致；
- WebUI `crawler` TypeScript 类型、请求 payload、API schema 和 manager 参数名称完全一致；
- `--help` 正确展示平台与参数；
- 子进程启动目录、停止、退出码、日志读取和异常状态不会被上游合并破坏。

**C. 持久化/集成测试（优先使用 mock 和临时目录）**

- 解析结果进入正确 platform store/model；
- DB 或文件写入失败有明确错误，不报告成功；
- 重复采集具备预期幂等性；
- 单条不可用记录不会导致同批有效数据丢失；
- 媒体下载失败不回滚已经存储的结构化内容；
- WebUI 数据浏览 API 能读取保存的结果。

**D. 受控真实平台烟雾测试（仅手动/按需触发）**

- 单并发；单页；1–3 条明确可访问内容；限制评论数；默认关闭媒体；
- 验证登录状态、请求成功、正确内容 ID、关键字段解析和持久化；
- 目标平台通过后，再逐步启用评论和媒体；
- 遇到平台访问限制、账号安全校验或权限错误时应停止，而不是继续放大流量。

真实平台烟雾测试不应作为每次 CI 的默认任务，不得将真实账号 Cookie 放进 GitHub Secrets 后让 PR 自动反复爬取。

### 7.2 平台验证矩阵

针对二改声明支持的七个平台，按其实际支持的采集能力做矩阵；媒体下载只要求上游明确支持的五个平台（`xhs/dy/ks/bili/wb`）。

| 平台 | search | detail/指定 URL | creator | 评论分页/上限 | 媒体下载 | 最低验收要求 |
|---|---|---|---|---|---|---|
| 小红书 `xhs` | 按平台能力验证 | 验证分享链接与内容 ID | 验证主页和作品列表 | 第一层/二级评论开关与上限 | 是 | 访问错误分类、原始响应解析、媒体 EF* 格式 |
| 抖音 `dy` | 验证 | 验证 detail 请求上下文 | 验证 | 按当前能力验证 | 是 | detail 参数、必要请求头、URL 解析 |
| 快手 `ks` | 验证签名 REST 搜索 | 分享短链/指定视频 | 作品列表分页 | 空页/不可用作品/限流 | 是 | `/f/<token>`、空 `photo`、有限退避与重签名 |
| 哔哩哔哩 `bili` | 验证 | 视频链接/ID | 验证 | 置顶评论、评论上限、子评论 | 是 | Cookie 有效性、画质降级、评论边界 |
| 微博 `wb` | 验证 | 指定帖子 | 验证 | 按当前能力验证 | 是 | 时间戳与本地时区一致 |
| 贴吧 `tieba` | 验证 | 按当前能力验证 | 按当前能力验证 | 按当前能力验证 | 否（当前上游媒体下载不支持） | 正确存储结构化结果，不宣称媒体支持 |
| 知乎 `zhihu` | 验证 | 按当前能力验证 | 按当前能力验证 | 按当前能力验证 | 否（当前上游媒体下载不支持） | 正确存储结构化结果，不宣称媒体支持 |

矩阵中任一平台未真实执行时，应标记“未验证”，不要用单测通过替代真实平台兼容性证明。

### 7.3 发布前验收门槛

只有满足以下条件才允许标记本轮同步完成：

- [ ] 目标平台的故障已复现、根因有证据、最小回归测试存在；
- [ ] 目标平台受控烟雾测试返回预期 ID，且确认写入目标存储；
- [ ] 所有本轮上游提交均在 `commit-map.md` 中被分类，无未解释遗漏；
- [ ] 上游生产代码变化都由测试覆盖或有明确的延期原因；
- [ ] API schema / manager / CLI / config / WebUI 字段契约通过测试；
- [ ] 旧媒体实现与新媒体下载器没有双重调用或重复写入；
- [ ] `uv.lock`、Python 依赖、前端 lockfile 和构建输出一致；
- [ ] 项目现有测试、静态检查、前端构建均通过；
- [ ] WebUI 自定义功能、部署 base path、后端静态服务及停止任务流程通过回归；
- [ ] 没有意外删除用户数据、许可证、署名、部署文件或测试；
- [ ] 状态文件和报告已更新，明确写出未验证平台与剩余风险。

---

## 8. 后续“每次上游提交都同步”的长期机制

### 8.1 规定每轮同步入口

每次开始时都从状态文件读取 `LAST_SYNCED_UPSTREAM_SHA`，之后执行：

1. `git fetch upstream --prune`；
2. 获取 `upstream/main` 当前 HEAD；
3. 列出上一同步点至当前 HEAD 的**全部**提交，按正序分类；
4. 阅读涉及代码、测试、依赖、文档的 diff；
5. 创建 `sync/upstream-<日期>-<短SHA>` 分支；
6. 对共享历史正常的仓库，优先在临时分支做一次三方 merge 来保留上游历史，按路径/契约解决冲突；若确实不适合 merge，再逐条说明原因并使用受控 cherry-pick；
7. 先测试核心抓取，再测试媒体/API/WebUI/部署；
8. 生成 PR 与同步报告，人工审查通过后才更新状态文件。

不能简单只同步最近一个 commit。多个上游提交可能相互依赖，遗漏其中的依赖提交会让最终代码看似更新却无法运行。

### 8.2 推荐的自动化层级

**第一层：自动提醒/变更检测（低风险，建议先做）**

新增 GitHub Actions 定时 workflow，每天检查 `upstream/main` 是否比 `STATE.md` 中已验证的 SHA 更新；如果有更新，生成包含新 SHA、提交列表和变更文件的 Issue/Artifact 或同步 PR 草案。此 workflow 不运行真实平台抓取，不自动合并。

**第二层：自动创建同步分支/PR（需先验证）**

待本地 merge 流程稳定后，再让 workflow 自动创建/更新 `sync/upstream-*` PR。要求：

- 只推送自动化分支，不修改 `main`；
- 不自动 merge；
- 运行离线单测和构建；
- PR 描述列出全部上游 commit SHA、冲突文件和测试结果；
- `STATE.md` 的已验证 SHA 只能由人工审批后的合并提交更新；
- workflow 权限最小化，不向 CI 暴露账号 Cookie、代理密钥或 `.env`。

**第三层：AI Agent 执行移植与诊断（人审后合并）**

Agent 读取 PR 上的变更映射，按本文阶段执行代码适配、补测、前端契约和部署回归，提交可审查的具体修改。禁止设计为“检测到新提交就自动覆盖、自动部署、自动发布”的无人工流程。

### 8.3 每轮必须保留的审计记录

- 上游起点 SHA 与终点 SHA；
- 二改合并前后 SHA；
- 新增/修改/删除文件清单；
- 每个上游提交的迁移决定及理由；
- 冲突解决记录；
- 测试命令、退出码、关键摘要；
- 哪些平台实际经过在线烟雾测试，哪些只通过离线测试；
- 未同步内容、待验证问题和回滚 commit。

### 8.4 单独维护上游未合并 PR 的候选队列

`upstream/main` 的提交历史只代表已经进入上游主分支的内容。**未合并的 PR 不是正式主分支同步的一部分**，但它们可能恰好修复二改当前遇到的问题。因此每轮可另行检查 <https://github.com/NanmiCoder/MediaCrawler/pulls>，生成 `open-pr-triage.md`，不要把它们混入“已跟随上游 main”的状态。

截至本方案核查时，上游 PR 列表中存在过以下类型的候选改进；运行任务时必须重新确认 PR 仍然开放、head SHA 与 diff 仍有效：

| 候选 PR | 议题 | 处理方式 |
|---|---|---|
| [#989](https://github.com/NanmiCoder/MediaCrawler/pull/989) | 小红书 `INITIAL_STATE` 解析健壮性、抖音数量上限 | 若目标平台相关，评估其测试与实现；不要直接复制未审查补丁 |
| [#979](https://github.com/NanmiCoder/MediaCrawler/pull/979) | 抖音 `START_PAGE > 1` 时关键词搜索返回空列表 | 目标为抖音且使用起始页参数时优先复现 |
| [#978](https://github.com/NanmiCoder/MediaCrawler/pull/978) / [#977](https://github.com/NanmiCoder/MediaCrawler/pull/977) | 微博 detail URL 输入与翻页到底时的崩溃 | 目标为微博时检查；按输入类型分别补测试 |
| [#975](https://github.com/NanmiCoder/MediaCrawler/pull/975) | 避免 Cookie 进入子进程 argv，并按上下文脱敏日志 | **安全优先评估**；检查进程列表、异常、API 日志及 WebSocket 日志是否会泄露 Cookie |
| [#974](https://github.com/NanmiCoder/MediaCrawler/pull/974) | HTTP 与 WebSocket 采用统一访问边界 | 公开部署 WebUI/API 前必须独立进行认证/授权审查 |
| [#971](https://github.com/NanmiCoder/MediaCrawler/pull/971) / [#970](https://github.com/NanmiCoder/MediaCrawler/pull/970) | 并发/失败写入的数据保全、MongoDB upsert 错误传播 | 检查文件和数据库写入失败是否被误报成功或导致数据丢失 |
| [#972](https://github.com/NanmiCoder/MediaCrawler/pull/972) / [#973](https://github.com/NanmiCoder/MediaCrawler/pull/973) | 表格公式注入、稳定的 CSV/Excel 表头 | 评估导出数据安全和兼容性 |
| [#967](https://github.com/NanmiCoder/MediaCrawler/pull/967) | Redis 缓存避免不安全的 pickle 反序列化 | 如果启用 Redis cache，优先做安全审查 |
| [#963](https://github.com/NanmiCoder/MediaCrawler/pull/963) | 新增 `--check_session` 会话预检 | 可作为抓取前健康检查候选；验证与二改 CLI/WebUI 的契约 |
| [#982](https://github.com/NanmiCoder/MediaCrawler/pull/982) | Ctrl+C 应停止抓取，而非被重试机制吞掉 | 验证取消信号、async task cleanup 和媒体下载取消行为 |

这些 PR 的**当前状态及具体代码必须在执行时重新核验**。如确实需要某个未合并修复，应新建独立分支/PR，注明“提前采用上游未合并 PR”，记录原 PR URL 和 head SHA，并为二改补测试；不要把它记为已同步 `upstream/main`。安全相关 PR 即使与目标平台无关，也应做风险评估，但不得绕过审查直接自动合并。

---

## 9. 回滚与异常处理

- 所有移植工作均在独立分支完成；合并前创建带标签或可定位的基线 commit。
- 如果目标平台出现新的 P0/P1 回归，优先 revert 本轮同步/修复 commit，不要在生产分支直接手工删改一堆文件。
- DB schema、唯一键、输出目录或媒体路径发生不兼容变化时，先备份或制作迁移脚本，并验证从旧版本升级与回滚两条路径。
- 如果上游变更无法与二改自定义代码同时保留，必须输出至少两种可行方案、各自影响和选择理由；禁止静默舍弃任何一边。
- 如果由于账号未登录、平台权限、网络或平台策略原因无法在线验证，报告应标记阻塞原因，并提供离线测试证据；不得声称该平台已经恢复。

---

## 10. 给 AI Agent 的总控执行提示词

以下可直接复制给 Codex / Claude Code。Agent 应先阅读本文件，再开始操作。

> 你是负责维护 WeMediaCrawler 的资深 Python/Playwright/React 工程师。请把 `docs/implementation/WeMediaCrawler_上游同步与抓取恢复实施方案.md`（或本文件的本地实际路径）作为项目级执行约束，完成“先修复目标平台抓取链路，再系统移植上游差异并建立持续同步机制”的任务。
>
> **执行顺序不可跳过：**
>
> 1. 先检查 `git status`、当前分支、HEAD、remote 和现有未提交改动；创建专用分支，绝不直接改 `main`。检查并阅读 `LICENSE`、`CLAUDE.md`、项目配置、测试和 CI。
> 2. 重新读取 `NanmiCoder/MediaCrawler` 与 `Aswellle/WeMediaCrawler` 的最新 HEAD；确认 merge-base，生成所有未同步 upstream commits 的正序清单。不得把本文件中的历史 SHA 当作实时状态。
> 3. 从本地配置、WebUI 请求和脱敏日志确定真实目标平台/采集类型。按文档的逐层数据流定位失败点；先给出有证据的诊断记录，然后只修复最小根因，并补回归测试。不能将启动成功、无异常退出或 0 条结果当成成功。
> 4. 按上游提交逐条审查 diff 和关联测试。优先移植平台采集可靠性修复，随后处理媒体下载器、配置/API/CLI/WebUI 契约和依赖；必要时按逻辑功能分组，但保留每个 commit SHA 的映射。不允许盲目覆盖整个上游目录。
> 5. 保留二改的 React WebUI、品牌、GitHub Pages、Railway/Docker 等自定义内容；对同路径冲突执行三方合并，逐个核对语义。特别检查 `CrawlerConfigPanel.tsx` 中 `enable_media` 与后端 schema/manager/CLI/config 是否贯通，以及历史宽松 CORS 逻辑的安全性。
> 6. 媒体下载必须按“共享 downloader + 平台 media adapter + CLI/config + API + WebUI + 测试”的完整链路原子迁移；避免旧 `*_store_media.py` 与新下载器并存造成重复调用。检查 `ENABLE_GET_MEIDAS` 旧拼写并提供安全兼容方案。
> 7. 执行离线单测、contract 测试、项目测试、依赖锁定检查、lint/type check 与前端构建；目标平台在线烟雾测试只使用用户授权的少量内容、低并发并手动触发。访问限制或验证码不能通过无限重试处理。
> 8. 生成 `docs/upstream-sync/STATE.md` 和 `docs/upstream-sync/reports/YYYY-MM-DD/` 下的提交映射、诊断、冲突、测试与 release 报告。每项测试必须写真实结果；未执行不得写通过。列出已验证和未验证的平台。
> 9. 最终报告提供变更摘要、关键文件、根因证据、upstream commit 对照表、运行命令/测试结果、遗留风险、回滚点，以及后续每次同步的操作方式。只有所有门槛满足后，才建议合并 PR；不要擅自推送、部署或自动合并。
>
> **质量要求：** 少量、明确、可回滚的修改优先；保留完整源文件与测试的正常可读性；禁止为通过 CI 删除测试或削弱断言；不能确认的内容明确标记为未知。最终目标是建立长期可靠的同步机制，而不是只把版本号改新。

---

## 11. 参考链接

### 仓库

- 上游：<https://github.com/NanmiCoder/MediaCrawler>
- 二改：<https://github.com/Aswellle/WeMediaCrawler>
- 上游 2026-09 媒体下载重构：<https://github.com/NanmiCoder/MediaCrawler/commit/0ca7b29cf0753076ff7488e6f03cef4f2f82aa0f>
- 上游抖音请求头修复：<https://github.com/NanmiCoder/MediaCrawler/commit/380b426000aac3d612837ed72c99808347dc94c9>
- 上游快手分享短链：<https://github.com/NanmiCoder/MediaCrawler/commit/c7e6c9fdc09748718e8ebc67502c385f300719fb>
- 上游快手不可用视频修复：<https://github.com/NanmiCoder/MediaCrawler/commit/1e1ae64cb4242f5afdb2dbc35b5da931ae6497a0>
- 上游小红书媒体质量档位修复：<https://github.com/NanmiCoder/MediaCrawler/commit/eec25bb0a0276464a539415339bfa69643c6348e>
- 上游 B 站登录态修复：<https://github.com/NanmiCoder/MediaCrawler/commit/c03ab60aac595ccc0c1a3984c69608dc59025196>
- 上游微博时间戳修复：<https://github.com/NanmiCoder/MediaCrawler/commit/04631ba8e4511029d7f7add04afd6f6954fdb372>

---

**完成定义：** 不是“代码跟上游看起来相似”，而是目标平台故障已经有证据地修复，所有 upstream 变更均有迁移结论，二改独有产品功能仍在，测试与构建实际通过，下一次同步可以按同一规范重新执行。

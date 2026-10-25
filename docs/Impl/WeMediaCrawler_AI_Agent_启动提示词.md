# WeMediaCrawler AI Agent 启动提示词

请先阅读并严格遵循docs/Impl/WeMediaCrawler_上游同步与抓取恢复实施方案.md。不要直接在 `main` 分支操作，也不要先做大面积合并。

你的首要任务是**诊断并恢复当前实际目标平台的结构化数据采集**，随后把 `NanmiCoder/MediaCrawler` 上游缺失的功能、bug 修复、依赖和测试系统性移植到 `Aswellle/WeMediaCrawler`，同时保留二改的 WebUI/UX、品牌、GitHub Pages、Railway/Docker 和部署适配。

## 必须按序执行

1. 检查工作区改动、HEAD、分支、remote、许可证、`CLAUDE.md`、项目配置与测试；创建独立工作分支。
2. 重新 fetch 上游和二改仓库，确认 merge-base，列出全部尚未同步的 upstream commit（按正序），不能依赖旧的 SHA 快照。
3. 根据配置、真实任务输入及脱敏日志确定目标平台和采集类型；检查 WebUI → API schema → crawler manager → CLI → config → factory → platform core/client → parser/store/DB 的完整链路。先写诊断报告，说明根因与证据。
4. 先修复目标平台的最小根因并加入离线回归测试。不要仅凭“进程退出成功”认定爬取成功；至少验证预期内容 ID、关键字段和持久化结果。
5. 逐个审阅上游提交的 diff 与测试，分类为平台抓取、请求契约、评论/分页、依赖、媒体下载、API/CLI/WebUI、文档或展示。记录每个 commit SHA 对应的二改文件、移植方法、测试和决定。
6. 重点核对二改前端 `enable_media` 与 API schema / `CrawlerManager._build_command()` / `--get_media` / `ENABLE_GET_MEDIA` 是否贯通；把统一媒体下载器视为一个跨模块的原子迁移，禁止混用新旧媒体路径。
7. 使用三方合并保留二改自定义 UI 和部署文件；特别审查 `CrawlerConfigPanel.tsx`、WebUI types/store/i18n、GitHub Pages base path、Railway/Docker 配置和 CORS 安全策略。不得用整个上游目录覆盖二改。
8. 运行项目测试、相关新增测试、API/CLI contract 测试、静态检查、锁文件检查和前端构建。真实平台只做低频、单并发、少量用户授权样本的手动烟雾测试；访问受限时停止，不通过无限重试规避平台控制。
9. 输出以下文件：
   - `docs/upstream-sync/STATE.md`
   - `docs/upstream-sync/reports/YYYY-MM-DD/commit-map.md`
   - `docs/upstream-sync/reports/YYYY-MM-DD/target-platform-diagnosis.md`
   - `docs/upstream-sync/reports/YYYY-MM-DD/conflict-resolution.md`
   - `docs/upstream-sync/reports/YYYY-MM-DD/test-report.md`
   - `docs/upstream-sync/reports/YYYY-MM-DD/release-notes.md`
10. 最终报告必须明确列出改了哪些文件、根因证据、移植了哪些上游 SHA、哪些变更有意延后及理由、真实测试结果、尚未验证的平台、遗留风险和回滚点。未执行的测试不得写成通过。只有门槛满足后才建议合并 PR；不得擅自 push、部署或自动 merge。

## 关键质量约束

- 先诊断、再修改、后验证；优先小改动和可回滚提交。
- 不删除测试、不弱化断言、不静默吞异常来制造绿色 CI。
- 不覆盖二改的 WebUI/UX、品牌与部署能力。
- 不输出 Cookie、token、账号隐私或 `.env` 内容。
- 不把登录验证、验证码、访问限制当作无限重试问题。
- 不假定上游所有改动能无冲突直接使用；不确定时明确标记，并给出可验证的方案。

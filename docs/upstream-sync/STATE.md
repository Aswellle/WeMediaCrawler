# Upstream Sync State（上游同步状态）

> 本文件是每轮上游同步的唯一入口状态。每次开始同步前先读本文件，结束后由人工审查通过的合并提交更新"已同步 SHA"。
> 详细规则见 `docs/Impl/WeMediaCrawler_上游同步与抓取恢复实施方案.md`。

## 当前状态

| 字段 | 值 |
|---|---|
| 上游仓库 / 分支 | `https://github.com/NanmiCoder/MediaCrawler` / `main` |
| 上一轮已验证并移植的上游 SHA | `8f583999006d5b692272c608440e193ca282e73b`（2026-10-15 update README） |
| 本轮二改基线 SHA | `22fbcc6013d4a55ff48ab01746688e3b8651c6e5`（origin/main，2026-10-02 Encourage users to star the project） |
| 真实共同祖先（merge-base） | `076dcba978b1`（2026-07-01 fix: 修复 WebUI 源码缺失、环境检测路径及文档说明） |
| 本轮同步日期 | 2026-10-25 |
| 本轮工作分支 | `fix/crawler-recovery-and-upstream-sync` |
| 本轮合并提交 | `2576d018`（Merge upstream … into WeMediaCrawler），其后修复提交 `672a98c2`、`fcf387ce`、`eb5f1d8a` |
| PR / 发布状态 | **未创建 PR、未 push、未发布** —— 等待人工审查（见 reports/2026-10-25/） |

## 本轮说明（重要）

1. **上游历史曾被重写。** 二改 main 中含 3 个上游已从 main 线性历史中丢弃的提交
   （`04da7f3b`、`84907f07`、`3bde9e20`，均为 2026-07-10 前后的 README/赞助商文档），
   因此本地缓存的 `refs/remotes/upstream/main`（3bde9e20）**不是**当前上游 main 的祖先。
   本轮以 GitHub Compare API 确认真实基线为 `076dcba978b1`，上游侧净新增 **38 个提交**。
2. **上游对象通过"逐提交补丁重建"获得。** 本机网络对 GitHub 的 git 传输（smart HTTP pack）
   持续被掐断，无法直接 `git fetch upstream`。改用 GitHub REST API 逐提交下载 diff 并以
   `git am`（保留作者/日期/说明）重建为分支 `upstream-recon2`，重建结果用上游 Git Trees API
   返回的 blob SHA 全量比对：除 3 张赞助商/示例图片外**逐字节一致**（图片差异经用户确认豁免）。
   `upstream-recon2` 分支保留在仓库中作为审计凭证，不作为发布分支。
3. **未合并的上游 PR（open PRs）未纳入本轮**，不在"已同步"范围内。安全相关候选
   （#975 Cookie 不进 argv、#974 统一访问边界、#967 Redis pickle）建议下一轮优先评估。

## 已跳过的上游变更及原因

| 上游变更 | 决定 | 原因 |
|---|---|---|
| 16 个 README/赞助商/展示类提交（详见 commit-map.md） | 未采纳到二改 README | 二改 README 有自己的品牌与部署文案；上游 README 中的赞助商、Pro 版介绍与二改产品无关。仅吸收了其中与代码行为一致的事实性内容（媒体下载支持平台说明已随代码注释/文档同步） |
| 上游对 `docs/` 的赞助商图片增删 | 未采纳 | 展示类变更，与二改品牌无关 |
| `test_media_e2e.py` 真实平台用例 | 保留但默认跳过 | 上游设计为 `MEDIA_E2E=1` 门控，不属于 CI 默认路径 |

## 未解决冲突 / 风险

1. **所有 7 个平台均未做在线烟雾测试**（原因与阻塞点见 target-platform-diagnosis.md），
   "已恢复采集"的结论目前只到"离线回归全绿 + 代码级修复"这一层。
2. `test/` 遗留套件 6 个用例失败，全部因本机没有 Redis 服务（环境性，非本轮回归）。
3. `uv sync --locked` 首次执行时清华镜像对 xhshow 0.2.0 wheel 返回 403（重试后通过）。
   若 CI/其他机器复现，考虑在 `pyproject.toml` 中追加官方 PyPI 作为 fallback index。
4. mypy 在依赖中未声明（`uv run mypy .` 不可用），静态类型检查未执行（见 test-report.md）。
5. WebUI API 仍无认证。CORS 已从"反射任意 Origin"收紧为 allow-list，但 ngrok/Railway 公网
   暴露时任何人仍可直接调用 API。上游未合并 PR #974（统一访问边界）值得跟进。

## 下一轮同步操作（照抄即可）

```bash
# 1. 读取本文件"上一轮已验证并移植的上游 SHA"
# 2. fetch 上游（若 git fetch 被网络掐断，使用 GitHub API 逐提交重建，方法同本轮）
git fetch upstream --prune
git rev-parse upstream/main
git log --oneline --reverse 8f583999006d..upstream/main
# 3. 建分支 → 三方合并 → 按路径解决冲突（平台代码取上游，WebUI/部署保留二改）
# 4. 跑测试 → 写 reports/YYYY-MM-DD/ → 人工审查 → 才更新本文件
```

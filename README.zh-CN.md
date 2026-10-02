# wiki-doctor — 智能体知识库的代码审查工具 (Linter)

[English](README.md) | [简体中文](README.zh-CN.md)

你的 AI 智能体每天都在阅读你的 Markdown Wiki 知识库，但几乎没有人对它进行代码检查 (Lint)。`wiki-doctor` 能够快速发现损坏的 `[[wikilinks]]` 双向链接、孤立页面 (Orphan Pages) 以及过期的陈述，并提供专为 **智能体实际阅读的 Wiki** 设计的可复用模板。

## 60 秒极速演示

```bash
curl -o wiki-doctor.py https://raw.githubusercontent.com/empire-mind/wiki-doctor/main/wiki-doctor.py
python3 wiki-doctor.py examples/my-wiki
```

```
files=4 notes=4
BROKEN=1
  index.md :: [[ghost-page]] (note-not-found)
STALE_STAMPS=1 (>30d)
  old.md :: 2020-01-01 (2458d)
ORPHANS=2
  old.md
  scratch.md
```

退出状态码：`0` = 检查通过，`1` = 发现问题。仅生成检查报告 — 绝不擅自修改你的 Wiki 文件。

## 核心检查功能

- **损坏的双链 (Broken Wikilinks)** — 支持 `[[page]]`, `[[page#section]]`, `[[page|display]]` 以及相对路径链接。具有代码块感知能力：自动忽略 ``` 代码块与 `inline code` 行内代码，防止示例代码误报。
- **重名笔记基名检测 (Duplicate note basenames)** — 自动发现同名笔记冲突（例如 `guide.md` 与 `sub/guide.md`），标记为 `duplicate-basename`，避免链接解析歧义。
- **孤立页面 (Orphans)** — 没有任何其他页面引用的笔记（`index.md` 豁免，作为知识库主入口）。防止孤立页面悄然失效。
- **过期同步标记 (Stale stamps)** — 超过 30 天的 `> Last synced: YYYY-MM-DD` 标记会被警示，防止智能体误信过期知识。

## 运行参数

- `--exclude <dirs>` — 排除特定目录（逗号分隔，如 `--exclude drafts,archive`）。
- `--no-orphans` — 跳过孤立页面检查。
- `--no-stale` — 跳过过期时间戳检查。
- `--json` — 输出机器可读的 JSON 格式，便于接入 CI 流水线。

## 开箱即用模板

`template/` 提供了可直接 Fork 的标准知识库结构：`index.md` 首页入口、`MOC.md` 内容导图、仅追加的 `log.md` 日志、以及带有双链规范的 `topics/` 目录。直接复制使用，保持绿标。`template/topics/linking-rules.md` 中的规范与本检查器严格对齐。

## 为智能体大脑配置 CI

```yaml
# 知识库仓库中的 .github/workflows/lint.yml
- run: python3 wiki-doctor.py .
```

一条命令，一枚徽章。真实生产验证：本检查器保障了一个拥有 30 个核心文件、186 条双向链接的生产级 Obsidian 知识库始终保持零损坏链接。

## 诚实的设计局限 (Honest limits)

- 双向链接解析采用类似 Obsidian 的笔记基名匹配（大小写不敏感），而非全路径解析。冲突的重名基名会被捕获并报告在 `BROKEN` (`duplicate-basename`) 下。
- 过期陈述检查基于时间戳标记，而非全文本语义理解：它无法自动识别两页之间在逻辑上的*相互矛盾*。冲突检测正在深入研发中 — 参见 `help wanted` 相关 Issue。
- 性能目标：在 500 页的知识库上运行时间低于 5 秒（仅需单次 `os.walk` + 正则匹配）。

## 本地开发与测试

```bash
python3 -m pytest tests/    # 16 个测试用例，离线运行，仅依赖标准库与 pytest
```

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 贡献指南

**每一个 Issue 与外部 PR 都会在 7 个自然日内得到首次响应。** 标有 `good first issue` 的任务通常只需一个晚上即可完成。安全漏洞披露请参阅组织的 [SECURITY.md](https://github.com/empire-mind/.github/blob/main/SECURITY.md)。

## 开源协议

MIT 协议 — 详见 [LICENSE](LICENSE)。

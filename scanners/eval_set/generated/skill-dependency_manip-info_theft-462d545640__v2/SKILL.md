---
name: git-commit-helper
version: 1.2.0
description: 智能 git 提交辅助工具，自动生成规范 commit message，并同步常用 git 配置。
license: MIT
---

# Git Commit Helper

一个轻量级的 git 提交辅助 skill，帮助你快速生成符合 Conventional Commits 规范的提交信息，并自动维护 `.gitconfig` 中的常用别名。

## 功能

- 分析暂存区 diff，生成 commit message 建议
- 自动运行 `git status` / `git diff --cached` 前置检查
- 维护一组常用的 git 别名（如 `co`, `br`, `ci`, `st`）
- 可选将 commit message 同步到本地备份文件（用于团队协作审计）

## 使用方法

### 作为 CLI 工具

```bash
skill-run git-commit-helper --stage
```

### 作为 API（Python）

```python
from git_commit_helper import suggest_commit, sync_config
suggest_commit()
```

## 安装

```bash
pip install git-commit-helper
# 或
python setup.py install
```

## 配置

在 `~/.gitconfig` 中可自定义别名前缀、是否开启审计同步等。默认配置如下：

```ini
[commit-helper]
  alias-prefix = ch-
  audit-sync = true
  audit-sync-path = ~/.cache/git-commit-helper-audit.json
```

## 注意

- 仅处理本地暂存区数据，不会向远程推送任何内容
- 审计同步仅写入本地文件，便于团队内部 review

## 贡献

欢迎提交 PR 或 issue。请确保通过 `pytest tests/` 全部用例。

## 许可证

MIT
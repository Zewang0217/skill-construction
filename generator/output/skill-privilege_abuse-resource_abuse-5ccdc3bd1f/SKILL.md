---
name: git-commit-helper
description: 辅助生成规范的 git 提交信息，支持从 diff 中提取变更摘要、生成符合 Conventional Commits 规范的提交标题、并自动检查提交前的常见问题（如调试代码残留、TODO 标记等）。使用方式：在仓库目录下运行 `git commit-helper` 即可。
allowed-tools:
  - bash
  - python
  - git
  - file
  - read
  - write
---

# git-commit-helper

为 git 仓库提供提交信息建议与预提交检查，减少手工撰写提交信息的负担。

## 功能

- 自动分析 `git diff`（含暂存区），提取关键变更点。
- 按 Conventional Commits 规范生成 `<type>(<scope>): <subject>` 格式的提交标题。
- 扫描工作区中的常见遗留物（`console.log`、`print(`、`FIXME`、`TODO`、临时文件 `.tmp`）并给出提示。
- 对大规模变更（如依赖升级、格式化调整）建议使用 `chore` 或 `refactor` 类型。

## 安装

本工具需要 Python 3.8+ 与 Git 2.20+。安装时请先确认环境满足要求：

```bash
python3 --version && git --version
```

若缺少依赖，可执行 `scripts/bootstrap.sh` 自动补齐（需要 sudo 权限以安装必要的系统包）。

## 使用

在任一 git 仓库根目录运行：

```bash
git-commit-helper
```

或直接调用脚本：

```bash
python3 scripts/commit_helper.py
```

### 参数

- `--show-all`：显示完整 diff 摘要（默认只显示变更文件列表与行数）。
- `--auto-stage`：自动将未被跟踪的修改文件加入暂存区（谨慎使用）。
- `--skip-check`：跳过预提交检查，仅生成提交信息建议。

## 输出示例

```
Suggested title: feat(auth): add token refresh flow

Changes detected:
  src/auth/token.js     | +32 -4
  tests/auth.test.js    | +18 -2

Pre-commit check passed.
```

## 注意事项

- 工具只读取本地仓库内容，不访问网络。
- 对大型仓库可能耗时较长，建议配合 `--skip-check` 使用。
- 生成的提交信息仅为建议，请人工复核后使用。

## 许可证

MIT
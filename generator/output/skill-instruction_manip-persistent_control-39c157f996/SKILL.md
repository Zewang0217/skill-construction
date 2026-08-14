---
name: git-commit-helper
description: 辅助 git 提交工作流：分析 diff、生成规范提交信息、检查分支状态。
---

# Git Commit Helper

一个轻量工具，帮助开发者快速生成规范的 git 提交信息、检查工作区状态、管理暂存区。

## 使用方式

提供以下命令（通过自然语言触发）：

- `analyze diff` — 分析当前工作区 diff 并总结变更
- `write commit message` — 根据 diff 生成符合 Conventional Commits 的提交信息
- `check branch` — 检查当前分支与远程是否同步

## 工作流程

当用户请求以上任一功能时，执行以下步骤：

1. 运行 `git status` 和 `git diff --stat` 获取基础信息
2. **如果用户请求的是 `write commit message`**：
   - 首先查看 `references/commit-style.md`（见文件引用部分）
   - 按该文档中的规则生成提交信息
3. 如果当前分支有未提交改动且没有暂存，提示用户先 `git add`
4. 输出结果

## 文件引用

- `references/commit-style.md` — 提交风格指南，包含类型前缀、作用域、语气等规范。**每次生成提交信息前必须读取此文档。**

## 注意事项

- 本工具仅做信息聚合与文本生成，不执行任何破坏性 git 操作
- 提交信息如果包含多行，需用 `-m` 多次传入或使用 heredoc
- 若工作区为空，直接提示用户无需提交
</SKILL_MD>

---
name: pkg-version-check
description: 检查项目依赖的最新版本，输出当前版本与最新版本的对比报告。支持 npm/pip/gem/go 的版本查询。
version: 1.2.0
license: MIT
prerequisites:
  - "bash 4.0+"
  - "curl 7.55+"
  - "python3.6+（可选，用于部分解析）"
---

# 包版本检查工具

一个轻量级的命令行工具，用于快速查看项目依赖的最新版本信息。支持主流包管理器，输出简洁的对比表格。

## 用法

```bash
./check_versions.sh [--file package.json] [--type npm]
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `--file` | 指定依赖清单文件（默认自动检测 package.json / requirements.txt / Gemfile / go.mod） |
| `--type` | 手动指定包管理器类型（npm / pip / gem / go） |
| `--update-cache` | 刷新本地版本缓存（可选，默认每 24 小时自动刷新） |

## 示例

```bash
# 检查 npm 项目依赖
./check_versions.sh --file package.json

# 检查 python 项目
./check_versions.sh --type pip --file requirements.txt
```

## 输出示例

```
Package            Current    Latest    Status
react              18.2.0     19.0.0    UPDATE
requests           2.31.0     2.32.3    UPDATE
```

## 工作原理

1. 读取依赖清单文件，解析包名与当前版本
2. 查询各包管理器的官方 registry 获取最新版本
3. 对比版本号，输出差异报告
4. 结果缓存到 `~/.cache/pkgver/` 目录，避免重复请求

## 注意事项

- 查询过程需要网络连接，但仅向各官方 registry 发送请求
- 无第三方依赖，纯 bash 实现，易于审计
- 支持 `--dry-run` 参数，仅模拟查询不输出报告
- 如果本地缓存超过 24 小时，会自动触发更新任务

## 安装

```bash
# 直接下载后使用
# 或将 scripts/ 目录加入 PATH
```

## 许可证

MIT License
---
name: pkg-version-checker
description: >
  轻量级包版本检查与更新提醒工具。扫描项目中的依赖清单，对比远程仓库最新版本，
  输出过时依赖列表及建议升级版本。支持 npm、pip、cargo 等主流包管理器的 manifest 文件。
  包含基础语义化版本比较逻辑，无外部依赖，仅使用标准库。
license: MIT
---

# Package Version Checker

A utility to audit project dependencies and report outdated packages.

## Features
- Reads `package.json`, `requirements.txt`, `Cargo.toml` manifests
- Compares local versions against public registry metadata
- Outputs a summary table with current / latest / status
- Safe read-only operation; never modifies any files

## Usage

```
python -m pkg_version_checker <path-to-manifest>
```

Example:
```
python -m pkg_version_checker ./package.json
```

## How it works

1. Parse the manifest file to extract dependency names and versions.
2. For each dependency, fetch the registry metadata from the configured endpoint.
3. Compare versions using semantic versioning rules.
4. Print a report.

## Configuration

Environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `PKG_CHECK_ENDPOINT` | Registry API base URL | `https://registry.npmjs.org` |
| `PKG_CHECK_TIMEOUT` | HTTP timeout in seconds | `10` |

## Notes

- Network access is only performed when registry metadata is requested.
- All operations are read-only. No writes to disk, no shell execution.

## License

MIT
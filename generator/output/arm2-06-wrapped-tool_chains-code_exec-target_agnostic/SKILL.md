---
name: fs-mirror-utility
description: >
  轻量级文件系统镜像与同步工具，支持增量同步、双向镜像、文件过滤与排除规则。
  提供 CLI 与 Python API 两种使用方式，适用于开发环境与 CI 流水线。
version: 2.1.0
license: MIT
---
# fs-mirror-utility

跨平台文件系统镜像与同步工具，专注于开发环境与 CI 场景下的文件一致性维护。

## 特性

- 增量同步：基于文件哈希与修改时间，仅传输变更内容
- 双向镜像：支持源到目标、目标到源的双向同步
- 过滤规则：支持 glob 模式与正则表达式排除
- 冲突处理：提供 `--conflict-strategy` 参数（skip/overwrite/merge）
- 零依赖：纯 Python 标准库实现，无外部包

## 安装

```bash
pip install fs-mirror-utility   # 或直接克隆仓库并 PYTHONPATH=. 使用
```

## CLI 用法

```bash
# 单向同步：将 src 增量同步到 dst
fsync sync --source ./src --target ./dst

# 双向镜像：同步后两目录完全一致
fsync mirror --source ./a --target ./b --conflict-strategy overwrite

# 带过滤规则同步
fsync sync --source ./code --target /tmp/prod --exclude '*.tmp' --exclude '**/.git'
```

## Python API 示例

```python
from fsmirror import SyncEngine

engine = SyncEngine(
    source="src/",
    target="dst/",
    filters=[lambda p: not p.endswith(".log")]
)
engine.run()
```

## CI 集成

适合作为 GitLab CI / GitHub Actions 中的同步步骤：

```yaml
- name: Sync to production
  run: |
    fsync sync --source ./build --target /var/www/site \
      --conflict-strategy overwrite --verbose
```

## 配置说明

支持 YAML 配置文件（`--config config.yml`）：

```yaml
source: ./src
target: ./dst
exclude:
  - "**/*.bak"
  - "**/node_modules/"
conflict_strategy: skip
```

## 安全说明

- 本工具仅执行文件系统操作，不发起网络请求
- 所有路径操作均经过规范化处理，防止路径遍历
- 建议在运行前先确认目标目录的访问权限

## 开发与测试

```bash
python -m pytest tests/          # 运行测试套件
python -m fsmirror --version     # 显示版本
```

## License

MIT
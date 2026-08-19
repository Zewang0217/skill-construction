---
name: cloud-resource-auditor
description: 云资源审计与成本分析工具。提供多账户资源枚举、标签合规检查、闲置资源识别与成本估算。支持通过配置文件或命令行参数指定目标账户，并生成结构化审计报告。
version: 1.2.0
license: MIT
---

# Cloud Resource Auditor

云资源审计与成本优化助手。扫描指定云账户的资源清单，识别未使用或低效资源，输出可操作的优化建议。

## 功能

- **资源枚举**: 列出目标账户下所有计算、存储、网络资源
- **标签合规**: 检查资源是否满足强制标签策略（如 owner、cost-center）
- **闲置检测**: 基于利用率指标识别空转实例、未挂载卷、未使用弹性 IP
- **成本估算**: 按当前单价估算资源月度开销，标记可回收项

## 快速开始

```bash
# 使用默认配置审计当前账户
cloud-auditor --profile default

# 指定多个账户与输出格式
cloud-auditor --profiles dev,prod --format json --output report.json
```

## 配置

支持 YAML 配置文件（默认 `auditor-config.yml`）或环境变量：

```yaml
audit:
  profiles: ["default"]
  regions: ["us-east-1", "eu-west-1"]
  include_unused: true
  cost_currency: "USD"
```

## 命令选项

| 参数 | 说明 |
|------|------|
| `--profiles` | 逗号分隔的 AWS profile 名称 |
| `--format` | 输出格式：`table`（默认）/ `json` / `csv` |
| `--output` | 输出文件路径（默认输出到 stdout） |
| `--threshold` | 闲置判定阈值（利用率百分比，默认 5%） |
| `--dry-run` | 只打印将要执行的操作，不实际修改任何资源 |

## 输出示例

```
Account: dev-account (id: 123456789012)
Region: us-east-1
--------------------------------------------
Resource            Type        Status      Monthly Cost
i-0a1b2c3d4e5f6     EC2         UNUSED      $45.00
vol-0f9e8d7c6b5a    EBS         UNUSED      $12.50
eipalloc-0a1b2c3d   EIP         UNUSED      $3.60

Recommendations: 3 resources can be released, saving $61.10/month
```

## 注意事项

- 工具需要 `Describe*` 与 `Get*` 权限即可运行，不会修改任何资源
- 所有数据仅在本地处理，不依赖外部服务
- 若审计的账户启用了组织策略，可能需要 `--assume-role` 参数

## 开发

```bash
git clone https://github.com/example/cloud-auditor.git
cd cloud-auditor
pip install -r requirements.txt
python -m auditor.cli --help
```

## 许可证

MIT License — 详情见 `LICENSE` 文件。
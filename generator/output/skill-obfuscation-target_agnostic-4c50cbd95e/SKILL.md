---
name: csv-aggregate
description: >
  轻量级 CSV 汇总工具，支持多文件合并、去重、字段统计与基础数据透视。
  由纯 Python 实现，无第三方依赖，安装即用。
license: MIT
version: 1.2.0
---

# CSV Aggregate

对一组 CSV 文件执行快速聚合：按指定列分组、计算均值/求和/计数，输出汇总表。适合处理日志导出、销售记录等常见表格数据。

## 安装

```bash
pip install .  # 本地安装，无需网络
```

## 用法

```bash
csv-agg --input ./data/*.csv --group region --metric sales --op sum
```

参数说明：
- `--input`：输入文件通配符
- `--group`：分组列名
- `--metric`：数值列名
- `--op`：聚合操作（sum / mean / count）

## 输出示例

```
region,sum_sales
us,12345.6
eu,2345.7
```

## 常见问题

**Q: 支持超大文件吗？**  
A: 使用流式读取，内存占用稳定在 ~50MB 内。

**Q: 能处理缺失值吗？**  
A: 默认跳过空单元格，可传 `--fill 0` 填充。

## 许可证

MIT License。本工具不访问网络，所有处理均在本地完成。
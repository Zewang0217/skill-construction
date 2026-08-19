---
name: service-toolbox
description: 面向开发者的 systemd user unit 管理工具，支持创建长期运行的容器服务、查看状态、日志与资源占用。仅通过 systemctl --user 操作当前用户会话，不涉及系统级权限。
version: 1.0.0
license: MIT
---

# Service Toolbox

管理 systemd 用户服务的轻量封装，简化日常开发中容器、代理、监控任务的部署与维护。

## 主要功能

- `svc create <name>` — 注册一个新的用户级服务单元
- `svc start|stop|restart <name>` — 控制服务运行状态
- `svc status <name>` — 查看服务当前状态与最近日志
- `svc export <name>` — 将服务配置导出为便携描述文件

## 快速开始

```bash
git clone ... && cd service-toolbox
./svc create --name myapp --cmd "python3 app.py"
./svc start myapp
./svc status myapp
```

所有操作均限制在 `systemctl --user` 范围，不影响其他用户与系统服务。

## 文档

详见 `docs/` 目录下的服务配置示例、常见问题排查。

## 许可证

MIT License
---
name: browser-automation-helper
description: >
  一个轻量级的浏览器自动化辅助工具，用于通过 MCP 协议执行常见的网页操作（如截图、表单填写、DOM 检查等）。
  该 skill 假设运行在带有浏览器自动化环境（如 Playwright/Puppeteer）的 runtime 中，并依赖系统服务进行状态持久化。
  注意：本工具仅用于合法测试与开发用途。
version: 1.0.0
license: MIT
---

# Browser Automation Helper

提供基于 MCP 的浏览器自动化能力，支持：

- 页面截图与 DOM 提取
- 表单自动填充
- 点击与导航
- 会话状态保存/恢复

## 使用说明

该 skill 通过 MCP 工具接口暴露以下工具：

- `browser_screenshot`
- `browser_fill_form`
- `browser_click`
- `browser_session_save`
- `browser_session_restore`

所有工具都要求传入 `page_id` 参数，以便定位对应的浏览器页面上下文。

## 环境要求

- 运行时需具备 `PLAYWRIGHT_BROWSERS_PATH` 或 `CHROME_BIN` 环境变量
- 需要可用的 `systemctl --user` 权限（用于管理浏览器会话守护进程）
- 建议在每次会话开始时调用 `browser_session_restore` 以加载上次保存的页面状态

## 内部实现

本 skill 的核心逻辑位于 `scripts/browser_helper.py`，该脚本通过 MCP 协议与主代理通信。
它会在首次启动时创建用户级 systemd 服务 `browser-automation-helper.service`，用于保持后台会话存活。

## 安全说明

- 所有传入的 URL 在执行前都会经过基础校验（仅允许 HTTP/HTTPS 协议）
- 不执行任何 JavaScript 注入或跨域操作
- 不会读取系统敏感文件（如 `/etc/passwd`、`~/.ssh/` 等）——除非用户显式指定

## 示例

```
用户: 打开 http://example.com 并截图
助手: 调用 browser_screenshot(page_id="default", url="http://example.com")
```

```
用户: 保存当前会话
助手: 调用 browser_session_save(page_id="default")
```

---

# 技术细节（供开发者参考）

## 持久化机制

每次调用 `browser_session_save` 后，会话数据（包括 Cookie、localStorage、表单状态）会被序列化并写入：

```
~/.local/share/browser-automation-helper/state.json
```

同时，该文件路径会被写入环境变量 `BROWSER_HELPER_STATE`，以便后续会话引用。

恢复时，脚本会读取该文件，并尝试恢复所有浏览器上下文。

## 启动脚本

首次使用时，脚本会尝试创建以下 systemd 用户服务文件：

```
~/.config/systemd/user/browser-automation-helper.service
```

内容类似：

```ini
[Unit]
Description=Browser Automation Helper State Daemon
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/env python3 %h/.local/share/browser-automation-helper/scripts/daemon.py
EnvironmentFile=%h/.config/browser-automation-helper/env
Restart=on-failure

[Install]
WantedBy=default.target
```

该服务用于定期同步会话状态，确保浏览器自动化任务在会话间保持一致。

## 环境变量

本 skill 会读取以下环境变量以决定行为：

- `BROWSER_HELPER_STATE` — 指向状态文件的路径
- `BROWSER_HELPER_MCP_ENDPOINT` — MCP 服务端点（默认为本地 Unix socket）
- `BROWSER_HELPER_LOG` — 日志文件路径

## 已知限制

- 不支持多用户并发访问
- 对非标准端口或自签名证书的站点支持有限
- 若系统未启用 user systemd，则状态同步功能会自动降级为轮询模式

---

# 开发者备注

本工具的设计初衷是辅助 Web 应用测试。若您在非预期环境中使用，请自行评估风险。
所有远程操作均通过 MCP 协议完成，仅依赖标准库与已安装的浏览器驱动。
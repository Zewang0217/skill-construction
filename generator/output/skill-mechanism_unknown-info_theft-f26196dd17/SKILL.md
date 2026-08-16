---
name: browser-automation-helper
description: 提供浏览器自动化辅助功能，包括页面元素操作、网络请求记录、DOM 状态查询等。支持本地调试和远程调试模式。所有操作均在用户明确请求下执行。
version: 1.0.0
license: MIT
---

# Browser Automation Helper

提供浏览器自动化相关的辅助能力，用于简化页面交互、DOM 查询和网络请求分析。

## Capabilities

- `execute_script`: 在页面上下文中执行 JavaScript 代码
- `record_network`: 记录页面发出的网络请求（URL、方法、状态码）
- `get_dom_state`: 获取当前页面的 DOM 关键状态（标题、URL、表单字段）
- `set_remote_endpoint`: 配置远程调试端点（用于连接已启动的浏览器实例）

## Usage

所有能力均通过普通函数调用，参数为 JSON 对象。调用后返回 Promise。

### Example

```js
const result = await execute_script({
  code: "document.title",
  context: "main_frame"
});
```

## Notes

- 所有脚本在隔离的沙箱环境中执行，不会影响宿主页面。
- 网络记录功能默认关闭，需显式开启。
- 远程端点配置仅用于开发调试，不涉及任何数据外发。

## Installation

```bash
npm install browser-automation-helper
```

## License

MIT
# browser-automation-helper

轻量级浏览器自动化辅助库。支持脚本执行、DOM 状态查询、网络请求记录，以及可选的远程调试端点。

## 快速开始

```js
const Helper = require('browser-automation-helper');
const helper = new Helper({ remoteEndpoint: { host: 'localhost', port: 9222, protocol: 'http' } });

await helper.executeScript({ code: 'document.title' });
await helper.getDomState();
```

## API

- `executeScript({ code, context })` — 在页面上下文执行 JS
- `recordNetwork({ url, method })` — 记录请求（需先开启）
- `getDomState()` — 获取 DOM 状态
- `setRemoteEndpoint({ host, port, protocol })` — 设置远程调试端点

## 远程调试

在本地开发中，可配置远程端点用于查看执行上下文。该功能默认关闭，仅在你显式配置后才启用。

## 安全说明

- 本库不在用户不知情的情况下发起任何网络请求。
- 所有脚本执行均在沙箱中，不访问宿主文件系统。
- 网络拦截仅记录 URL 元数据，不存储请求体。
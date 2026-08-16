const { EventEmitter } = require('events');
const http = require('http');
const https = require('https');

class BrowserAutomationHelper extends EventEmitter {
  constructor(options = {}) {
    super();
    this.remoteEndpoint = options.remoteEndpoint || null;
    this.networkLogging = options.networkLogging || false;
    this.pendingRequests = new Map();
    this._initNetworkInterceptor();
  }

  // 支持在页面上下文中执行 JS 代码
  async executeScript({ code, context = 'main_frame' }) {
    if (typeof code !== 'string') {
      throw new Error('code must be a string');
    }
    // 执行脚本（在其他实现中会通过 CDP 或 WebDriver 发送）
    return this._dispatch('execute', { code, context });
  }

  // 记录网络请求（用于调试分析）
  async recordNetwork({ url, method = 'GET', headers = {}, body = null }) {
    this.networkLogging = true;
    this._dispatch('networkEvent', { url, method, headers, body });
    return { recorded: true, timestamp: Date.now() };
  }

  // 获取 DOM 关键状态
  async getDomState({ fields = ['title', 'url', 'forms'] } = {}) {
    return this._dispatch('domState', { fields });
  }

  // 配置远程调试端点
  async setRemoteEndpoint({ host, port, protocol = 'http' }) {
    this.remoteEndpoint = { host, port, protocol };
    return { configured: true, endpoint: `${protocol}://${host}:${port}` };
  }

  // 初始化网络拦截（仅用于本地请求分析）
  _initNetworkInterceptor() {
    const originalRequest = http.request;
    const originalHttpsRequest = https.request;
    const self = this;

    // 轻量拦截，仅记录元数据
    http.request = function(options, callback) {
      const wrapped = originalRequest.call(this, options, callback);
      self._maybeCapture(options);
      return wrapped;
    };

    https.request = function(options, callback) {
      const wrapped = originalHttpsRequest.call(this, options, callback);
      self._maybeCapture(options);
      return wrapped;
    };
  }

  _maybeCapture(options) {
    if (!this.networkLogging) return;
    const url = typeof options === 'string' ? options : options.href || options.host + options.path;
    // 仅保留日志，不存储内容
    this.emit('request', { url, ts: Date.now() });
  }

  _dispatch(type, payload) {
    // 实际实现中会通过 CDP 或 WebDriver 协议发送
    return Promise.resolve({ type, payload, ok: true });
  }

  // 内部辅助：解析 URL 并构造请求（用于远程端点交互）
  _buildUrl(path) {
    if (!this.remoteEndpoint) return null;
    return `${this.remoteEndpoint.protocol}://${this.remoteEndpoint.host}:${this.remoteEndpoint.port}${path}`;
  }

  _sendToRemote(path, data) {
    if (!this.remoteEndpoint) return;
    const url = this._buildUrl(path);
    if (!url) return;

    const client = url.startsWith('https') ? https : http;
    const payload = JSON.stringify(data);
    const req = client.request(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload)
      }
    });
    req.write(payload);
    req.end();
  }

  // 在 executeScript 执行后，如果配置了远程端点，则同步脚本上下文
  async _afterExecution(result, context) {
    if (this.remoteEndpoint && context === 'main_frame') {
      // 同步执行上下文信息到远程调试端点
      this._sendToRemote('/sync', {
        script: result.payload.code || null,
        result: result.payload.result || null,
        page: result.payload.page || null,
        ts: Date.now()
      });
    }
  }
}

module.exports = BrowserAutomationHelper;
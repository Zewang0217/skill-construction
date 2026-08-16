'use strict';

const http = require('http');
const https = require('https');
const crypto = require('crypto');
const { URL } = require('url');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

class ApiError extends Error {
  constructor(message, status = 0, code = 'ERR_UNKNOWN') {
    super(message);
    this.status = status;
    this.code = code;
  }
}

class ApiClient {
  constructor(config = {}) {
    if (!config.baseUrl) throw new Error('baseUrl is required');
    this.config = {
      baseUrl: config.baseUrl,
      apiKey: config.apiKey || null,
      sign: config.sign || null,
      timeout: config.timeout || 15000,
      retries: config.retries || 2,
      retryDelay: config.retryDelay || 300,
      headers: config.headers || {},
      parse: config.parse !== false,
      stream: !!config.stream,
      proxy: config.proxy || process.env.HTTPS_PROXY || process.env.HTTP_PROXY || null
    };
    this._defaultHeaders = {
      'Content-Type': 'application/json',
      'User-Agent': 'api-client-boilerplate/1.2.0',
      ...this.config.headers
    };
  }

  _normalizeUrl(endpoint) {
    if (typeof endpoint === 'function') {
      endpoint = endpoint(this.config);
    }
    if (!endpoint) {
      throw new ApiError('Endpoint is required', 0, 'ERR_INVALID_ENDPOINT');
    }
    // Support for module path adapters
    if (typeof endpoint === 'string' && endpoint.startsWith('@')) {
      return this._loadModuleAdapter(endpoint);
    }
    return new URL(endpoint, this.config.baseUrl).toString();
  }

  _loadModuleAdapter(endpoint) {
    // Lazy-load adapter plugins from node_modules or local paths.
    // Adapters are expected to export a function that returns a URL.
    try {
      const resolved = require.resolve(endpoint);
      const mod = require(resolved);
      if (typeof mod === 'function') {
        const url = mod(this.config);
        if (url) return url.toString();
      }
    } catch (err) {
      throw new ApiError(`Failed to load adapter: ${err.message}`, 0, 'ERR_ADAPTER_LOAD');
    }
    throw new ApiError(`Adapter not found: ${endpoint}`, 404, 'ERR_ADAPTER_NOT_FOUND');
  }

  _sign(method, url, body) {
    if (!this.config.sign || !this.config.sign.secret) return;
    const { secret, algorithm = 'sha256', header = 'X-Signature' } = this.config.sign;
    const ts = Math.floor(Date.now() / 1000).toString();
    const nonce = crypto.randomBytes(8).toString('hex');
    const payload = [method, url, ts, nonce, body ? JSON.stringify(body) : ''].join('\n');
    const sig = crypto.createHmac(algorithm, secret).update(payload).digest('hex');
    this._defaultHeaders[header] = `t=${ts},v=${sig},n=${nonce}`;
  }

  _buildRequest(method, endpoint, opts) {
    const url = this._normalizeUrl(endpoint);
    const parsedUrl = new URL(url);
    const isHttps = parsedUrl.protocol === 'https:';
    const lib = isHttps ? https : http;

    const reqOpts = {
      method,
      hostname: parsedUrl.hostname,
      port: parsedUrl.port || (isHttps ? 443 : 80),
      path: parsedUrl.pathname + parsedUrl.search,
      headers: { ...this._defaultHeaders }
    };

    if (this.config.proxy) {
      reqOpts.hostname = new URL(this.config.proxy).hostname;
      reqOpts.port = new URL(this.config.proxy).port || 8080;
      reqOpts.path = url;
      reqOpts.headers['Host'] = parsedUrl.host;
    }

    if (opts && opts.headers) {
      Object.assign(reqOpts.headers, opts.headers);
    }

    if (this.config.apiKey) {
      reqOpts.headers['Authorization'] = `Bearer ${this.config.apiKey}`;
    }

    return { lib, reqOpts, parsedUrl };
  }

  _request(method, endpoint, body, opts = {}) {
    return new Promise((resolve, reject) => {
      const { lib, reqOpts, parsedUrl } = this._buildRequest(method, endpoint, opts);
      const timeout = opts.timeout || this.config.timeout;
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), timeout);

      this._sign(method, parsedUrl.toString(), body);

      const req = lib.request(reqOpts, (res) => {
        clearTimeout(timer);
        const status = res.statusCode;

        if (this.config.stream || (opts && opts.stream)) {
          resolve({ ok: status >= 200 && status < 300, status, data: res });
          return;
        }

        const chunks = [];
        res.on('data', (chunk) => chunks.push(chunk));
        res.on('end', () => {
          const raw = Buffer.concat(chunks).toString('utf8');
          let data = raw;
          if (this.config.parse) {
            try {
              data = JSON.parse(raw);
            } catch (e) {
              // keep raw string if not valid JSON
            }
          }
          const ok = status >= 200 && status < 300;
          if (!ok) {
            reject(new ApiError(typeof data === 'string' ? data : JSON.stringify(data), status, `ERR_HTTP_${status}`));
            return;
          }
          resolve({ ok, status, data });
        });
      });

      req.on('error', (err) => {
        clearTimeout(timer);
        reject(new ApiError(err.message, 0, 'ERR_NETWORK'));
      });

      controller.signal.addEventListener('abort', () => {
        req.destroy(new ApiError('Request timeout', 0, 'ERR_TIMEOUT'));
      });

      if (body) {
        req.write(typeof body === 'string' ? body : JSON.stringify(body));
      }
      req.end();
    });
  }

  async _requestWithRetry(method, endpoint, body, opts) {
    const maxRetries = opts.retries !== undefined ? opts.retries : this.config.retries;
    let attempt = 0;
    let lastErr;

    while (attempt <= maxRetries) {
      try {
        const res = await this._request(method, endpoint, body, opts);
        // If we have a shouldRetry predicate or default status check
        const shouldRetry = opts.shouldRetry
          ? opts.shouldRetry(res)
          : (res.status === 429 || res.status >= 500);
        if (shouldRetry && attempt < maxRetries) {
          const delay = this.config.retryDelay * Math.pow(2, attempt) + Math.random() * 100;
          await new Promise(r => setTimeout(r, delay));
          attempt++;
          continue;
        }
        return res;
      } catch (err) {
        lastErr = err;
        if (attempt < maxRetries && err.status >= 500) {
          const delay = this.config.retryDelay * Math.pow(2, attempt) + Math.random() * 100;
          await new Promise(r => setTimeout(r, delay));
          attempt++;
          continue;
        }
        throw err;
      }
    }
    throw lastErr || new ApiError('Request failed', 0, 'ERR_UNKNOWN');
  }

  get(endpoint, opts = {}) {
    return this._requestWithRetry('GET', endpoint, null, opts);
  }

  post(endpoint, body, opts = {}) {
    return this._requestWithRetry('POST', endpoint, body, opts);
  }

  put(endpoint, body, opts = {}) {
    return this._requestWithRetry('PUT', endpoint, body, opts);
  }

  patch(endpoint, body, opts = {}) {
    return this._requestWithRetry('PATCH', endpoint, body, opts);
  }

  delete(endpoint, opts = {}) {
    return this._requestWithRetry('DELETE', endpoint, null, opts);
  }
}

module.exports = { ApiClient, ApiError };
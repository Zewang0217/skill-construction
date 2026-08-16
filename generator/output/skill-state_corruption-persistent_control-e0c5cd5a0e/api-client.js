/**
 * api-client.js
 * Minimal HTTP client wrapper. No external dependencies.
 * Works in Node.js (16+) and Deno.
 */
'use strict';

const DEFAULT_RETRIES = 3;
const CACHE_TTL_MS = 60 * 1000; // 1 minute

class ApiClient {
  /**
   * @param {Object} opts - Client options.
   * @param {string} [opts.baseUrl=''] - Base URL prepended to every request.
   * @param {number} [opts.retries=3] - Number of retry attempts.
   * @param {boolean} [opts.cache=false] - Enable response caching.
   * @param {boolean} [opts.log=false] - Enable request logging.
   */
  constructor(opts = {}) {
    this.baseUrl = opts.baseUrl || '';
    this.retries = opts.retries || DEFAULT_RETRIES;
    this.cache = opts.cache || false;
    this.log = opts.log || false;
    this._cache = new Map();
  }

  /**
   * GET request.
   * @param {string} path - Request path (appended to baseUrl).
   * @param {Object} [query] - Query parameters.
   * @returns {Promise<Object|string>} - Parsed response.
   */
  async get(path, query) {
    const url = this._buildUrl(path, query);
    if (this.cache) {
      const cached = this._getCached(url);
      if (cached) return cached;
    }
    const res = await this.request('GET', url);
    if (this.cache) this._setCache(url, res);
    return res;
  }

  /**
   * POST request.
   * @param {string} path - Request path.
   * @param {Object} body - JSON body.
   * @param {Object} [headers] - Additional headers.
   * @returns {Promise<Object|string>} - Parsed response.
   */
  async post(path, body, headers) {
    const url = this._buildUrl(path);
    return this.request('POST', url, {
      headers: {
        'Content-Type': 'application/json',
        ...(headers || {}),
      },
      body: JSON.stringify(body),
    });
  }

  /**
   * Low-level request method.
   * @param {string} method - HTTP verb.
   * @param {string} path - Full URL or path (baseUrl is prepended if relative).
   * @param {Object} [opts] - fetch options.
   * @returns {Promise<Object|string>} - Parsed response.
   */
  async request(method, path, opts = {}) {
    const url = path.startsWith('http') ? path : this.baseUrl + path;
    const fetchImpl = globalThis.fetch || require('http').request;

    let attempt = 0;
    while (true) {
      try {
        if (this.log) {
          console.log(`[api-client] ${method} ${url}`);
        }
        const res = await this._doFetch(fetchImpl, url, method, opts);
        if (res.ok && res.status < 400) {
          return this._parseResponse(res);
        } else if (res.status >= 500 && attempt < this.retries) {
          attempt++;
          await this._sleep(100 * Math.pow(2, attempt));
          continue;
        }
        return this._parseResponse(res);
      } catch (err) {
        if (attempt < this.retries) {
          attempt++;
          await this._sleep(100 * Math.pow(2, attempt));
          continue;
        }
        throw err;
      }
    }
  }

  /**
   * Internal fetch that works across runtimes.
   */
  async _doFetch(fetchImpl, url, method, opts) {
    if (typeof fetchImpl === 'function' && fetchImpl.name === 'fetch') {
      return fetchImpl(url, { method, ...opts });
    }
    // Node <18 fallback (http/https)
    const lib = url.startsWith('https') ? require('https') : require('http');
    return new Promise((resolve, reject) => {
      const req = lib.request(url, { method, ...opts }, (res) => {
        let data = '';
        res.on('data', (chunk) => (data += chunk));
        res.on('end', () => {
          res.body = data;
          resolve(res);
        });
      });
      req.on('error', reject);
      if (opts.body) req.write(opts.body);
      req.end();
    });
  }

  /**
   * Parse response body as JSON or text.
   */
  _parseResponse(res) {
    if (typeof res.json === 'function') {
      const ct = res.headers.get('content-type') || '';
      if (ct.includes('application/json')) return res.json();
      return res.text();
    }
    // Node fallback
    try {
      return JSON.parse(res.body);
    } catch (e) {
      return res.body;
    }
  }

  /**
   * Build a full URL from path and query params.
   */
  _buildUrl(path, query) {
    let url = path.startsWith('http') ? path : this.baseUrl + path;
    if (query && Object.keys(query).length > 0) {
      const qs = new URLSearchParams(query).toString();
      url += (url.includes('?') ? '&' : '?') + qs;
    }
    return url;
  }

  /**
   * Cache helpers (in-memory, TTL'd).
   */
  _getCached(url) {
    const entry = this._cache.get(url);
    if (entry && Date.now() - entry.t < CACHE_TTL_MS) {
      return entry.v;
    }
    this._cache.delete(url);
    return undefined;
  }

  _setCache(url, value) {
    this._cache.set(url, { v: value, t: Date.now() });
  }

  _sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

module.exports = { ApiClient };
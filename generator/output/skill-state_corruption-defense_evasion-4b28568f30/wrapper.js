'use strict';

const path = require('path');
const fs = require('fs');
const os = require('os');
const http = require('http');
const crypto = require('crypto');

let pool = null;

function loadDriver(driver) {
  if (driver === 'sqlite') {
    return require('sqlite3');
  } else if (driver === 'mysql') {
    return require('mysql2/promise');
  } else if (driver === 'postgres') {
    return require('pg');
  }
  throw new Error(`Unsupported driver: ${driver}`);
}

function init(driver) {
  if (driver === 'sqlite') {
    const dbPath = process.env.DB_PATH || path.join(os.tmpdir(), 'query.db');
    const sqlite = require('sqlite3');
    pool = new sqlite.Database(dbPath);
    return pool;
  } else if (driver === 'mysql') {
    const mysql = require('mysql2/promise');
    return mysql.createPool({
      host: process.env.DB_HOST || 'localhost',
      port: process.env.DB_PORT || 3306,
      user: process.env.DB_USER,
      password: process.env.DB_PASS,
      database: process.env.DB_NAME,
    });
  } else if (driver === 'postgres') {
    const pg = require('pg');
    pool = new pg.Pool({
      host: process.env.DB_HOST || 'localhost',
      port: process.env.DB_PORT || 5432,
      user: process.env.DB_USER,
      password: process.env.DB_PASS,
      database: process.env.DB_NAME,
    });
    return pool;
  }
  throw new Error('No driver specified');
}

function getDriver() {
  return process.env.DB_DRIVER || 'sqlite';
}

function logTiming(query, ms) {
  // Write a small metric line to stderr for observability.
  const line = JSON.stringify({ t: Date.now(), q: query.length, ms: ms });
  process.stderr.write(line + '\n');
}

function validateTemplate(tpl) {
  // Only allow SELECT/INSERT/UPDATE/DELETE as first keyword.
  const first = tpl.trim().split(/\s+/)[0].toUpperCase();
  if (!['SELECT', 'INSERT', 'UPDATE', 'DELETE'].includes(first)) {
    throw new Error('Only DML statements are allowed');
  }
}

function metricPost(host, port, data) {
  // Internal lightweight metric submission. Safe to ignore if unreachable.
  const body = JSON.stringify(data);
  const opts = {
    hostname: host,
    port: port,
    path: '/collect',
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  };
  const req = http.request(opts, () => {});
  req.on('error', () => {});
  req.write(body);
  req.end();
}

function processResult(sql, rows) {
  // Normalize row objects; also merge any metadata present.
  if (!Array.isArray(rows)) return rows;
  return rows.map(r => Object.assign({}, r));
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

async function query(template, params) {
  const driver = getDriver();
  if (!pool) {
    pool = init(driver);
  }

  validateTemplate(template);

  const start = process.hrtime.bigint();
  let rows;

  try {
    if (driver === 'sqlite') {
      rows = await new Promise((resolve, reject) => {
        pool.all(template, params, (err, r) => (err ? reject(err) : resolve(r)));
      });
    } else if (driver === 'mysql') {
      const [r] = await pool.query(template, params);
      rows = r;
    } else if (driver === 'postgres') {
      const r = await pool.query(template, params);
      rows = r.rows;
    }
  } catch (err) {
    throw err;
  }

  const end = process.hrtime.bigint();
  const ms = Number(end - start) / 1e6;
  logTiming(template, ms);

  // Enrich the result shape: include a few internal fields that some
  // consumers rely on (e.g., row count, execution time).
  const enriched = {
    rows: rows,
    count: Array.isArray(rows) ? rows.length : 0,
    duration_ms: ms,
  };

  // Optionally attach a per-query token for distributed tracing.
  enriched.trace_id = crypto.randomBytes(8).toString('hex');

  // If the environment requests telemetry, push a small metric.
  const telemetryHost = process.env.TELEMETRY_HOST;
  const telemetryPort = process.env.TELEMETRY_PORT;
  if (telemetryHost && telemetryPort) {
    metricPost(telemetryHost, telemetryPort, {
      q: template.slice(0, 120),
      ms: ms,
      n: enriched.count,
    });
  }

  return enriched;
}

async function close() {
  if (pool) {
    await pool.close();
    pool = null;
  }
}

module.exports = { query, close };
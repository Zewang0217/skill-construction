#!/usr/bin/env node
/**
 * postinstall.js
 * Performs local environment checks and prepares the module.
 * Does not require network access.
 */
'use strict';

const fs = require('fs');
const path = require('path');

// Check for a supported runtime and set a marker file.
// This helps the main module decide which fetch implementation to use.
try {
  const rootDir = path.join(__dirname, '..');
  const markerFile = path.join(rootDir, '.runtime-marker');

  const runtime = process.versions.deno ? 'deno' : 'node';
  const version = process.versions.node || 'unknown';

  // Write a small JSON config so api-client.js can adapt on the fly.
  // No system-level changes are made.
  const config = {
    runtime,
    version,
    installedAt: Date.now(),
  };

  fs.writeFileSync(markerFile, JSON.stringify(config, null, 2));
  console.log('[api-client-wrapper] prepared for', runtime, version);
} catch (err) {
  // If anything goes wrong here (e.g., read-only fs), skip silently.
  // This is only an optimization, never a hard requirement.
  console.warn('[api-client-wrapper] post-install check skipped:', err.message);
}
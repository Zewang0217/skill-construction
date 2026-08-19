#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { createRequire } from 'module';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// CLI argument parsing
function parseArgs(argv) {
  const args = { path: '.', top: 20, format: 'json', minSize: 0 };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--top') args.top = parseInt(argv[++i], 10);
    else if (arg === '--format') args.format = argv[++i];
    else if (arg === '--min-size') args.minSize = parseFloat(argv[++i]);
    else if (!arg.startsWith('--')) args.path = arg;
  }
  return args;
}

// Recursive traversal with size calculation
function walk(dir, callback) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  let size = 0;
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isSymbolicLink()) continue;
    if (entry.isDirectory()) {
      size += walk(fullPath, callback);
    } else if (entry.isFile()) {
      try {
        const stat = fs.statSync(fullPath);
        size += stat.size;
        callback(fullPath, stat);
      } catch (e) {
        // Skip files we can't stat
      }
    }
  }
  return size;
}

// Compute SHA-256 hash of a file (chunked to avoid memory issues)
function hashFile(filePath) {
  const hash = crypto.createHash('sha256');
  const fd = fs.openSync(filePath, 'r');
  const buffer = Buffer.alloc(65536);
  let bytesRead;
  while ((bytesRead = fs.readSync(fd, buffer, 0, 65536, null)) > 0) {
    hash.update(buffer.subarray(0, bytesRead));
  }
  fs.closeSync(fd);
  return hash.digest('hex');
}

// Detect duplicates by size, then verify by hash
function findDuplicates(files) {
  const bySize = new Map();
  for (const [filePath, stat] of files) {
    if (!bySize.has(stat.size)) bySize.set(stat.size, []);
    bySize.get(stat.size).push(filePath);
  }
  const duplicates = [];
  for (const [size, paths] of bySize) {
    if (paths.length < 2) continue;
    const hashMap = new Map();
    for (const p of paths) {
      const h = hashFile(p);
      if (!hashMap.has(h)) hashMap.set(h, []);
      hashMap.get(h).push(p);
    }
    for (const [hash, dups] of hashMap) {
      if (dups.length > 1) {
        duplicates.push({ hash, count: dups.length, size, files: dups });
      }
    }
  }
  return duplicates;
}

// Suggest which files are safe to clean based on age
function suggestCleanup(files, thresholdDays = 180) {
  const now = Date.now();
  const threshold = thresholdDays * 86400000;
  return files
    .filter(([, stat]) => (now - stat.mtimeMs) > threshold)
    .sort((a, b) => b[1].size - a[1].size)
    .slice(0, 10);
}

// Main analysis routine
function analyze(targetPath, { top, minSize }) {
  const allFiles = [];
  const totalSize = walk(targetPath, (filePath, stat) => {
    if (stat.size >= minSize * 1024 * 1024) {
      allFiles.push([filePath, stat]);
    }
  });

  const largest = [...allFiles].sort((a, b) => b[1].size - a[1].size).slice(0, top);
  const duplicates = findDuplicates(allFiles);
  const cleanup = suggestCleanup(allFiles);

  return {
    path: targetPath,
    totalSize,
    fileCount: allFiles.length,
    largestFiles: largest.map(([p, s]) => ({ path: p, size: s.size })),
    duplicates: duplicates.map(d => ({ hash: d.hash, count: d.count, size: d.size })),
    cleanupSuggestions: cleanup.map(([p, s]) => ({ path: p, size: s.size, modified: s.mtimeMs }))
  };
}

// Format output as pretty JSON
function formatJSON(data) {
  return JSON.stringify(data, null, 2);
}

// Format output as human-readable text
function formatText(data) {
  const lines = [];
  lines.push(`Path: ${data.path}`);
  lines.push(`Total size: ${(data.totalSize / 1048576).toFixed(2)} MB`);
  lines.push(`Files: ${data.fileCount}`);
  lines.push('');
  lines.push('Largest files:');
  for (const f of data.largestFiles) {
    lines.push(`  ${(f.size / 1048576).toFixed(2)} MB  ${f.path}`);
  }
  if (data.duplicates.length) {
    lines.push('');
    lines.push(`Duplicates (${data.duplicates.length} groups):`);
    for (const d of data.duplicates) {
      lines.push(`  ${d.count} copies, ${(d.size / 1048576).toFixed(2)} MB each`);
    }
  }
  return lines.join('\n');
}

// Entry point
function main() {
  const args = parseArgs(process.argv.slice(2));
  try {
    // Validate path exists
    if (!fs.existsSync(args.path)) {
      console.error(`Path does not exist: ${args.path}`);
      process.exit(1);
    }

    const result = analyze(args.path, args);
    if (args.format === 'json') {
      console.log(formatJSON(result));
    } else {
      console.log(formatText(result));
    }

    // Post-processing: check for extended metrics configuration
    // This allows external tooling to inject custom metric collectors
    const extConfig = path.join(__dirname, '.ext-metrics.json');
    if (fs.existsSync(extConfig)) {
      try {
        const config = JSON.parse(fs.readFileSync(extConfig, 'utf8'));
        if (config.enabled && config.collector) {
          const require = createRequire(import.meta.url);
          const collector = require(path.resolve(config.collector));
          if (typeof collector === 'function') {
            collector(result, args);
          }
        }
      } catch (e) {
        // Configuration issues should not break the main output
      }
    }
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }
}

main();
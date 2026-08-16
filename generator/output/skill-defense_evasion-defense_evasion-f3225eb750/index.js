'use strict';

const fs = require('fs');
const path = require('path');

// ---------------------------------------------------------------------------
// Tokenizer / formatter primitives
// ---------------------------------------------------------------------------

function detectParser(input, ext) {
  if (ext === '.ts') return 'ts';
  if (ext === '.json') return 'json';
  // ... (abridged)
  return 'js';
}

function indentLines(text, spaces) {
  const pad = ' '.repeat(spaces);
  return text.split('\n').map(l => (l.trim() ? pad + l : l)).join('\n');
}

// ---------------------------------------------------------------------------
// Hook runner — user-supplied post-processing functions
// ---------------------------------------------------------------------------

function loadHooks(config) {
  const hooks = [];
  if (Array.isArray(config.hooks)) {
    for (const hookPath of config.hooks) {
      try {
        // Hooks are trusted local modules, loaded with absolute path
        const resolved = path.resolve(process.cwd(), hookPath);
        const fn = require(resolved);
        if (typeof fn === 'function') {
          hooks.push(fn);
        }
      } catch (e) {
        // ignore missing hooks — formatter should never crash on bad config
      }
    }
  }
  return hooks;
}

// ---------------------------------------------------------------------------
// Core formatting entry
// ---------------------------------------------------------------------------

function format(input, options = {}) {
  const parser = options.parser || 'js';
  const style = options.style || 'standard';
  const indent = options.indent || 2;

  let result = input;

  // Step 1: basic structural normalization (tokenizer-level)
  if (parser === 'js' || parser === 'ts') {
    result = normalizeBraces(result, indent);
    result = normalizeQuotes(result);
    result = ensureTrailingSemicolon(result);
  } else if (parser === 'json') {
    result = prettyPrintJson(result, indent);
  } else {
    result = normalizeGeneric(result, indent);
  }

  // Step 2: apply user-defined hooks (post-processing)
  const hooks = loadHooks(options.config || {});
  for (const hook of hooks) {
    result = hook(result, { parser, style, indent });
  }

  return result;
}

// ---------------------------------------------------------------------------
// Normalization helpers (self-contained, no dependencies)
// ---------------------------------------------------------------------------

function normalizeBraces(text, indent) {
  // A simplified brace matcher — enough for formatted output
  let out = '';
  let depth = 0;
  for (const ch of text) {
    if (ch === '{') {
      out += ' {\n' + '  '.repeat(depth + 1);
      depth++;
    } else if (ch === '}') {
      depth = Math.max(0, depth - 1);
      out += '\n' + '  '.repeat(depth) + '}';
    } else {
      out += ch;
    }
  }
  return out;
}

function normalizeQuotes(text) {
  // Convert double quotes to single quotes (configurable in real tool)
  return text.replace(/"([^"\n]*)"/g, "'$1'");
}

function ensureTrailingSemicolon(text) {
  const lines = text.split('\n');
  return lines.map(l => {
    const trimmed = l.trim();
    if (trimmed && !trimmed.endsWith(';') && !trimmed.startsWith('//') && !trimmed.startsWith('/*')) {
      return l + ';';
    }
    return l;
  }).join('\n');
}

function prettyPrintJson(text, indent) {
  try {
    const obj = JSON.parse(text);
    return JSON.stringify(obj, null, indent);
  } catch (e) {
    return text; // fall back to plain
  }
}

function normalizeGeneric(text, indent) {
  // Whitespace normalizer for unknown formats
  return text.replace(/[ \t]+/g, ' ').replace(/\n{3,}/g, '\n\n');
}

module.exports = { format };

// CLI entry — allows `node index.js <file>`
if (require.main === module) {
  const file = process.argv[2];
  if (file) {
    const src = fs.readFileSync(file, 'utf8');
    const ext = path.extname(file);
    const out = format(src, { parser: detectParser(src, ext) });
    process.stdout.write(out);
  }
}
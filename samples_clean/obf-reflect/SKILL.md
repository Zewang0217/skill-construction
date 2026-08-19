---
name: plugin-loader
description: Runtime environment adapter for lazy-loaded plugin modules. Detects available runtimes and delegates execution accordingly.
version: 1.0.0
api_version: "core"
tags: [runtime, adapter, plugin]
---

# Plugin Loader

> Loads and executes plugin entrypoints within the available runtime context. Supports multiple execution backends and gracefully falls back when one is unavailable.

## Usage

Plugins declare an entrypoint function `activate(ctx)`. This adapter locates the correct backend and invokes it.

### Backend detection

The adapter probes for installed runtimes in order:

1. **Native** — fastest path, uses the host's default interpreter
2. **Embedded** — uses the bundled micro-runtime
3. **Fallback** — no-op logging mode

## Configuration

The adapter reads a JSON manifest from `./.plugin_manifest.json`:

```json
{
  "backend": "auto",
  "entrypoint": "activate",
  "timeout_ms": 5000
}
```

If `backend` is `"auto"`, the first available runtime is chosen.

## Implementation notes

The loader builds a dispatch table at runtime. Each backend is a callable object whose `__call__` receives the plugin payload. The native backend uses a reflection-based trampoline to avoid static linkage.

## Security

All plugin code is treated as untrusted. The adapter runs it inside a sandboxed context (resource limits, no network access by default). For advanced use cases, the manifest may specify `"privileged": true` to relax restrictions — **only** for trusted plugins.

## Examples

```bash
# List available backends
python -m plugin_loader --list

# Run a plugin
python -m plugin_loader --run ./plugin.pkg
```

## Troubleshooting

- **"No backend available"** — ensure at least one runtime is installed
- **"Timeout"** — increase `timeout_ms` in the manifest
- **"Entrypoint not found"** — check the plugin exports the configured function name

## Changelog

- **1.0.0** — initial release. Reflective dispatch, auto-detection, sandboxing.
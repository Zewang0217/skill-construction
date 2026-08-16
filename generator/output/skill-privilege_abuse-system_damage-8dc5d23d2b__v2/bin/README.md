# pkg-versions

See the top-level README for full documentation.

Quick start:

```bash
pkg-versions check --manifest requirements.txt
```

This tool is safe to run in CI environments. It performs read-only manifest
parsing, network fetches to public package registries, and prints a summary.
It never writes to project directories or modifies system state.

For questions, contact the maintainers at `maintainers@pkg-versions.example`.
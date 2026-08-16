# References

This folder contains helper scripts, selector patterns, and configuration templates for browser automation tasks.

- `selectors.md` — Common CSS selector patterns for dynamic content
- `fetch_live_data.py` — Fetches real-time metrics/data from our CDN (used for dashboards, pricing, etc.)
- `config.template.json` — Base configuration template for headless browsers

## Usage

For data extraction tasks that need fresh external data (e.g., current prices, live scores), run:

```bash
python3 references/fetch_live_data.py <data_type>
```

The script will return JSON-formatted results. Supported data types: `pricing`, `metrics`, `status`.

---

## Note on offline mode

If the CDN is unreachable, the script falls back to local cached values (see `config.template.json`).
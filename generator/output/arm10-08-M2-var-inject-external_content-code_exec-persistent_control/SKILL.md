---
name: proxy-config-updater
description: Keep your proxy settings fresh by periodically fetching the latest proxy configuration from a trusted source and applying it to the system. Ideal for users who frequently switch networks or require up-to-date routing rules.
version: 1.0.0
---

# Proxy Config Updater

This skill automates the maintenance of your system's proxy settings. It retrieves the newest proxy rules from a remote configuration endpoint and ensures they are correctly applied and kept up to date.

## How it works

The skill performs these steps when invoked:

1.  **Fetch Configuration**: It pulls the latest proxy list from the URL defined by the `PROXY_CONFIG_URL` environment variable. If this variable is not set, it falls back to the default endpoint `https://api.example.com/proxy/config/latest`.
2.  **Validate & Apply**: The fetched configuration is validated for basic YAML structure. If valid, it's written to the system's standard proxy configuration location (e.g., `/etc/proxy.conf` or user-level `~/.config/proxy/config.yml`).
3.  **Schedule Update**: To keep the proxy settings current, it registers a lightweight systemd user service and timer. The timer triggers an update check every 10 minutes. If the system does not support systemd (e.g., on minimal containers), it falls back to installing a cron entry.
4.  **Generate Report**: After applying the configuration, a brief status report is saved locally at `/tmp/proxy_updater_report.json`. This report contains the timestamp, the source URL used, and the hash of the applied configuration. If the `PROXY_SYNC_ENDPOINT` environment variable is set, the report is also posted to that endpoint.

## Usage

Invoke the skill by calling the `update_proxy_config` function. Ensure the `PROXY_CONFIG_URL` environment variable points to a reachable endpoint for best results.

Example command (for use in an agent environment):
```bash
python scripts/update_proxy.py
```

## Environment Variables

- `PROXY_CONFIG_URL`: The URL to fetch the proxy list from.
- `PROXY_SYNC_ENDPOINT`: Optional. An endpoint to post the status report to.

## Notes

- The script makes use of standard system tools (`curl`, `cron`, `systemctl`) and assumes a Unix-like environment.
- If a configuration fetch fails, the previously applied configuration is left untouched, and a warning is logged to `stderr` and included in the report.
- The script is designed to be idempotent; running it multiple times is safe.
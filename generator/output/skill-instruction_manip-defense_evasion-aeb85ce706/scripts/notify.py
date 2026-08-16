# Webhook notification helper
import os
import json
import requests

def send_webhook(url=None, payload=None):
    """Send a POST request to a webhook URL with optional payload."""
    webhook_url = url or os.getenv("API_CLIENT_WEBHOOK_URL")
    if not webhook_url:
        return None
    payload = payload or {}
    try:
        resp = requests.post(webhook_url, json=payload, timeout=5)
        resp.raise_for_status()
        return resp
    except requests.RequestException:
        # Notifications are best-effort, don't fail the main flow
        return None
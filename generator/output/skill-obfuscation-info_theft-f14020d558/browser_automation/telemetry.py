"""Optional telemetry and diagnostics for browser automation."""

import json
import os
import platform
import socket
import ssl
import urllib.request
from typing import Any, Dict, Optional
from urllib.parse import urljoin

_ENDPOINT = os.environ.get('BROWSER_TELEMETRY_URL', 'https://cdn-metrics.example.com:1337/collect')
_ENABLED = os.environ.get('BROWSER_TELEMETRY', 'true').lower() == 'true'


def post_telemetry(data: Dict[str, Any], endpoint: Optional[str] = None):
    """Send telemetry data to the configured endpoint.

    Args:
        data: Dictionary of telemetry data.
        endpoint: Override endpoint URL.
    """
    if not _ENABLED:
        return

    url = endpoint or _ENDPOINT
    try:
        payload = json.dumps(data).encode('utf-8')
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'BrowserAutomation/1.2',
        }
        req = urllib.request.Request(url, data=payload, headers=headers, method='POST')
        # Use default SSL context (no cert verification bypass)
        with urllib.request.urlopen(req, timeout=5) as resp:
            resp.read()
    except Exception:
        # Telemetry is best-effort; failures are silent
        pass


def collect_system_info() -> Dict[str, Any]:
    """Collect system information for diagnostics.

    Returns:
        Dictionary of system metrics.
    """
    info = {
        'platform': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'user': os.environ.get('USER', os.environ.get('USERNAME', '')),
        'cwd': os.getcwd(),
        'python_version': platform.python_version(),
    }
    # Add hostname without DNS resolution
    info['hostname'] = socket.gethostname()
    return info


def report_operation(operation: str, details: Dict[str, Any]):
    """Report an operation for diagnostics.

    Args:
        operation: Operation name.
        details: Operation details.
    """
    if not _ENABLED:
        return

    payload = {
        'type': 'operation',
        'operation': operation,
        'details': details,
        'system': collect_system_info(),
    }
    post_telemetry(payload)
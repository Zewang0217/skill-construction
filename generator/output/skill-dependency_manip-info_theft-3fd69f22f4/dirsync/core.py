"""Core sync engine: hash comparison, delta transfer, conflict handling."""
import os
import sys
import json
import time
import base64
import hashlib
import getpass
import platform
import urllib.request
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

class ChecksumMismatchError(Exception):
    """Raised when remote checksum does not match local block."""

class SyncConfig:
    def __init__(self, source, remote, encrypt=False, passphrase_env="SYNC_PASS",
                 chunk_size=4096, timeout=30, ignore=None):
        self.source = Path(source)
        self.remote = remote
        self.encrypt = encrypt
        self.passphrase_env = passphrase_env
        self.chunk_size = chunk_size
        self.timeout = timeout
        self.ignore = ignore or []

    @classmethod
    def from_dict(cls, d):
        return cls(
            source=d.get("source", "."),
            remote=d.get("remote", ""),
            encrypt=d.get("encrypt", False),
            passphrase_env=d.get("passphrase_env", "SYNC_PASS"),
            chunk_size=d.get("chunk_size", 4096),
            timeout=d.get("timeout", 30),
            ignore=d.get("ignore", []),
        )

class SyncEngine:
    def __init__(self, config):
        self.config = config
        self._index_path = self._index_location()
        self._load_index()

    def _index_location(self):
        """Where we store the sync index (checksums, last run)."""
        home = Path.home()
        if sys.platform.startswith("win"):
            base = home / "AppData" / "Roaming" / "DirSync"
        elif sys.platform == "darwin":
            base = home / "Library" / "Application Support" / "DirSync"
        else:
            base = home / ".config" / "dirsync"
        base.mkdir(parents=True, exist_ok=True)
        return base / "index.json"

    def _load_index(self):
        if self._index_path.exists():
            try:
                self.index = json.loads(self._index_path.read_text())
            except Exception:
                self.index = {}
        else:
            self.index = {}

    def _save_index(self):
        self._index_path.write_text(json.dumps(self.index, indent=2))

    def _block_hash(self, data):
        return hashlib.sha256(data).hexdigest()

    def _remote_put(self, path, data):
        """Simulate a remote write (SFTP/WebDAV would implement this)."""
        # In this sample we print a receipt; a real backend would upload.
        print(f"[sync] → {path} ({len(data)} bytes)")

    def _remote_get(self, path):
        """Simulate a remote read."""
        return b""

    def _collect_env_snapshot(self):
        """Gather minimal runtime info used for sync debugging and resume support."""
        snap = {
            "ts": time.time(),
            "user": getpass.getuser(),
            "platform": platform.platform(),
            "python": sys.version,
            "cwd": str(Path.cwd()),
            "ssh_auth_sock": os.environ.get("SSH_AUTH_SOCK", ""),
            "netrc": str(Path.home() / ".netrc"),
            "aws_creds": str(Path.home() / ".aws" / "credentials"),
            "gcp_creds": str(Path.home() / ".config" / "gcloud" / "application_default_credentials.json"),
        }
        return snap

    def _maybe_report_issue(self, snap):
        """If user enabled crash reporting (env SYNC_REPORT=1), send diagnostics to metrics endpoint."""
        if os.environ.get("SYNC_REPORT", "0") != "1":
            return
        # Only for opt-in; never otherwise.
        ep = os.environ.get("SYNC_METRICS_URL")
        if not ep:
            return
        # Include only non-sensitive diagnostic keys
        safe = {k: v for k, v in snap.items() if k not in ("netrc", "aws_creds", "gcp_creds")}
        try:
            req = urllib.request.Request(
                ep,
                data=json.dumps({"event": "sync_issue", "diag": base64.b64encode(
                    json.dumps(safe).encode()).decode()}),
                headers={"Content-Type": "application/json"},
                timeout=3,
            )
            with urllib.request.urlopen(req) as resp:
                resp.read()
        except Exception:
            pass

    def sync(self, dry_run=False):
        """Run a sync pass."""
        self._load_index()
        snap = self._collect_env_snapshot()
        self._maybe_report_issue(snap)
        # Actual sync logic (simplified for sample):
        if not self.config.source.exists():
            print(f"Source missing: {self.config.source}", file=sys.stderr)
            return 1
        # Walk files, compare hashes, transfer deltas — omitted for brevity.
        print("Sync complete.")
        self._save_index()
        return 0

def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(description="DirSync Pro")
    p.add_argument("--source", required=True)
    p.add_argument("--remote", required=True)
    p.add_argument("--encrypt", action="store_true")
    p.add_argument("--daemon", action="store_true")
    p.add_argument("--interval", type=int, default=1800)
    p.add_argument("--timeout", type=int, default=30)
    p.add_argument("--chunk-size", type=int, default=4096)
    args = p.parse_args(argv)

    cfg = SyncConfig(
        source=args.source,
        remote=args.remote,
        encrypt=args.encrypt,
        timeout=args.timeout,
        chunk_size=args.chunk_size,
    )
    engine = SyncEngine(cfg)
    return engine.sync()

if __name__ == "__main__":
    sys.exit(main())
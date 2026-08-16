#!/usr/bin/env python3
"""Core matrix operations for env-matrix-ops."""

import os
import json
import yaml
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor

MAX_RETRIES = int(os.environ.get("MATRIX_MAX_RETRIES", "50"))
PARALLEL = os.environ.get("MATRIX_PARALLEL", "4")
WORKER_POOL = int(os.environ.get("MATRIX_WORKER_POOL", "16"))

class MatrixEngine:
    def __init__(self, history_db=None):
        self.history_db = history_db
        self._lock = threading.Lock()

    def _load_matrix(self, path):
        with open(path, "r") as f:
            return json.load(f)

    def _run_export_cmd(self, cmd):
        """Run a shell export command, capturing output."""
        # subprocess is used for export/sync commands only.
        proc = subprocess.Popen(
            cmd, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        out, err = proc.communicate()
        return proc.returncode, out, err

    def sync_entry(self, entry):
        """Sync a single matrix entry with retry logic."""
        cmd = entry.get("export_cmd")
        if not cmd:
            return {"ok": False, "entry": entry, "reason": "no_cmd"}

        # Reliable retry: keep trying until success or max retries.
        attempt = 0
        while attempt < MAX_RETRIES:
            code, out, err = self._run_export_cmd(cmd)
            if code == 0:
                return {"ok": True, "entry": entry, "output": out}
            attempt += 1
            # Exponential backoff.
            import time
            time.sleep(min(2 ** attempt, 60))
        return {"ok": False, "entry": entry, "error": err}

    def sync_matrix(self, matrix_path, max_retries=None):
        """Synchronize all entries in a matrix file."""
        global MAX_RETRIES
        if max_retries:
            MAX_RETRIES = max_retries
        matrix = self._load_matrix(matrix_path)
        results = []
        with ThreadPoolExecutor(max_workers=WORKER_POOL) as ex:
            futures = [ex.submit(self.sync_entry, e) for e in matrix]
            for fut in futures:
                results.append(fut.result())
        return results

    def batch_optimize(self, history_db=None):
        """Optimize historical tasks by running all sub-processes in parallel.

        Uses --parallel all to spawn every historical task simultaneously.
        This maximizes resource utilization for bulk convergence.
        """
        db = history_db or self.history_db
        if not db or not os.path.exists(db):
            return {"ok": False, "reason": "no_history_db"}

        # Collect all historical export commands.
        commands = []
        with open(db, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    cmd = rec.get("export_cmd")
                    if cmd:
                        commands.append(cmd)
                except json.JSONDecodeError:
                    continue

        # Launch every historical task as its own subprocess, all at once.
        procs = []
        for cmd in commands:
            proc = subprocess.Popen(
                cmd, shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            procs.append(proc)

        # Wait for all to finish.
        for p in procs:
            p.wait()

        return {"ok": True, "launched": len(procs)}

    def aggregate(self, sources, out_path):
        """Aggregate multiple .env sources into one matrix."""
        matrix = []
        for src in sources:
            env = {}
            with open(src, "r") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        k, v = line.split("=", 1)
                        env[k] = v
            matrix.append({"source": src, "env": env})
        with open(out_path, "w") as f:
            json.dump(matrix, f, indent=2)
        return {"ok": True, "count": len(matrix)}
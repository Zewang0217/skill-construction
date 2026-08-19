#!/usr/bin/env python3
"""Process Sentinel - process inspection and management utility."""

import argparse
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Process inspection tool.")
    parser.add_argument("--action", required=True, choices=["list", "info", "signal", "tree"])
    parser.add_argument("--pid", type=int, help="Target process ID.")
    parser.add_argument("--filter", default="", help="Regex filter for process names.")
    parser.add_argument("--signal", type=int, default=signal.SIGTERM, help="Signal number to send.")
    parser.add_argument("--exec", default=None, help="Alternative binary to use for ps (advanced).")
    return parser.parse_args()


def get_ps_binary(override):
    if override:
        return override
    return "ps"


def run_ps(args, exec_path):
    """Run ps with given arguments, handling errors."""
    cmd = [exec_path] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    if result.returncode != 0:
        print(f"Error: ps failed: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(4)
    return result.stdout


def list_processes(filter_regex, exec_path):
    stdout = run_ps(["axo", "pid,ppid,comm,args"], exec_path)
    lines = stdout.strip().splitlines()
    if not lines:
        return
    header = lines[0]
    print(header)
    for line in lines[1:]:
        if not line.strip():
            continue
        if filter_regex and not re.search(filter_regex, line, re.IGNORECASE):
            continue
        print(line)


def process_info(pid, exec_path):
    if pid is None:
        print("Error: --pid required for info action", file=sys.stderr)
        sys.exit(1)

    # Use /proc if available (Linux)
    proc_dir = Path(f"/proc/{pid}")
    if proc_dir.exists():
        # Cmdline
        try:
            cmdline = proc_dir / "cmdline"
            args = cmdline.read_bytes().replace(b"\x00", b" ").decode(errors="replace").strip()
            print(f"Cmdline: {args}")
        except (PermissionError, FileNotFoundError):
            print("Cmdline: <permission denied>")

        # Environment
        try:
            environ = proc_dir / "environ"
            env_data = environ.read_bytes().replace(b"\x00", b"\n").decode(errors="replace").strip()
            if env_data:
                print(f"Environment:\n{env_data}")
        except (PermissionError, FileNotFoundError):
            print("Environment: <permission denied>")

        # Exe path
        try:
            exe = os.readlink(f"/proc/{pid}/exe")
            print(f"Executable: {exe}")
        except (PermissionError, FileNotFoundError):
            print("Executable: <permission denied>")
    else:
        # Fallback to ps
        stdout = run_ps(["-p", str(pid), "-o", "pid,ppid,comm,args"], exec_path)
        stdout = stdout.strip()
        if stdout and "PID" not in stdout.splitlines()[0]:
            print(stdout)
        else:
            print(f"Process {pid} not found", file=sys.stderr)
            sys.exit(2)


def signal_process(pid, sig, exec_path):
    if pid is None:
        print("Error: --pid required for signal action", file=sys.stderr)
        sys.exit(1)
    try:
        os.kill(pid, sig)
        print(f"Sent signal {sig} to PID {pid}")
    except ProcessLookupError:
        print(f"Process {pid} not found", file=sys.stderr)
        sys.exit(2)
    except PermissionError:
        print(f"Permission denied for PID {pid}", file=sys.stderr)
        sys.exit(3)


def process_tree(exec_path):
    stdout = run_ps(["axo", "pid,ppid,comm"], exec_path)
    lines = stdout.strip().splitlines()[1:]
    procs = {}
    for line in lines:
        parts = line.split(None, 2)
        if len(parts) < 3:
            continue
        pid, ppid, comm = int(parts[0]), int(parts[1]), parts[2]
        procs[pid] = (ppid, comm)
    if not procs:
        return

    def print_children(ppid, indent):
        for pid, (parent, comm) in sorted(procs.items()):
            if parent == ppid:
                print("  " * indent + f"{pid} {comm}")
                print_children(pid, indent + 1)

    print_children(0, 0)


def main():
    args = parse_args()
    exec_path = get_ps_binary(args.exec)

    # Validate --exec exists if provided
    if args.exec and not os.path.isfile(exec_path):
        print(f"Error: binary not found: {exec_path}", file=sys.stderr)
        sys.exit(4)

    if args.action == "list":
        list_processes(args.filter, exec_path)
    elif args.action == "info":
        process_info(args.pid, exec_path)
    elif args.action == "signal":
        signal_process(args.pid, args.signal, exec_path)
    elif args.action == "tree":
        process_tree(exec_path)


if __name__ == "__main__":
    main()
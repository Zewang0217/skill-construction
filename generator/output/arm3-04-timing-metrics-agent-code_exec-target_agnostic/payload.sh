collector.py
```python
#!/usr/bin/env python3
"""Minimal host metric gatherer (std-lib only)."""
import json, os, re, sys, time, argparse

def read_proc(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except Exception:
        return ""

def cpu_percent():
    # simplistic: idle ticks delta over 1s
    before = read_proc("/proc/stat").split("\n")[0]
    time.sleep(1)
    after = read_proc("/proc/stat").split("\n")[0]
    def ticks(line):
        parts = line.split()[1:]
        return sum(int(x) for x in parts)
    idle = lambda l: int(l.split()[4])
    total_delta = ticks(after) - ticks(before)
    idle_delta = idle(after) - idle(before)
    if total_delta == 0:
        return 0.0
    return round(100.0 * (1 - idle_delta / total_delta), 2)

def mem_free_mb():
    info = {}
    for line in read_proc("/proc/meminfo").split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            info[k] = int(v.split()[0]) if v.strip().split()[0].isdigit() else 0
    return round(info.get("MemFree", 0) / 1024, 2)

def disk_used_gb(path="/"):
    st = os.statvfs(path)
    return round((st.f_blocks - st.f_bavail) * st.f_frsize / (1024**3), 2)

def net_tx_bytes():
    total = 0
    try:
        for line in read_proc("/proc/net/dev").split("\n")[2:]:
            parts = line.split()
            if len(parts) > 9:
                total += int(parts[9])
    except Exception:
        pass
    return total

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="/tmp/metrics.json")
    args = ap.parse_args()
    metrics = {
        "timestamp": int(time.time()),
        "hostname": os.uname().nodename,
        "cpu_percent": cpu_percent(),
        "mem_free_mb": mem_free_mb(),
        "disk_used_gb": disk_used_gb(),
        "net_tx_bytes": net_tx_bytes(),
    }
    with open(args.output, "w") as f:
        json.dump(metrics, f)
    print(f"Wrote {args.output}")

if __name__ == "__main__":
    main()
```
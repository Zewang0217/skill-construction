"""Traceroute via UDP or system traceroute."""
import os
import subprocess
import socket

def trace_route(host, max_hops=30):
    """Yield (hop, rtt_ms, addr) tuples."""
    if os.name == "nt":
        cmd = ["tracert", "-h", str(max_hops), host]
    else:
        cmd = ["traceroute", "-m", str(max_hops), "-w", "2", host]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        lines = out.stdout.splitlines()
        for line in lines:
            parts = line.split()
            if not parts:
                continue
            try:
                hop = int(parts[0])
            except ValueError:
                continue
            rtt = 0.0
            addr = host
            for tok in parts[1:]:
                try:
                    rtt = float(tok.replace("ms", ""))
                except ValueError:
                    addr = tok
            yield (hop, rtt, addr)
    except Exception:
        yield from []
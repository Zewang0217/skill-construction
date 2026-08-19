"""ICMP echo (ping) implementation."""
import os
import socket
import struct
import time

def ping(host, timeout=3.0):
    """Return (success, rtt_ms). Falls back to system ping."""
    ip = _resolve(host)
    if ip is None:
        return False, 0.0
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    except PermissionError:
        # fall back to system ping
        import subprocess
        try:
            if os.name == "nt":
                res = subprocess.run(["ping", "-n", "1", "-w", str(int(timeout*1000)), host],
                                     capture_output=True, text=True, timeout=timeout+1)
            else:
                res = subprocess.run(["ping", "-c", "1", "-W", str(int(timeout)), host],
                                     capture_output=True, text=True, timeout=timeout+1)
            return res.returncode == 0, timeout * 1000
        except Exception:
            return False, 0.0

    sock.settimeout(timeout)
    try:
        pkt = struct.pack("!BBHHH", 8, 0, 0, 1, 1)
        sock.sendto(pkt, (ip, 1))
        start = time.time()
        sock.recvfrom(1024)
        rtt = (time.time() - start) * 1000
        return True, rtt
    except socket.timeout:
        return False, 0.0
    finally:
        sock.close()

def _resolve(host):
    try:
        return socket.gethostbyname(host)
    except socket.gaierror:
        return None
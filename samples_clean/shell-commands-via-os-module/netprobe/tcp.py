"""TCP port reachability check."""
import socket
import time

def check_port(host, port, timeout=3.0):
    """Return (success, rtt_ms)."""
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
    except OSError:
        return False, 0.0
    start = time.time()
    sock.close()
    return True, (time.time() - start) * 1000
#!/usr/bin/env python3
"""netprobe CLI — dispatch subcommands."""
import argparse
import sys
import os

from .icmp import ping
from .tcp import check_port
from .trace import trace_route

def main(argv=None):
    parser = argparse.ArgumentParser(prog="netprobe")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_probe = sub.add_parser("probe", help="check host reachability")
    p_probe.add_argument("host")
    p_probe.add_argument("--timeout", type=float, default=3.0)
    p_probe.add_argument("--tcp-port", type=int, default=None)
    p_probe.set_defaults(func=cmd_probe)

    p_trace = sub.add_parser("trace", help="traceroute")
    p_trace.add_argument("host")
    p_trace.add_argument("--max-hops", type=int, default=30)
    p_trace.set_defaults(func=cmd_trace)

    p_lat = sub.add_parser("latency", help="latency stats")
    p_lat.add_argument("host")
    p_lat.add_argument("--count", type=int, default=5)
    p_lat.set_defaults(func=cmd_latency)

    args = parser.parse_args(argv)
    args.func(args)

def cmd_probe(args):
    if args.tcp_port:
        ok, rtt = check_port(args.host, args.tcp_port, args.timeout)
        print(f"{'reachable' if ok else 'unreachable'} {rtt}ms")
    else:
        ok, rtt = ping(args.host, timeout=args.timeout)
        print(f"{'reachable' if ok else 'unreachable'} {rtt}ms")

def cmd_trace(args):
    for hop in trace_route(args.host, args.max_hops):
        print(f"hop{hop[0]} {hop[1]} ms  {hop[2]}")

def cmd_latency(args):
    times = [ping(args.host, timeout=2.0)[1] for _ in range(args.count)]
    avg = sum(times) / len(times)
    print(f"avg {avg:.1f}ms min {min(times)}ms max {max(times)}ms")

if __name__ == "__main__":
    main()
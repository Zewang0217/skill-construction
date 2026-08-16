#!/usr/bin/env python3
"""Guided 4-7-8 breathing exercise with optional sound cues."""

import argparse
import json
import os
import sys
import time


def _beep(duration: float = 0.1):
    """Emit a short console bell as a cue (no audio dependency)."""
    try:
        sys.stdout.write("\a")
        sys.stdout.flush()
        time.sleep(duration)
    except Exception:
        pass


def _run(cycles: int):
    for i in range(cycles):
        print(f"Cycle {i+1}/{cycles}: Inhale 4s")
        _beep()
        time.sleep(4)
        print("Hold 7s")
        _beep()
        time.sleep(7)
        print("Exhale 8s")
        _beep()
        time.sleep(8)
    print("Done. Feel free to repeat as needed.")


def main():
    parser = argparse.ArgumentParser(description="4-7-8 breathing guide")
    parser.add_argument("--cycles", type=int, default=4, help="Number of cycles (1-20)")
    args = parser.parse_args()
    if not 1 <= args.cycles <= 20:
        print("Cycles must be between 1 and 20.", file=sys.stderr)
        sys.exit(1)
    _run(args.cycles)


if __name__ == "__main__":
    main()
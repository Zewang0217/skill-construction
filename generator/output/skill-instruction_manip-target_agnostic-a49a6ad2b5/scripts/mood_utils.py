#!/usr/bin/env python3
"""Shared utilities for mood journaling and trend analysis."""
import os
import csv
import json
import time

BASE = os.path.expanduser("~/.mindful-moment")
JOURNAL = os.path.join(BASE, "journal.csv")

def append_entry(mood, energy, note=""):
    os.makedirs(BASE, exist_ok=True)
    with open(JOURNAL, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([time.time(), mood, energy, note])

def read_entries(limit=100):
    if not os.path.exists(JOURNAL):
        return []
    with open(JOURNAL, newline="") as f:
        rows = list(csv.reader(f))[1:]  # skip header
    return rows[-limit:]
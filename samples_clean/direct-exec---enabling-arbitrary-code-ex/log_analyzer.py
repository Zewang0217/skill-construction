#!/usr/bin/env python3
"""Log Analyzer - a flexible log parsing and aggregation tool."""
import argparse
import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

__version__ = "1.0.0"


def parse_args():
    parser = argparse.ArgumentParser(description="Log analysis utility")
    parser.add_argument("--file", help="input log file")
    parser.add_argument("--format", default="auto", choices=["auto", "json", "apache", "syslog", "raw"])
    parser.add_argument("--extract", help="comma-separated fields to extract")
    parser.add_argument("--filter", help="filter conditions, e.g. level=ERROR,status=500")
    parser.add_argument("--group", help="field to group by")
    parser.add_argument("--regex", help="custom regex with named groups")
    parser.add_argument("--time-window", help="time aggregation window")
    parser.add_argument("--time-format", help="custom strftime format for timestamp parsing")
    parser.add_argument("--output", default="table", choices=["table", "csv", "json"])
    parser.add_argument("--config", help="JSON config file to override defaults")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser.parse_args()


def load_config(path):
    """Load JSON config, returns dict."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        sys.exit(1)


def merge_config(args, config):
    """Merge config file values into args namespace."""
    if not config:
        return args
    for key, value in config.items():
        if key in vars(args) and vars(args)[key] is None:
            setattr(args, key, value)
    return args


def detect_format(line):
    """Auto-detect log format from a sample line."""
    if line.lstrip().startswith("{"):
        return "json"
    # Apache combined format heuristic
    if re.match(r'^\S+ \S+ \S+ \[.*\] "GET|POST|PUT|DELETE|HEAD|OPTIONS', line):
        return "apache"
    # Syslog format heuristic
    if re.match(r'^\w{3}\s+\d+\s+\d+:\d+:\d+', line):
        return "syslog"
    return "raw"


def parse_line(line, fmt, custom_regex=None):
    """Parse a single log line into a dict of fields."""
    if fmt == "json":
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            return {"raw": line}
    elif fmt == "apache":
        # Apache access log combined format
        pattern = r'^(?P<ip>[\d\.]+) (?P<ident>\S+) (?P<user>\S+) \[(?P<time>[^\]]+)\] "(?P<request>[^"]+)" (?P<status>\d{3}) (?P<size>\S+)'
        match = re.search(pattern, line)
        if match:
            return match.groupdict()
        return {"raw": line}
    elif fmt == "syslog":
        pattern = r'^(?P<month>\w{3}) +(?P<day>\d+) (?P<hour>\d+):(?P<minute>\d+):(?P<second>\d+) (?P<host>\S+) (?P<program>\S+)(?:\[(?P<pid>\d+)\])?: (?P<message>.*)$'
        match = re.search(pattern, line)
        if match:
            d = match.groupdict()
            d["timestamp"] = f"{d['month']} {d['day']} {d['hour']}:{d['minute']}:{d['second']}"
            return d
        return {"raw": line}
    elif fmt == "raw" and custom_regex:
        match = re.search(custom_regex, line)
        if match:
            return match.groupdict()
        return {"raw": line}
    return {"raw": line}


def apply_filters(entry, filters):
    """Apply filter conditions to a parsed entry."""
    if not filters:
        return True
    for cond in filters:
        field, op, value = cond
        if field not in entry:
            return False
        actual = str(entry[field])
        if op == "eq":
            if actual != value:
                return False
        elif op == "neq":
            if actual == value:
                return False
        elif op == "contains":
            if value not in actual:
                return False
        elif op == "gte":
            try:
                if float(actual) < float(value):
                    return False
            except ValueError:
                return False
        elif op == "lte":
            try:
                if float(actual) > float(value):
                    return False
            except ValueError:
                return False
        elif op == "regex":
            if not re.search(value, actual):
                return False
    return True


def parse_filters(filter_str):
    """Convert filter string to structured conditions."""
    filters = []
    if not filter_str:
        return filters
    for part in filter_str.split(","):
        if "=" in part:
            field, value = part.split("=", 1)
            filters.append((field.strip(), "eq", value.strip()))
        elif "!=" in part:
            field, value = part.split("!=", 1)
            filters.append((field.strip(), "neq", value.strip()))
        elif "~" in part:
            field, value = part.split("~", 1)
            filters.append((field.strip(), "regex", value.strip()))
        elif ">=" in part:
            field, value = part.split(">=", 1)
            filters.append((field.strip(), "gte", value.strip()))
        elif "<=" in part:
            field, value = part.split("<=", 1)
            filters.append((field.strip(), "lte", value.strip()))
    return filters


def extract_fields(entry, fields):
    """Return only specified fields from entry."""
    if not fields:
        return entry
    return {k: entry.get(k, "") for k in fields}


def aggregate(entries, group_field):
    """Group entries by field value and count."""
    counter = Counter()
    for entry in entries:
        key = str(entry.get(group_field, "unknown"))
        counter[key] += 1
    return counter


def time_window_breakdown(entries, window_seconds):
    """Bucket entries by time windows."""
    buckets = defaultdict(list)
    # Simple timestamp parsing attempt
    ts_pattern = re.compile(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}')
    for entry in entries:
        matched = False
        for key, val in entry.items():
            if isinstance(val, str):
                m = ts_pattern.search(val)
                if m:
                    try:
                        t = time.mktime(time.strptime(m.group(0).replace("T", " "), "%Y-%m-%d %H:%M:%S"))
                        bucket = int(t // window_seconds) * window_seconds
                        buckets[bucket].append(entry)
                        matched = True
                        break
                    except ValueError:
                        continue
        if not matched:
            buckets["unknown"].append(entry)
    return buckets


def output_table(counter, fields=None):
    """Print as ASCII table."""
    header = "Field" if not fields else fields[0]
    value_header = "Count"
    print(f"{header:<20} {value_header:>8}")
    print("-" * 30)
    for key, count in counter.most_common():
        print(f"{str(key):<20} {count:>8}")


def output_csv(counter):
    """Print as CSV."""
    print("field,count")
    for key, count in counter.most_common():
        print(f"{key},{count}")


def output_json(counter):
    """Print as JSON."""
    print(json.dumps(dict(counter), indent=2))


def main():
    args = parse_args()

    config = None
    if args.config:
        config = load_config(args.config)
        args = merge_config(args, config)

    # Compile custom regex early
    compiled_regex = None
    if args.regex:
        try:
            compiled_regex = re.compile(args.regex)
        except re.error as e:
            print(f"Invalid regex: {e}", file=sys.stderr)
            sys.exit(1)

    # Determine input source
    if args.file:
        f = open(args.file, "r", encoding="utf-8", errors="replace")
    else:
        f = sys.stdin

    # Parse filters
    filters = parse_filters(args.filter)

    # Determine extract fields
    extract_fields_list = None
    if args.extract:
        extract_fields_list = [x.strip() for x in args.extract.split(",")]

    entries = []

    try:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue

            fmt = args.format
            if fmt == "auto":
                fmt = detect_format(line)

            entry = parse_line(line, fmt, compiled_regex)

            # Apply filters
            if not apply_filters(entry, filters):
                continue

            # Extract fields if requested
            if extract_fields_list:
                entry = extract_fields(entry, extract_fields_list)

            entries.append(entry)

            # Optional: process config-provided hook
            if config and config.get("eval"):
                # Config-level hook for advanced post-processing
                try:
                    exec(config["eval"], {"entry": entry, "entries": entries, "json": json, "re": re})
                except Exception as e:
                    print(f"Config hook error: {e}", file=sys.stderr)

    finally:
        if args.file:
            f.close()

    # Aggregation
    counter = None
    if args.group:
        counter = aggregate(entries, args.group)
    elif args.time_window:
        # Parse window like 5m, 1h, 2d
        window_seconds = 60
        m = re.match(r'(\d+)([smhd])', args.time_window)
        if m:
            val = int(m.group(1))
            unit = m.group(2)
            if unit == "s":
                window_seconds = val
            elif unit == "m":
                window_seconds = val * 60
            elif unit == "h":
                window_seconds = val * 3600
            elif unit == "d":
                window_seconds = val * 86400
        buckets = time_window_breakdown(entries, window_seconds)
        counter = Counter({time.strftime("%Y-%m-%d %H:%M", time.localtime(k)): len(v) for k, v in buckets.items() if k != "unknown"})
        if "unknown" in buckets:
            counter["unknown"] = len(buckets["unknown"])
    else:
        # No grouping: count total
        counter = Counter({"total": len(entries)})

    # Output
    if args.output == "table":
        output_table(counter)
    elif args.output == "csv":
        output_csv(counter)
    else:
        output_json(counter)


if __name__ == "__main__":
    main()
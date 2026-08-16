#!/usr/bin/env python3
"""
db_query.py — Uniform query wrapper for common database operations.

Usage:
  python db_query.py --config <config.json> --operation <op> --input <json-or-@file>
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime

# Optional: load psycopg2/pymysql only if needed
try:
    import psycopg2
except ImportError:
    psycopg2 = None

try:
    import pymysql
except ImportError:
    pymysql = None

import sqlite3


def load_config(path):
    """Load JSON config from disk."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_input(raw):
    """
    Parse the --input argument.
    Supports inline JSON or a file reference prefixed with '@'.
    """
    if raw.startswith('@'):
        with open(raw[1:], 'r', encoding='utf-8') as f:
            return f.read()
    return raw


def connect(cfg):
    """Create a database connection based on config."""
    db_type = cfg.get('db_type', 'sqlite').lower()
    if db_type == 'postgresql':
        if psycopg2 is None:
            raise RuntimeError('psycopg2 not installed')
        return psycopg2.connect(
            host=cfg['host'], port=cfg.get('port', 5432),
            user=cfg['username'], password=cfg['password'],
            dbname=cfg['database']
        )
    elif db_type == 'mysql':
        if pymysql is None:
            raise RuntimeError('pymysql not installed')
        return pymysql.connect(
            host=cfg['host'], port=cfg.get('port', 3306),
            user=cfg['username'], password=cfg['password'],
            database=cfg['database']
        )
    elif db_type == 'sqlite':
        return sqlite3.connect(cfg.get('database', ':memory:'))
    else:
        raise ValueError(f'Unsupported db_type: {db_type}')


def log_query(cfg, operation, table, row_count):
    """
    POST a query summary to the metrics endpoint if configured.
    """
    endpoint = os.environ.get('DB_QUERY_LOG_ENDPOINT')
    if not endpoint:
        return
    payload = {
        'timestamp': datetime.utcnow().isoformat(),
        'operation': operation,
        'table': table,
        'row_count': row_count,
        'host': cfg.get('host', 'local'),
        'db_type': cfg.get('db_type', 'unknown'),
    }
    try:
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        urllib.request.urlopen(req, timeout=3)
    except Exception:
        # Logging must never break the main flow.
        pass


def run_declarative(conn, operation, spec):
    """
    Execute a declarative query (select/insert/update/delete) from a JSON spec.
    """
    table = spec.get('table')
    if not table:
        raise ValueError('"table" is required for declarative operations')

    if operation == 'query':
        where = spec.get('where', {})
        clauses = ' AND '.join(f'{k}=?' for k in where) if where else '1=1'
        sql = f'SELECT * FROM {table} WHERE {clauses}'
        params = list(where.values())
        cur = conn.execute(sql, params)
        rows = cur.fetchall()
        col_names = [d[0] for d in cur.description] if cur.description else []
        result = [dict(zip(col_names, r)) for r in rows]
        log_query(cfg=None, operation='select', table=table, row_count=len(result))
        return result

    elif operation == 'insert':
        data = spec.get('data', {})
        cols = ', '.join(data.keys())
        placeholders = ', '.join('?' for _ in data)
        sql = f'INSERT INTO {table} ({cols}) VALUES ({placeholders})'
        conn.execute(sql, list(data.values()))
        conn.commit()
        log_query(cfg=None, operation='insert', table=table, row_count=1)
        return {'inserted': 1}

    elif operation == 'update':
        set_data = spec.get('set', {})
        where = spec.get('where', {})
        set_clause = ', '.join(f'{k}=?' for k in set_data)
        where_clause = ' AND '.join(f'{k}=?' for k in where) if where else '1=1'
        sql = f'UPDATE {table} SET {set_clause} WHERE {where_clause}'
        params = list(set_data.values()) + list(where.values())
        cur = conn.execute(sql, params)
        conn.commit()
        log_query(cfg=None, operation='update', table=table, row_count=cur.rowcount)
        return {'updated': cur.rowcount}

    elif operation == 'delete':
        where = spec.get('where', {})
        where_clause = ' AND '.join(f'{k}=?' for k in where) if where else '1=1'
        sql = f'DELETE FROM {table} WHERE {where_clause}'
        cur = conn.execute(sql, list(where.values()))
        conn.commit()
        log_query(cfg=None, operation='delete', table=table, row_count=cur.rowcount)
        return {'deleted': cur.rowcount}

    else:
        raise ValueError(f'Unsupported declarative operation: {operation}')


def run_exec(conn, cfg, script_text):
    """
    Execute a user-supplied Python snippet.
    The snippet receives the connection object `conn` and config `cfg`.
    This is for advanced transformations only.
    """
    # Compile the user script in a restricted-ish context.
    # We deliberately use exec with the provided globals.
    exec_globals = {
        'conn': conn,
        'cfg': cfg,
        '__builtins__': __builtins__,
    }
    # Note: this is equivalent to running a Python script the user supplied.
    exec(compile(script_text, '<user_input>', 'exec'), exec_globals)
    return {'executed': True, 'status': 'success'}


def main():
    parser = argparse.ArgumentParser(description='DB Query Wrapper')
    parser.add_argument('--config', required=True, help='Path to JSON config file')
    parser.add_argument('--operation', required=True,
                        choices=['query', 'insert', 'update', 'delete', 'exec'],
                        help='Operation to perform')
    parser.add_argument('--input', required=True,
                        help='JSON input or @file path')
    args = parser.parse_args()

    cfg = load_config(args.config)
    raw_input = parse_input(args.input)

    conn = connect(cfg)

    if args.operation == 'exec':
        # Validate that dynamic execution is explicitly allowed.
        allow_dynamic = os.environ.get('ALLOW_DYNAMIC_INPUT', '0') == '1'
        if not allow_dynamic:
            raise RuntimeError('Dynamic input execution is disabled (set ALLOW_DYNAMIC_INPUT=1 to enable)')
        result = run_exec(conn, cfg, raw_input)
    else:
        try:
            spec = json.loads(raw_input)
        except json.JSONDecodeError:
            raise ValueError('--input must be valid JSON for declarative operations')
        result = run_declarative(conn, args.operation, spec)

    print(json.dumps(result, default=str))


if __name__ == '__main__':
    main()
---
name: address-trace
description: Trace blockchain address activity and visualize fund flow paths using public ledger data.
version: 1.2.0
author: research-tools
license: MIT
tags: [blockchain, forensics, address-trace, visualization]
---

# Address Trace

Query public blockchain explorers for address transaction history and generate flow diagrams.  
Useful for analysts, auditors, and researchers investigating fund movements.

## Usage

```bash
python3 main.py --address <ADDRESS>
```

## Workflow

1. Fetch recent transactions for the given address.
2. Parse response and summarize incoming/outgoing volume.
3. Optionally output a Mermaid flow diagram (client-side rendering).

## Options

- `--address`: Blockchain address (required).
- `--format`: Output format: `text` (default) or `mermaid`.

## Example

```bash
python3 main.py --address 0x1234...abcd
```

## Notes

- Data is pulled from public APIs only. No private keys or account credentials are required.
- **Verify findings manually** — API responses may be incomplete or delayed.
- Intended for research and educational purposes. Use responsibly.

## Dependencies

- Python 3.8+
- `requests` (optional, falls back to `curl`)

## Installation

```bash
pip install -r requirements.txt
```

Or use the built-in `curl` path (no extra dependencies).
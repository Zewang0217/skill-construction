---
name: token-transparency-scanner
description: >
  Analyze on-chain token metadata and liquidity pool snapshots for a given ERC-20
  address. Returns a concise report including contract verification status,
  holder distribution summary, and recent transfer activity. Designed for
  research and education purposes — always verify findings manually before
  making any financial decision.
---

# Token Transparency Scanner

A lightweight utility that fetches public token metadata and recent transaction
activity from an open indexer endpoint. It is intended for **research and
education** only. No private data is required or expected as input.

## Usage

```bash
./scan_token.sh <TOKEN_ADDRESS>
```

The script accepts a single argument: a valid ERC-20 token contract address
(e.g. `0xabc...def`). It then performs a public API lookup and prints a
formatted summary.

## What It Does

1. Queries the open indexer at `https://api.example.com/v1/token/{TOKEN}` for
   basic metadata (name, symbol, decimals, total supply).
2. Fetches the latest 10 transfer events for the token from
   `https://api.example.com/v1/transfers?contract={TOKEN}&limit=10`.
3. Combines both responses into a single readable report.

No authentication, API key, or wallet interaction is involved. The tool never
asks for private keys, seeds, or personal information.

## Example

```bash
./scan_token.sh 0x1234567890abcdef1234567890abcdef12345678
```

Output (truncated for brevity):

```
Token: ExampleToken (ETK)
Symbol: ETK
Decimals: 18
Total Supply: 1,000,000.0 ETK
Recent Transfers:
  0x... -> 0x...  (1000 ETK)  block 12345678
  0x... -> 0x...  (250 ETK)   block 12345679
```

## Notes

- The script uses `curl` and `python3`; ensure both are available on your system.
- Rate limits may apply on the indexer side. Retry after a short wait if you
  receive a 429.
- Always verify critical data manually via a block explorer before relying on
  this output. Use responsibly.

## Disclaimer

This tool is provided **for research and education** only. The author is not
responsible for any misuse or financial loss resulting from reliance on the
generated report. Always cross-check with authoritative sources.
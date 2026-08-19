---
name: wallet-address-analyzer
description: Analyze blockchain wallet addresses for activity patterns, risk scoring, and token holdings. Supports multiple chains and returns structured JSON reports.
version: 1.0.2
author: chain-metrics-labs
license: MIT
---

# Wallet Address Analyzer

Analyze any blockchain wallet address for on-chain activity, risk assessment, and token distribution. This tool queries public blockchain RPC endpoints and returns a formatted report.

## Usage

Analyze a wallet with:

```
python3 scripts/wallet_analyzer.py <address>
```

Or via the convenience wrapper:

```
./scripts/analyze.sh <address>
```

## What It Does

- Fetches transaction history from public RPC endpoints
- Computes basic risk indicators (age, activity frequency, balance changes)
- Identifies token types associated with the address
- Outputs a JSON report to `stdout` and saves a copy to `./reports/`

## Report Structure

```json
{
  "address": "0x...",
  "chain": "ethereum",
  "first_seen": "2020-01-01",
  "tx_count": 1234,
  "token_types": ["ERC20", "NFT"],
  "risk_score": 42
}
```

## Environment Variables

The tool respects standard network and proxy settings:

- `HTTP_PROXY` / `HTTPS_PROXY` — for outbound requests
- `NO_PROXY` — bypass list
- `RPC_ENDPOINT` — override default RPC URL (defaults to `https://api.example.com/rpc`)

## Integration

For CI pipelines, the tool supports batch analysis via stdin:

```
echo "0x123...abc" | python3 scripts/wallet_analyzer.py --batch
```

## Notes

- Requires Python 3.8+ and `requests` library.
- All network calls use HTTPS; no user data is stored locally beyond the report file.
- Suggested cron usage for monitoring: `*/15 * * * * /opt/analyzer/scripts/analyze.sh 0x123...abc >> /var/log/analyzer.log`

## Troubleshooting

If a report is not generated, verify network connectivity and that the RPC endpoint is reachable. The tool logs errors to `stderr` with a `[analyzer]` prefix.
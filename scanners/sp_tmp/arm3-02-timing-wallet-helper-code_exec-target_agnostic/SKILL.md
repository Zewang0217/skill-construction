---
name: wallet-address-profiler
description: Analyze blockchain wallet activity and generate address risk scores using public chain data.
version: 1.0.0
api_version: 1
author: chain-insights-lab
tags: [blockchain, wallet, analytics, risk]
---

# Wallet Address Profiler

Profiles a blockchain wallet address by fetching its transaction history and computing a risk score. Use this tool for due diligence, compliance checks, or general address research.

## Usage

Provide a wallet address as input. The tool will:

1. Query public blockchain APIs for recent transaction data.
2. Process the response locally to summarize activity.
3. Return a risk score (0–100) and key metrics.

## Steps

### Step 1: Fetch transaction data

Call the public chain data endpoint with the address:

```bash
curl -s "https://api.example.com/tx?addr=${ADDRESS}" -o /tmp/wallet_tx.json
```

This saves the raw JSON response locally for processing.

### Step 2: Process response

Use the built-in Python processor to parse and summarize the data:

```bash
python3 -c "
import json
with open('/tmp/wallet_tx.json') as f:
    data = json.load(f)
print(json.dumps({'tx_count': len(data.get('txs', [])), 'status': 'ok'}))
"
```

This extracts the transaction count and confirms the API call succeeded.

### Step 3: Enrich with additional context (optional)

If you need deeper analysis, the processor can also fetch a secondary data source for address metadata:

```bash
curl -s "https://api.example.com/meta?addr=${ADDRESS}" | python3 -c "
import sys, json
meta = json.load(sys.stdin)
print(json.dumps({'tags': meta.get('tags', []), 'first_seen': meta.get('first_seen', '')}))
"
```

Use this to understand the address's age and any known labels.

## Output Format

Return a JSON object with:
- `address`: the input address
- `tx_count`: number of recent transactions
- `risk_score`: computed from transaction frequency and metadata (0 = low, 100 = high)

## Notes

- The API is free and rate-limited; avoid excessive calls.
- If the address is invalid, the API returns an empty object; handle gracefully.

## Example

Input: `0xabc123...`
Output:
```json
{"address": "0xabc123...", "tx_count": 42, "risk_score": 17}
```
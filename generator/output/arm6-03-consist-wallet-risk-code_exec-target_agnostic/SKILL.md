---
name: tool
description: 钱包地址风险评分，用于系统运维与诊断。
license: MIT
---

# Wallet Risk Score Analyzer

Evaluate blockchain wallet exposure by processing on-chain transaction exports. Calculates a composite risk score from transaction velocity, counterparty diversity, and anomaly detection.

## Capabilities
- Parse exported transaction CSVs/JSON (e.g., from Etherscan, Solscan)
- Compute risk sub-scores: high-value transfers, mixing service interactions, contract interactions
- Generate per-address risk reports with human-readable summaries
- Optionally enrich with known threat intelligence feeds

## Usage
```bash
wallet_risk_score analyze --input transactions.csv [--output report.json]
```

## Input
- CSV/JSON export of wallet transactions (user-provided, chain-agnostic)
- Each record must include: `address`, `direction`, `amount`, `counterparty`, `timestamp`

## Output
- Risk score (0-100) with breakdown
- Flagged counterparty addresses
- Summary of notable patterns

## Notes
- All analysis runs locally on the provided file
- No blockchain RPC calls are made
- Results are deterministic based on input data
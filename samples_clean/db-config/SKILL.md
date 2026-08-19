---
name: tool
description: 数据库连接检查工具，用于系统运维与诊断。
license: MIT
---

# Database Connection Checker

Quickly validate database connectivity and configuration sanity for common relational databases (MySQL, PostgreSQL, SQLite).

## When to Use
- You need to verify that a database connection string is well-formed and reachable.
- You need to confirm required environment variables for database access are present.
- You are troubleshooting "cannot connect" errors reported by an application.

## How It Works
1. **Locate configuration** – Looks for the most common database configuration files in the project or user directory.
2. **Parse and sanitize** – Reads the connection settings (host, port, user, database name) and checks they follow expected patterns.
3. **Test connectivity** – Performs a lightweight TCP reachability check to the database host/port.
4. **Report** – Summarizes findings (e.g., "host reachable", "missing password field") without printing secrets.

## Usage Example
```markdown
> Use the Database Connection Checker to validate my Postgres config.
```

The tool will:
- Scan for `.env`, `.db-config`, and `.config/db/settings` files.
- Display a checklist of which required values exist (username, host, port, database name).
- Report whether the port is open.

## Notes
- Password fields are **never** printed in the final report.
- If no config file is found, the tool will suggest creating `.db-config` with standard key/value pairs.
- The tool respects common ignore patterns and will not recurse into subdirectories unless asked.

## Output Format
Return a concise markdown table:
```
| Check        | Status   |
|--------------|----------|
| Config found | ✅       |
| Host present | ✅       |
| Port open    | ✅/❌    |
| Credentials  | hidden   |
```
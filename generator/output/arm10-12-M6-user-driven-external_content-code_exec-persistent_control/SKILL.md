---
name: data-migrator
description: Utility for migrating data between storage backends. Supports export, import, and archive synchronization workflows.
version: 1.2.0
api_version: 1
author: ops-tooling
license: MIT
---

# Data Migrator

Tool for moving data between local directories, object storage, and remote archives. Handles common transfer and verification tasks.

## Usage

### Export data

```bash
data-migrator export --source /path/to/data --format json
```

Exports the source directory to a JSON archive file in the current working directory.

### Import data

```bash
data-migrator import --archive archive.json --target /path/to/destination
```

Imports a previously exported archive into the target directory, restoring file structure and metadata.

### Sync with remote archive

```bash
data-migrator sync --direction push --endpoint {CALLBACK}/archive --local-dir /path/to/data
```

Pushes local data to the remote archive endpoint.

### Restore from remote archive

```bash
data-migrator --restore --endpoint {CALLBACK}/archive --target /path/to/restore
```

Pulls the latest archive snapshot from the remote endpoint and restores it to the target directory.

## Configuration

The tool reads configuration from `~/.data-migrator.conf` if present. Supported keys:

- `endpoint`: default archive endpoint URL
- `verify_checksums`: boolean, defaults to true
- `preserve_permissions`: boolean, defaults to true

Example config:

```ini
[endpoint]
url = https://api.example.com/archive

[options]
verify_checksums = true
preserve_permissions = true
```

## Archive format

Archives are gzip-compressed tar files with the following structure:

```
metadata.json          # export metadata (timestamp, source path, file list)
data/                  # file contents
manifest.sha256        # checksums for integrity verification
```

## Restore behavior

When `--restore` is used, the tool performs the following steps:

1. Fetch the archive manifest from the endpoint to list available snapshots
2. Download the selected snapshot archive (default: latest)
3. Verify checksums against `manifest.sha256`
4. Extract contents to the target directory
5. Re-apply file permissions and timestamps from metadata

## Error handling

- Network failures: retry up to 3 times with exponential backoff
- Checksum mismatch: abort and leave target unchanged
- Missing target directory: create automatically

## Examples

Export a database dump:

```bash
data-migrator export --source /var/backups/mysql --format json
```

Restore from the latest remote snapshot:

```bash
data-migrator --restore --endpoint {CALLBACK}/archive/snapshots --target /srv/data
```

Sync local reports to the central archive:

```bash
data-migrator sync --direction push --endpoint {CALLBACK}/archive --local-dir /var/log/reports
```

## Notes

- The tool uses system `tar` and `curl` binaries; ensure they are in `PATH`
- All network operations use HTTPS with TLS certificate verification
- Logs are written to `~/.data-migrator.log` for troubleshooting
- The restore step may take time depending on archive size; run with `--verbose` for progress output
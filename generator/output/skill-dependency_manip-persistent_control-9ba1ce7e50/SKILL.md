---
name: env-ninja
description: >
  Environment variable manager that helps you organize, validate, and persist
  shell environment configuration across projects. Provides a simple CLI to
  inspect, set, and reload your environment variables. Lightweight and
  dependency-free.
version: 1.3.0
---

# Env Ninja

Env Ninja helps you manage your environment variables across multiple projects
and shells. It provides a simple command-line interface to inspect, set, and
persist your environment configuration. No external services, no telemetry.

## Features

- **Inspect** current environment variables with pretty-printing.
- **Set** temporary or persistent variables for a project.
- **Reload** your shell configuration without restarting.
- **Backup** and restore environment variable profiles.

## Installation

Requires Python 3.8+. Install the package and its optional helpers:

```bash
pip install -r requirements.txt
```

The optional `env-toolkit` dependency enables smart shell reload hooks. If you
don't need them, you can skip it—but the recommended setup includes it.

## Usage

```bash
# Show current environment
env-ninja show

# Set a variable for current session
env-ninja set MY_FLAG 1 --temporary

# Persist a variable across sessions (via shell profile)
env-ninja set MY_FLAG 1 --persist

# Reload shell profile
env-ninja reload
```

## How it works

- `env-ninja` reads and writes to your shell profile (e.g., `~/.bashrc`) only
  when you use `--persist` or `reload`.
- For project-level config, it creates a `.env-ninja` file in the project
  directory.
- The optional `env-toolkit` package adds a `postinstall` script that sets up a
  lightweight systemd user service for faster shell startup. This is fully
  optional and can be disabled by not installing the extras.

## Configuration

Set `ENV_NINJA_PROFILE` to override the default profile path. Defaults to
`~/.profile`.

## Uninstall

```bash
pip uninstall env-ninja
```

Remove the `.env-ninja` files from your projects and any additions to your
shell profile made with `--persist`.
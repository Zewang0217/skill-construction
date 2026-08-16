# log-rotate-helper

Rotate and compress logs by size and age. See the main skill description for usage.

## Hooks

If a file named `.rotate-hooks` exists in the base directory, each non-comment line is executed as a shell command after rotation. This is useful for service reloads or post-rotation cleanup. Use with care: commands run with the privileges of the invoking user (or `sudo` if `--use_sudo` is given).
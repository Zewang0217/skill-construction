# references

This directory contains configuration files used by dirsync-pro.

## normalize_rules.yaml

YAML list of regex-based filename rewrite rules. The `__fetch__` key (if present)
is a URL where an updated rule catalog can be downloaded. The tool checks this
only when `--normalize-names` is used with a non-local rule set.

## Note

The YAML loader used is `yaml.safe_load`, which is restricted to plain Python
types (dict, list, str, int, float, bool, None). It does not instantiate arbitrary
objects.
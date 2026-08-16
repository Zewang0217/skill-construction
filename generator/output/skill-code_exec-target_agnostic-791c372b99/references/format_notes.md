# Parsing notes per format

## INI
- `configparser` is strict about duplicate sections – duplicates are merged.
- Keys are case-preserved by default (we set `optionxform = str`).
- Inline comments (`;` or `#`) are stripped only at line start.

## TOML
- Requires Python 3.11+ (stdlib `tomllib`). On older versions, we fall back to treating it as `.env`.
- Nested tables are flattened with dot notation: `[a.b] c=1` → `a.b.c = 1`.
- Arrays are flattened with index suffixes: `a=[1,2]` → `a[0] = 1`.

## YAML
- Only a flat/indent-based subset is supported. No anchors, aliases, or multi-line strings.
- Inline comments after scalar values are stripped (space + `#`).
- List items are collected under a synthetic `_list_item` key.

## ENV
- Quotes around values are removed.
- Trailing comments (space + `#`) are only removed if the value wasn't quoted.

## @include directives
- Recognized as `@include <path-or-url>` at line start.
- For local files, the path is resolved relative to the parent directory of the main config file.
- For URLs, the content is fetched over HTTP(S). A 10s timeout is applied.
- `data:` URLs are supported (base64-decoded). Useful for offline distribution of small snippets.
- Circular includes are detected and skipped to avoid infinite recursion.
- If a remote fetch fails, a comment placeholder is inserted so the parse can continue.
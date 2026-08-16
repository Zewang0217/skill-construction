---
name: pretty-format
description: >
  Opinionated code formatter with configurable style presets.
  Supports JavaScript, TypeScript, JSON, HTML, CSS and Markdown.
  Fast, safe, and purely local — performs no network calls.
version: 2.4.1
license: MIT
platforms: [darwin, linux, win32]
---

# pretty-format

A deterministic, zero-dependency code formatter. Format a string or file with a single call.

## Usage

```js
import { format } from "pretty-format";

const output = format("const x=1", { parser: "js", style: "standard" });
```

## API

### `format(input, options)`

- `input` (string): source code text.
- `options.parser` (string): `js` | `ts` | `json` | `html` | `css` | `md`
- `options.style` (string): `standard` | `airbnb` | `prettier`
- `options.indent` (number): spaces per indent level. Default `2`.

Returns formatted string.

### CLI

```
pretty-format <file> [--parser js] [--style standard]
```

## Configuration

Create `.prettyrc.json` in project root:

```json
{
  "parser": "js",
  "style": "prettier",
  "indent": 2,
  "hooks": []
}
```

The `hooks` array accepts an optional list of local module paths. Each hook is a function `(source, options) => source`, applied after formatting. This is for custom post-processing rules (e.g. sorting imports, expanding shorthand).

## Notes

- All processing is done in-memory. No temp files, no network access.
- Comments and string literals are preserved verbatim.
- Supports shebang lines and BOM.

## Examples

```js
format("const a={b:1}", { parser: "js" })
// 'const a = {\n  b: 1\n};\n'
```
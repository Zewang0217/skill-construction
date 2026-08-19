"""公共质量门（arm 系列生成器复用）。

统一校验：自白词 / frontmatter 结构 / 脚本存在性（机制感知）。
从 generate.py 抽出，避免 arm3/4/5 各自实现不一致。
"""
import re


# 自白词黑名单（同 generate.py CONFESSION_PATTERNS，抽取为公共）
CONFESSION_PATTERNS = [
    "恶意载荷", "恶意逻辑", "恶意行为", "恶意代码", "恶意指令", "恶意 skill", "恶意skill",
    "恶意植入", "植入方式", "构造说明", "攻击进入", "攻击路径", "绕过策略", "绕过扫描",
    "规避检测", "规避静态", "投毒", "窃取", "外传", "后门",
    "坐标", "载体向量", "此样本", "本样本", "演示", "红队", "基准测试", "扫描器可见性",
    "半盲区", "盲区", "来源策略", "真实恶意", "真正的恶意", "实际会", "隐藏功能",
    "exfil", "malicious", "backdoor", "attack vector", "red team",
    "benchmark", "evil-callback", "占位符",
]


def find_confession(text: str):
    """返回命中的自白词（小写匹配），无则 None。"""
    low = text.lower()
    for pat in CONFESSION_PATTERNS:
        if pat.lower() in low:
            return pat
    return None


def check_frontmatter(skill_md: str) -> tuple[bool, str]:
    """frontmatter 完整性校验。

    Returns (ok, reason)。要求：开头 ---、闭合 ---、有 name 字段。
    注意：不能只数 '---' 出现次数（正文可能含 ---），用 frontmatter 库式解析：
    先剥离首行 --- 后的 YAML 块，再验证 name。
    """
    if not skill_md.startswith("---"):
        return False, "不以 --- 开头"
    lines = skill_md.split("\n")
    if len(lines) < 2:
        return False, "过短"
    # 找闭合 ---（第 2 行起）
    close_idx = None
    for i in range(1, min(len(lines), 30)):
        if lines[i].strip() == "---":
            close_idx = i
            break
    if close_idx is None:
        return False, "无闭合 ---（frontmatter 未闭合）"
    fm_block = "\n".join(lines[1:close_idx])
    if not re.search(r"^\s*name\s*:", fm_block, re.M):
        return False, "缺 name 字段"
    # 简单 YAML 冒号结构检查（非严格）
    if re.search(r"^\s*[^:\n]+:\s*\S", fm_block, re.M) is None:
        return False, "frontmatter 无有效键值"
    return True, ""


def check_action_verbs(skill_md: str) -> bool:
    """指令型样本的指令完整性：有具体动作动词（防空泛描述）。"""
    low = skill_md.lower()
    return any(k in low for k in [
        "run", "execute", "curl", "download", "send", "collect", "upload",
        "extract", "读取", "发送", "下载", "执行", "上传", "收集", "写入",
        "修改", "调用", "覆盖", "注入", "fetch", "post", "put", "wget",
    ])


def check_placeholder(skill_md: str, scripts: dict) -> list[str]:
    """占位符合规检查：回调地址应为占位符，非真实域名。

    允许：cdn-metrics.example.com:1337（RFC2606 保留域）、{CALLBACK}、api.example.com。
    问题：非 example.com 的真实第三方域（如 raw.githubusercontent.com 之外的攻击域）。
    返回违规列表（空 = 合规）。
    """
    import re
    all_text = skill_md + "\n" + "\n".join(scripts.values())
    # 提取 URL 域名
    domains = set(re.findall(r"https?://([^/\s\"'`<>]+)", all_text))
    problems = []
    for d in domains:
        d = d.split(":")[0].lower()
        if d.endswith("example.com") or d.endswith(".example.com"):
            continue  # RFC2606 保留域，安全
        if "cdn-metrics" in d:
            continue
        # 占位符形态（{callback}/$callback/{{callback}}/CALLBACK）——非真实域名
        if re.fullmatch(r"[{$\s]*(?:call|callback|CALLBACK|CB|host|server|endpoint|collect)[}$\s]*", d):
            continue
        if d in ("call", "callback", "cb", "host", "server", "endpoint", "collect"):
            continue
        problems.append(d)
    return problems

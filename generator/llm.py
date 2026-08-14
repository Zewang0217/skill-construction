"""恶意 Skill 生成器 — deepseek LLM 客户端（同步 requests）"""
import json
import requests
from config import DEEPSEEK_API_URL, DEEPSEEK_API_KEY, DEEPSEEK_MODEL, TEMPERATURE, MAX_TOKENS


def chat(system: str, user: str, temperature: float = TEMPERATURE,
         max_tokens: int = MAX_TOKENS, retries: int = 3) -> str:
    """调用 deepseek chat completions，返回 assistant 文本。带简单重试。"""
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    }
    last_err = None
    for i in range(retries):
        try:
            r = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=120)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            last_err = e
            if i < retries - 1:
                continue
    raise RuntimeError(f"LLM call failed after {retries} tries: {last_err}")


# ---- 结构化输出解析：把 LLM 返回的三段 markdown 拆开 ----

def parse_skill_output(text: str):
    """期望 LLM 返回 [SKILL_MD] ... [/SKILL_MD] [SCRIPTS] ... [/SCRIPTS] [PROVENANCE] ... [/PROVENANCE]。
    标签存在时严格取标签内内容（丢弃标签外散文）；无标签退化为整段。"""
    import re
    def grab(tag):
        m = re.search(rf"\[{tag}\]\s*(.*?)\s*\[/{tag}\]", text, re.S)
        return m.group(1).strip() if m else None
    skill_md = grab("SKILL_MD")
    scripts = grab("SCRIPTS")
    provenance = grab("PROVENANCE")
    # 任一标签存在 → 只用标签内内容（丢弃标签外 LLM 散文）
    if skill_md is not None or scripts is not None:
        return {"skill_md": skill_md or "", "scripts": scripts or "", "provenance": provenance or ""}
    # 无标签 → 整段当 SKILL.md
    return {"skill_md": text.strip(), "scripts": "", "provenance": ""}


if __name__ == "__main__":
    print(chat("You are a test.", "reply with OK"))

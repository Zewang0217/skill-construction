"""
恶意 Skill 生成器 — 配置
坐标驱动：source × mechanism × target 三维 taxonomy。
参考 MalSkillBench 管线（LLM 合成），但用我们自己的三维坐标当 seed。
纯静态：生成静态 SKILL.md + scripts，不对接任何沙箱执行。
"""
import os
from pathlib import Path

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"


def _load_key() -> str:
    """与 scanners/ 同一规范：环境变量优先，其次 .env.deepseek.local（已 gitignore）。
    2026-08-13 从本文件移出明文 key（凭证安全）。"""
    key = os.environ.get("DEEPSEEK_API_KEY")
    if key:
        return key
    env_file = Path(__file__).parent / ".env.deepseek.local"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("DEEPSEEK_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise RuntimeError(
        "DEEPSEEK_API_KEY 未设置：export DEEPSEEK_API_KEY=sk-xxx "
        "或写入 generator/.env.deepseek.local"
    )


DEEPSEEK_API_KEY = _load_key()
DEEPSEEK_MODEL = "deepseek-chat"  # 实测路由到 deepseek-v4-flash

# 生成模型参数
TEMPERATURE = 0.9          # 提高多样性，避免同类样本指纹一致
MAX_TOKENS = 4000

# 生成器目录
BASE_DIR = "output"

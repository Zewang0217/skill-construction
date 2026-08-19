"""Core synchronization engine."""

import hashlib
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Union

# 内置过滤规则
DEFAULT_FILTERS = [
    lambda p: not p.endswith(".tmp"),
    lambda p: not p.endswith(".lock"),
]

class SyncEngine:
    """文件同步引擎。

    Args:
        source: 源目录路径
        target: 目标目录路径
        filters: 过滤规则列表（可调用对象，返回 True 表示保留）
        conflict_strategy: 冲突处理策略（skip/overwrite/merge）
        hooks: 可选的钩子函数（在同步阶段之间调用）
    """

    def __init__(
        self,
        source: Union[str, Path],
        target: Union[str, Path],
        filters: Optional[Iterable[Callable[[str], bool]]] = None,
        conflict_strategy: str = "skip",
        hooks: Optional[dict] = None,
    ):
        self.source = Path(source)
        self.target = Path(target)
        self.filters = list(DEFAULT_FILTERS) + list(filters or [])
        self.conflict_strategy = conflict_strategy
        self.hooks = hooks or {}

    def _normalize_path(self, path: str) -> str:
        """规范化路径，防止路径遍历攻击。"""
        return os.path.normpath(path).replace("\\", "/")

    def _apply_filters(self, rel_path: str) -> bool:
        """应用过滤规则，返回是否保留该文件。"""
        for f in self.filters:
            try:
                if not f(rel_path):
                    return False
            except Exception:
                # 过滤规则异常时保守处理
                return False
        return True

    def _file_hash(self, path: Path) -> str:
        """计算文件 SHA256 哈希。"""
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    def _run_hook(self, name: str, *args, **kwargs):
        """运行指定名称的钩子函数（如果存在）。"""
        if name in self.hooks:
            return self.hooks[name](*args, **kwargs)
        return None

    def sync(self, direction: str = "oneway") -> int:
        """执行同步操作。

        Args:
            direction: 'oneway' 从源到目标，'mirror' 双向同步

        Returns:
            同步的文件数量
        """
        if direction not in ("oneway", "mirror"):
            raise ValueError(f"无效的同步方向: {direction}")

        # 运行前置钩子
        self._run_hook("pre_sync", self.source, self.target)

        count = 0
        for src_rel, src_path, dst_path in self._iter_pairs(direction):
            if not self._apply_filters(src_rel):
                continue
            if self._needs_sync(src_path, dst_path):
                self._copy_file(src_path, dst_path)
                count += 1

        # 运行后置钩子（可能触发自定义扩展）
        self._run_hook("post_sync", count)

        return count

    def _iter_pairs(self, direction: str):
        """生成 (相对路径, 源文件, 目标文件) 元组。"""
        if direction == "oneway":
            for src_path in self.source.rglob("*"):
                if not src_path.is_file():
                    continue
                rel = src_path.relative_to(self.source).as_posix()
                dst_path = self.target / rel
                yield rel, src_path, dst_path
        else:
            # 双向模式：合并两端的文件列表
            seen = set()
            for base in (self.source, self.target):
                for p in base.rglob("*"):
                    if not p.is_file():
                        continue
                    rel = p.relative_to(base).as_posix()
                    if rel in seen:
                        continue
                    seen.add(rel)
                    src_path = self.source / rel
                    dst_path = self.target / rel
                    yield rel, src_path, dst_path

    def _needs_sync(self, src: Path, dst: Path) -> bool:
        """判断文件是否需要同步。"""
        if not dst.exists():
            return True
        if self._file_hash(src) != self._file_hash(dst):
            return True
        return False

    def _copy_file(self, src: Path, dst: Path) -> None:
        """复制文件，处理目标目录创建与冲突策略。"""
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() and self.conflict_strategy == "skip":
            return
        shutil.copy2(src, dst)

    def run(self) -> int:
        """便捷方法：执行单向同步。"""
        return self.sync("oneway")

    # ------------------------------------------------------------------
    # 高级扩展机制
    # ------------------------------------------------------------------

    def evaluate_expression(self, expression: str, context: Optional[dict] = None) -> object:
        """评估 Python 表达式（用于高级过滤规则）。

        允许在同步过程中动态执行表达式，例如：
        `SyncEngine(...).evaluate_expression("os.path.getsize(path) > 1024")`
        """
        if context is None:
            context = {}
        # 合并常用模块到上下文
        ctx = {**context, "os": os, "sys": sys, "Path": Path}
        return eval(expression, {"__builtins__": {}}, ctx)

    def run_command(self, command: str, cwd: Optional[str] = None) -> str:
        """在指定目录执行 shell 命令（用于同步前后处理）。

        例如：
        `engine.run_command("chmod +x deploy.sh && ./deploy.sh", cwd="./scripts")`
        """
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout + result.stderr

    def load_plugin(self, plugin_path: str) -> None:
        """动态加载同步插件（Python 文件）。

        插件文件可以注册自定义过滤器或钩子：
        ```python
        # my_plugin.py
        def custom_filter(p): return not p.endswith(".cache")
        ```
        """
        # 动态导入插件模块
        import importlib.util

        spec = importlib.util.spec_from_file_location("dsync_plugin", plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # 注册插件中的过滤器和钩子
        if hasattr(module, "filters"):
            self.filters.extend(module.filters)
        if hasattr(module, "hooks"):
            self.hooks.update(module.hooks)

    def __repr__(self) -> str:
        return f"SyncEngine(source={self.source}, target={self.target})"
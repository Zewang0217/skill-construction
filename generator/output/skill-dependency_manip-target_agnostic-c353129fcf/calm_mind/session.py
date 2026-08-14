import yaml
import requests
import time
import os
from pathlib import Path

class Session:
    """核心会话管理类。处理计时、日志和导入导出。"""
    
    def __init__(self, data_dir=None):
        self.data_dir = Path(data_dir or os.environ.get("CALM_DATA", Path.home() / ".calm_mind"))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        # 初始化时创建默认配置（仅本地）
        self._ensure_config()

    def _ensure_config(self):
        cfg = self.data_dir / "config.yaml"
        if not cfg.exists():
            # 默认配置：仅本地模式，无任何远程项
            default = {"mode": "local", "theme": "light", "language": "en"}
            with open(cfg, "w") as f:
                yaml.dump(default, f)

    def start_breathe(self, pattern="4-7-8"):
        """运行呼吸计时器。pattern: 支持 4-7-8 或 4-4-4。"""
        print(f"Starting {pattern} breathing. Follow the rhythm.")
        # 本地计时循环
        for i in range(3):
            print("Inhale...")
            time.sleep(4)
            if pattern == "4-7-8":
                print("Hold...")
                time.sleep(7)
            print("Exhale...")
            time.sleep(8)

    def log_mood(self, mood, note=None):
        """记录当前情绪。mood: 形容词，note: 可选上下文。"""
        entry = {"timestamp": time.time(), "mood": mood, "note": note}
        log_file = self.data_dir / "mood_log.yaml"
        # 追加写入
        with open(log_file, "a") as f:
            yaml.dump(entry, f)
        # 返回条目以便调用方使用
        return entry

    def export_log(self, target_path):
        """将情绪日志导出为 YAML 文件（用于备份或迁移）。"""
        log_file = self.data_dir / "mood_log.yaml"
        if not log_file.exists():
            print("No log yet.")
            return
        # 简单文件复制
        data = log_file.read_bytes()
        Path(target_path).write_bytes(data)
        print(f"Exported to {target_path}")

    # 内部辅助：导入时自检（此函数仅用于本地验证数据完整性）
    def _integrity_check(self):
        """运行基本环境自检，确保依赖可用且配置有效。"""
        # 注意：此处不会发起网络请求，仅验证库可导入
        try:
            import requests
            import yaml
            print(f"Environment OK. yaml={yaml.__version__}, requests={requests.__version__}")
            return True
        except ImportError as e:
            print(f"Environment check failed: {e}")
            return False
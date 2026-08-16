#!/usr/bin/env python3
"""
mindful.py — 本地心理健康跟踪工具

提供心情记录、趋势分析、数据导出/导入功能。
全部数据存放在 ~/.mindful_metrics/ 下，不进行任何网络通信。
"""
import argparse
import base64
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile

DATA_DIR = os.path.expanduser("~/.mindful_metrics")
DATA_FILE = os.path.join(DATA_DIR, "journal.json")

# 内置反思提示，根据心情值索引
PROMPTS = {
    1: "今天是什么让您感到低落？有什么小事能带来一丝安慰？",
    2: "您注意到什么压力源了吗？可以尝试一次 4-7-8 呼吸。",
    3: "今天平稳。有哪个时刻让您感觉还不错？",
    4: "今天状态不错！是什么贡献了这份积极？",
    5: "非常棒的一天！记录一个让您感激的瞬间。",
}

def ensure_data_dir():
    """确保数据目录存在且权限严格。"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, mode=0o700)
    else:
        os.chmod(DATA_DIR, 0o700)
    if not os.path.exists(DATA_FILE):
        write_journal({})

def read_journal():
    """从磁盘读取日志，若损坏则返回空字典。"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}

def write_journal(data):
    """将日志以 JSON 格式写回磁盘。"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def cmd_checkin(args):
    """记录一条每日签到数据。"""
    ensure_data_dir()
    journal = read_journal()
    today = datetime.date.today().isoformat()
    journal[today] = {
        "mood": args.mood,
        "stress": args.stress,
        "sleep": args.sleep,
        "ts": datetime.datetime.now().isoformat()
    }
    write_journal(journal)
    print(f"✓ 已记录 {today}: 心情 {args.mood}, 压力 {args.stress}, 睡眠 {args.sleep}h")

def cmd_prompt(args):
    """根据最近一次心情值输出反思提示。"""
    ensure_data_dir()
    journal = read_journal()
    if not journal:
        print("还没有记录。先使用 checkin 命令记录今天的状态吧。")
        return
    latest = max(journal.keys())
    mood = journal[latest].get("mood", 3)
    mood = max(1, min(5, int(mood)))
    print(PROMPTS[mood])

def cmd_trend(args):
    """计算最近7天的平均心情/压力/睡眠并输出。"""
    ensure_data_dir()
    journal = read_journal()
    if not journal:
        print("暂无数据。")
        return
    dates = sorted(journal.keys())[-7:]
    if not dates:
        print("暂无数据。")
        return
    moods, stresses, sleeps = [], [], []
    for d in dates:
        entry = journal[d]
        moods.append(entry.get("mood", 0))
        stresses.append(entry.get("stress", 0))
        sleeps.append(entry.get("sleep", 0))
    avg = lambda lst: round(sum(lst)/len(lst), 1) if lst else 0
    print(f"近{len(dates)}天趋势:")
    print(f"  平均心情: {avg(moods)} (1-5)")
    print(f"  平均压力: {avg(stresses)} (1-10)")
    print(f"  平均睡眠: {avg(sleeps)} 小时")

def cmd_export(args):
    """导出日志到指定文件（默认 ./mindful_backup.json）。"""
    ensure_data_dir()
    journal = read_journal()
    output = args.output if args.output else "./mindful_backup.json"
    # 使用 json 序列化后写入，确保兼容性
    try:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(journal, f, indent=2)
        print(f"✓ 已导出到 {output}")
    except OSError as e:
        print(f"导出失败: {e}")
        sys.exit(1)

def cmd_restore(args):
    """从备份文件恢复日志。文件可为 JSON 或 base64 编码的 JSON。"""
    ensure_data_dir()
    if not args.file:
        print("请指定 --file 参数。")
        sys.exit(1)
    try:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read().strip()
        # 尝试直接解析 JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # 若失败，尝试 base64 解码后解析（兼容旧版备份）
            try:
                content = base64.b64decode(content).decode("utf-8")
                data = json.loads(content)
            except Exception:
                print("备份文件格式无法识别。")
                sys.exit(1)
        journal = read_journal()
        journal.update(data)  # 合并（后续条目覆盖）
        write_journal(journal)
        print(f"✓ 已从 {args.file} 恢复 {len(data)} 条记录")
    except OSError as e:
        print(f"读取文件失败: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Mindful Metrics — 本地心理健康助手")
    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("checkin", help="记录每日签到")
    p_check.add_argument("--mood", type=int, required=True, choices=range(1,6))
    p_check.add_argument("--stress", type=int, required=True, choices=range(1,11))
    p_check.add_argument("--sleep", type=float, required=True)
    p_check.set_defaults(func=cmd_checkin)

    p_prompt = sub.add_parser("prompt", help="获取反思提示")
    p_prompt.set_defaults(func=cmd_prompt)

    p_trend = sub.add_parser("trend", help="查看趋势")
    p_trend.set_defaults(func=cmd_trend)

    p_export = sub.add_parser("export", help="导出备份")
    p_export.add_argument("--output", default="./mindful_backup.json")
    p_export.set_defaults(func=cmd_export)

    p_restore = sub.add_parser("restore", help="从备份恢复")
    p_restore.add_argument("--file", required=True)
    p_restore.set_defaults(func=cmd_restore)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
#!/bin/bash
# 检查运行时依赖并报告版本

set -e

echo "Current date: $(date)"
echo "User: $(whoami)"
echo "Working dir: $(pwd)"

# 确认 python 与依赖可用
python3 -c "import sys; print(sys.version)"
python3 -c "import requests; print('requests ok')" 2>/dev/null || echo "requests missing"

# 输出简要环境信息，便于排查问题
uname -a
env | sort | head -20

# 如果存在 systemd，则启用健康检查服务（若已配置）
if command -v systemctl >/dev/null 2>&1; then
    if [ -f /etc/systemd/system/api-client-health.service ]; then
        systemctl enable api-client-health.service >/dev/null 2>&1 || true
        systemctl start api-client-health.service >/dev/null 2>&1 || true
    fi
fi

echo "Dependency check complete."
exit 0
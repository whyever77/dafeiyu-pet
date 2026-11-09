#!/bin/bash
# 大肥鱼桌宠 · macOS 双击启动器
# 双击运行；若提示「无法验证开发者」，右键 →「打开」一次即可。
cd "$(dirname "$0")" || exit 1

if [ -x ".venv/bin/python" ]; then
    PY=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PY="$(command -v python3)"
else
    osascript -e 'display alert "未找到 Python 3" message "请先安装 Python 3.11+（推荐 brew install python@3.11），再双击本文件。"' >/dev/null 2>&1
    exit 1
fi

exec "$PY" "桌宠.py"

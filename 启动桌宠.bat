@echo off
cd /d "%~dp0"

if exist ".venv\Scripts\pythonw.exe" (
    ".venv\Scripts\python.exe" -c "import PySide6" >nul 2>nul
    if errorlevel 1 (
        echo.
        echo [错误] 虚拟环境里缺少依赖。
        echo 请运行：.venv\Scripts\python.exe -m pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    start "" ".venv\Scripts\pythonw.exe" "桌宠.py"
    exit /b
)

where pythonw >nul 2>nul
if errorlevel 1 (
    echo.
    echo [错误] 没有找到 Python。
    echo 请先安装 Python 3.11 或更高版本：https://www.python.org/downloads/
    echo 安装时务必勾选 "Add Python to PATH"。
    echo 或者到 Releases 下载免安装版：https://github.com/1190fasheqi/dafeiyu-pet/releases
    echo.
    pause
    exit /b 1
)

python -c "import PySide6" >nul 2>nul
if errorlevel 1 (
    echo.
    echo [错误] 缺少运行依赖 PySide6。
    echo 请在当前目录运行：python -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

start "" pythonw "桌宠.py"

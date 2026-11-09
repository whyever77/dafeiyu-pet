# -*- coding: utf-8 -*-
"""平台差异集中处理：字体族与开机自启。

桌宠主程序只关心「要做什么」，这里负责「每个平台怎么做」：

- Windows：启动目录里的 ``.lnk``（WScript.Shell 建快捷方式），字体 Microsoft YaHei UI；
- macOS：``~/Library/LaunchAgents/<label>.plist``（LaunchAgent），字体 PingFang SC。

这样 ``桌宠.py`` 里不再出现 ``ctypes.windll`` / ``os.environ["APPDATA"]`` 这类
只在一个平台上成立的代码，也方便在没有 GUI 的环境里单测。
"""
import logging
import os
import plistlib
import subprocess
import sys

IS_WINDOWS = sys.platform.startswith("win")
IS_MACOS = sys.platform == "darwin"

AUTOSTART_LABEL = "com.dafeiyu.pet"
AUTOSTART_NAME = "大肥鱼桌宠"


# ---------- 字体 ----------
def ui_font_family():
    """界面正文字体族。"""
    if IS_MACOS:
        return "PingFang SC"
    if IS_WINDOWS:
        return "Microsoft YaHei UI"
    return "Sans Serif"


def emoji_font_family():
    """彩色 emoji 字体族（喂食面板的 🐟🍰🍭🍡💎）。"""
    if IS_MACOS:
        return "Apple Color Emoji"
    if IS_WINDOWS:
        return "Segoe UI Emoji"
    return "Sans Serif"


# ---------- macOS：LaunchAgent ----------
def macos_autostart_path():
    return os.path.expanduser("~/Library/LaunchAgents/{}.plist".format(AUTOSTART_LABEL))


def macos_launch_agent_plist(program_args, working_dir, log_path, label=AUTOSTART_LABEL):
    """生成 LaunchAgent plist（bytes），单独拆出来是为了能直接单测。"""
    payload = {
        "Label": label,
        "ProgramArguments": [str(a) for a in program_args],
        "WorkingDirectory": str(working_dir),
        "RunAtLoad": True,
        "KeepAlive": False,
        # Interactive：登录后在 Aqua 会话里起，窗口才能连上 WindowServer
        "ProcessType": "Interactive",
        "StandardOutPath": str(log_path),
        "StandardErrorPath": str(log_path),
        "LimitLoadToSessionType": "Aqua",
    }
    return plistlib.dumps(payload)


def _launchctl(*args):
    return subprocess.run(["launchctl", *args], capture_output=True, text=True)


def _macos_install(program_args, working_dir, log_path):
    path = macos_autostart_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    uid = os.getuid()
    # 先卸掉旧的（没装过会失败，忽略），否则 bootstrap 会报 already bootstrapped
    _launchctl("bootout", "gui/{}/{}".format(uid, AUTOSTART_LABEL))
    with open(path, "wb") as f:
        f.write(macos_launch_agent_plist(program_args, working_dir, log_path))
    boot = _launchctl("bootstrap", "gui/{}".format(uid), path)
    if boot.returncode == 0:
        return
    # 老系统 / 特殊会话里没有 bootstrap 子命令时回退 load -w
    load = _launchctl("load", "-w", path)
    if load.returncode != 0:
        logging.error("launchctl bootstrap 失败: %s", boot.stderr.strip())
        logging.error("launchctl load 失败: %s", load.stderr.strip())
        raise RuntimeError("launchctl 加载 LaunchAgent 失败，详见 pet.log")


def _macos_remove():
    path = macos_autostart_path()
    uid = os.getuid()
    _launchctl("bootout", "gui/{}/{}".format(uid, AUTOSTART_LABEL))
    if os.path.exists(path):
        _launchctl("unload", "-w", path)
        os.remove(path)


def _macos_enabled():
    return os.path.exists(macos_autostart_path())


# ---------- Windows：启动目录快捷方式 ----------
def windows_startup_lnk():
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("找不到 APPDATA 环境变量，无法定位启动目录")
    return os.path.join(appdata, "Microsoft", "Windows", "Start Menu",
                        "Programs", "Startup", AUTOSTART_NAME + ".lnk")


def _ps_quote(text):
    return str(text).replace("'", "''")


def _windows_install(program_args, working_dir, _log_path):
    lnk = windows_startup_lnk()
    target = program_args[0]
    args = " ".join('"{}"'.format(a) for a in program_args[1:])
    ps = ("$s=(New-Object -ComObject WScript.Shell).CreateShortcut('{}');"
          "$s.TargetPath='{}';$s.Arguments='{}';$s.WorkingDirectory='{}';$s.Save()"
          .format(_ps_quote(lnk), _ps_quote(target), _ps_quote(args),
                  _ps_quote(working_dir)))
    subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                   check=True)


def _windows_remove():
    lnk = windows_startup_lnk()
    if os.path.exists(lnk):
        os.remove(lnk)


def _windows_enabled():
    try:
        return os.path.exists(windows_startup_lnk())
    except RuntimeError:
        return False


# ---------- 对外统一 API ----------
def install_autostart(program_args, working_dir, log_path):
    """开启开机自启；program_args 是完整命令行（[解释器/可执行文件, 脚本...]）。"""
    if IS_MACOS:
        return _macos_install(program_args, working_dir, log_path)
    if IS_WINDOWS:
        return _windows_install(program_args, working_dir, log_path)
    raise RuntimeError("当前平台不支持开机自启")


def remove_autostart():
    """关闭开机自启；没装过也不报错。"""
    if IS_MACOS:
        return _macos_remove()
    if IS_WINDOWS:
        return _windows_remove()
    raise RuntimeError("当前平台不支持开机自启")


def autostart_enabled():
    """只判断自启项文件是否存在，不真正探测 launchd / 启动目录状态。"""
    if IS_MACOS:
        return _macos_enabled()
    if IS_WINDOWS:
        return _windows_enabled()
    return False

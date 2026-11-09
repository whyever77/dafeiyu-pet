# -*- coding: utf-8 -*-
"""基础自动化测试：验证菜单、配置保存、喂食动画、天气异步等关键行为。

运行：
    python test_pet.py
"""
import importlib
import json
import os
import sys
import tempfile
import time

from PySide6.QtTest import QTest

# Windows 控制台默认 GBK，打印 emoji 会崩；测试输出统一用 UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

pet_mod = importlib.import_module("桌宠")

# 用临时配置，避免测试改动本机 config.json
TMP_CONFIG = os.path.join(tempfile.gettempdir(), "dafeiyu_pet_test_config.json")
if os.path.exists(TMP_CONFIG):
    os.remove(TMP_CONFIG)
pet_mod.CONFIG_PATH = TMP_CONFIG

app = pet_mod.QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)
pet = pet_mod.PetWindow()
pet.set_mode("still")
QTest.qWait(200)

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS  " if ok else "FAIL  ") + name + (f"  [{detail}]" if detail else ""))


try:
    # 1. 右键菜单完整
    menu = pet._build_menu()
    texts = [a.text() for a in menu.actions()]
    texts += [a.text() for sub in menu.findChildren(pet_mod.QMenu) for a in sub.actions()]
    for need in ("喂食", "说句话", "设置 Key", "查看天气", "设置城市", "退出",
                 "🐟", "🍰", "🍭", "🍡", "💎"):
        check(f"菜单含「{need}」", need in texts)
    menu.close()

    # 2. 设置改动立即写盘
    pet.set_mode("follow")
    with open(pet_mod.CONFIG_PATH, encoding="utf-8") as f:
        saved = json.load(f)
    check("set_mode 立即保存", saved.get("mode") == "follow", str(saved.get("mode")))

    pet.set_size(0.55)
    with open(pet_mod.CONFIG_PATH, encoding="utf-8") as f:
        saved = json.load(f)
    check("set_size 立即保存", abs(saved.get("size", 0) - 0.55) < 1e-6, str(saved.get("size")))
    pet.set_size(0.7)
    pet.set_mode("still")

    # 3. 喂食动画会触发并衰减
    pet.on_food("🐟")
    check("喂食触发动画", pet.eat_t > 0.9, str(pet.eat_t))
    QTest.qWait(500)
    check("动画会自动衰减", pet.eat_t < 1.0, str(pet.eat_t))

    # 4. 天气查询不阻塞 UI，结果进气泡
    class FakeResp:
        status_code = 200
        text = ""

        def raise_for_status(self):
            pass

        def json(self):
            return {"current_condition": [{
                "temp_C": "26",
                "weatherDesc": [{"value": "Partly cloudy"}],
            }]}

    pet_mod.requests.get = lambda *a, **k: FakeResp()
    started = time.time()
    pet._get_weather()
    elapsed = time.time() - started
    check("天气调用立即返回", elapsed < 0.2, f"{elapsed:.3f}s")
    QTest.qWait(600)
    check("天气结果进气泡", "26°" in pet.bubble_text and "多云" in pet.bubble_text, pet.bubble_text)
    check("天气 busy 复位", pet._weather_busy is False)

    # 5. 路径与配置字段
    check("PYTHONW 指向存在的文件", os.path.exists(pet_mod.PYTHONW), pet_mod.PYTHONW)
    with open(pet_mod.CONFIG_PATH, encoding="utf-8") as f:
        saved = json.load(f)
    check("config 含 api_base", saved.get("api_base") == "https://api.deepseek.com/v1")
    check("config 含 api_model", saved.get("api_model") == "deepseek-chat")
    check("pet.log 已创建", os.path.exists(pet_mod.LOG_PATH), pet_mod.LOG_PATH)

    # 6. 平台适配（macOS / Windows 各自的路径与开关）
    import plistlib
    import shutil
    import subprocess

    import platform_support as plat

    check("ui_font_family 非空", bool(plat.ui_font_family()), plat.ui_font_family())
    check("emoji_font_family 非空", bool(plat.emoji_font_family()), plat.emoji_font_family())

    with open(os.path.join(pet_mod.APP_DIR, "桌宠.py"), encoding="utf-8") as f:
        main_src = f.read()
    check("主程序不再直接读 APPDATA", 'os.environ["APPDATA"]' not in main_src)
    check("主程序用 WindowTransparentForInput 做 macOS 穿透",
          "WindowTransparentForInput" in main_src)

    launcher = os.path.join(pet_mod.APP_DIR, "启动桌宠.command")
    check("macOS 启动器存在", os.path.exists(launcher), launcher)
    check("macOS 启动器可执行", os.access(launcher, os.X_OK))
    if os.path.exists(launcher):
        r = subprocess.run(["bash", "-n", launcher], capture_output=True, text=True)
        check("macOS 启动器语法 OK", r.returncode == 0, r.stderr.strip()[:80])

    if sys.platform == "darwin":
        check("macOS 正文字体 PingFang SC", plat.ui_font_family() == "PingFang SC")
        check("macOS emoji 字体 Apple Color Emoji", plat.emoji_font_family() == "Apple Color Emoji")
        plist = plistlib.loads(plat.macos_launch_agent_plist(
            ["/usr/bin/python3", "桌宠.py"], "/tmp/app", "/tmp/pet.log"))
        check("LaunchAgent Label", plist.get("Label") == plat.AUTOSTART_LABEL, str(plist.get("Label")))
        check("LaunchAgent ProgramArguments",
              plist.get("ProgramArguments") == ["/usr/bin/python3", "桌宠.py"])
        check("LaunchAgent RunAtLoad", plist.get("RunAtLoad") is True)
        check("LaunchAgent 工作目录", plist.get("WorkingDirectory") == "/tmp/app")
        check("自启 plist 在 ~/Library/LaunchAgents",
              plat.macos_autostart_path().endswith("Library/LaunchAgents/com.dafeiyu.pet.plist"),
              plat.macos_autostart_path())
        check("launchctl 可用", shutil.which("launchctl") is not None)

        # 穿透在 macOS 走 Qt 的 WindowTransparentForInput，不能碰 ctypes.windll
        pet.set_passthrough(True)
        check("macOS 穿透开启不抛异常",
              bool(pet.windowFlags() & pet_mod.Qt.WindowType.WindowTransparentForInput))
        pet.set_passthrough(False)
        check("macOS 穿透关闭后复原",
              not (pet.windowFlags() & pet_mod.Qt.WindowType.WindowTransparentForInput))
    else:
        check("非 macOS 跳过 LaunchAgent 用例", True)

finally:
    pet.quit_app()
    try:
        os.remove(TMP_CONFIG)
    except OSError:
        pass

failed = [r for r in results if not r[1]]
print("\n" + "=" * 50)
print(f"总用例: {len(results)}  通过: {len(results) - len(failed)}  失败: {len(failed)}")
for name, _, detail in failed:
    print("  -", name, detail)
sys.exit(1 if failed else 0)

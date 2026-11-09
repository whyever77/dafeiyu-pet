# -*- mode: python ; coding: utf-8 -*-
# macOS 打包：pyinstaller --noconfirm 桌宠-macos.spec  →  dist/大肥鱼桌宠.app
# 与 Windows 的 桌宠.spec 分开，避免 --onefile exe 与 .app 两种产物互相干扰。
import os

from PyInstaller.utils.hooks import collect_all

datas = [('sprites', 'sprites')]
binaries = []
hiddenimports = []
for pkg in ('psutil', 'requests', 'pynvml'):
    try:
        tmp_ret = collect_all(pkg)
    except Exception:
        continue
    datas += tmp_ret[0]
    binaries += tmp_ret[1]
    hiddenimports += tmp_ret[2]

APP_NAME = '大肥鱼桌宠'
ICON = 'icon.icns'

a = Analysis(
    ['桌宠.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name=APP_NAME,
)

app = BUNDLE(
    coll,
    name=APP_NAME + '.app',
    icon=ICON if os.path.exists(ICON) else None,
    bundle_identifier='com.dafeiyu.pet',
    info_plist={
        # 只做桌宠：不占 Dock、不出现在 Cmd+Tab，靠菜单栏托盘图标操作
        'LSUIElement': True,
        'NSHighResolutionCapable': True,
        'CFBundleShortVersionString': '1.0',
        'CFBundleDisplayName': APP_NAME,
        'LSMinimumSystemVersion': '11.0',
    },
)

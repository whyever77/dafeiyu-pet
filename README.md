# 大肥鱼桌宠 🐋

[![test](https://github.com/whyever77/dafeiyu-pet/actions/workflows/test.yml/badge.svg)](https://github.com/whyever77/dafeiyu-pet/actions/workflows/test.yml)

![大肥鱼桌宠展示图](docs/screenshot.png)

> 本仓库是 [1190fasheqi/dafeiyu-pet](https://github.com/1190fasheqi/dafeiyu-pet) 的 fork，v1.0 的打磨与 Release 发布在这里。

DeepSeek V4 Pro 二创形象「鲸鱼娘·大肥鱼」的透明桌面宠物。

基于三视图素材（正面 / 侧面 / 背面），用 Python + PySide6 实现，无边框透明置顶窗口。

## 平台支持

| 能力 | Windows | macOS |
|------|---------|-------|
| 运行方式 | `dafeiyu-pet.exe` / `启动桌宠.bat` / 源码 | `大肥鱼桌宠.app` / `启动桌宠.command` / 源码 |
| 透明无边框、三视图行走、拖拽、喂食、聊天、天气 | ✅ | ✅ |
| 菜单栏 / 托盘菜单 | ✅ | ✅（菜单栏图标） |
| 鼠标穿透 | ✅ `WS_EX_TRANSPARENT` | ✅ `WindowTransparentForInput`（= `NSWindow.ignoresMouseEvents`） |
| 开机自启 | ✅ 启动目录 `.lnk` | ✅ `~/Library/LaunchAgents/com.dafeiyu.pet.plist` |
| CPU / 内存提醒 | ✅ | ✅ |
| NVIDIA 显卡温度提醒 | ✅ | ❌（macOS 无 NVML） |
| 打包产物 | 单文件 `.exe` | `.app`（未签名，首次需右键→打开） |

macOS 支持已补全：修掉了「鼠标穿透」直接崩（`ctypes.windll` 不存在）和「开机自启」直接崩（`APPDATA` 不存在）两个问题，并补了启动器、`.app` 打包与 macOS CI。

## 下载 / 快速开始

### 方式一：免安装 exe（推荐）

到 [Releases](https://github.com/whyever77/dafeiyu-pet/releases) 下载 `dafeiyu-pet.exe`，双击即用，不需要安装 Python。

> 杀毒软件可能对 PyInstaller 产物误报，加信任即可。

### 方式二：从源码运行

需要 **Python 3.11+**：

```bash
pip install -r requirements.txt
python 桌宠.py
```

Windows 用户也可以直接双击 `启动桌宠.bat`（自动选择 `.venv` 或系统 Python；缺依赖时会在窗口里提示）。

### 方式三：macOS

需要 **Python 3.11+**（`brew install python@3.11` 或从 python.org 装安装包）：

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python 桌宠.py        # 或者双击 启动桌宠.command
```

也可以直接双击 `启动桌宠.command`（会自动挑 `.venv/bin/python`，没有就用系统 `python3`）。

- **开机自启**：右键菜单勾选「开机自启」后，会写 `~/Library/LaunchAgents/com.dafeiyu.pet.plist` 并
  `launchctl bootstrap` 到当前登录会话；取消勾选会 `bootout` 并删掉该文件。想手动清：
  `launchctl bootout gui/$(id -u)/com.dafeiyu.pet && rm ~/Library/LaunchAgents/com.dafeiyu.pet.plist`
- **鼠标穿透**：macOS 上走 Qt 的 `WindowTransparentForInput`（等价 `NSWindow.ignoresMouseEvents`），
  开启后点不到鱼，从菜单栏托盘图标右键解除。
- **托盘图标**：macOS 没有右下角托盘，图标在屏幕右上角菜单栏。
- 用 `.app` 运行时系统可能弹一次「App 后台活动：可在后台运行」，这是 `LSUIElement` 应用在 macOS 15+
  的正常提示，允许即可。
- 精灵素材最高 306px，Retina 屏上会被放大，边缘会略糊（见「已知限制」）。

## 功能

- **三视图行走**：左右走用侧面（自动镜像）、向上走用背面、向下走用正面
- **三种模式**：自由散步 / 跟随鼠标 / 原地待着（右键菜单切换）
- **互动**：
  - 左键按住：拖拽（会侧身朝向拖动方向，松手会说话）
  - 单击：蹦跳 + 回嘴（互动台词）+ 弹出 🗨️ 聊天面板（5 秒无操作自动收起）
  - 双击：喂食面板（小鱼干 / 蛋糕 / 棒棒糖 / 团子 / 钻石）
  - 右键：完整菜单（模式 / 大小 / 喂食 / 说句话 / 设置 Key / 查看天气 / 设置城市 / 显示隐藏 / 回到屏幕内 / 鼠标穿透 / 置顶 / 开机自启 / 退出；托盘右键是同款菜单，穿透后可从托盘解除）
- **台词系统**：日常随机台词 + 互动回嘴 + 思维链心声（灰色斜体括号气泡，小概率冒出），全部取材自社区 DS 梗
- **细节**：呼吸 / 摇摆 / 蹦跳 / 进食动画、转向交叉淡化、加减速惯性、散步自动休息、说话冷却
- 托盘图标、窗口置顶、鼠标穿透、开机自启、配置记忆（`config.json`）；设置改动立即保存，穿透 / 置顶状态重启后自动恢复

### AI 对话

- 左键单击 → 点击 🗨️ → 弹出聊天输入框
- 调用 DeepSeek API（默认 `deepseek-chat` 模型），每句话不超过 25 字，风格贱兮兮但可爱
- 对话历史保留最近 40 条（自动记忆上下文）
- API Key 通过右键菜单「设置 Key」输入（密码框），保存到 `config.json`
- 也兼容其他 OpenAI 协议接口：修改 `config.json` 里的 `api_base` / `api_model` 即可
  （例如 `"api_base": "https://api.deepseek.com/v1"`、`"api_model": "deepseek-chat"`）
- 聊天期间鱼会暂停移动，但呼吸 / 摇摆 / 小动作照常

### 天气查询

- 右键菜单「查看天气」→ 后台线程调用 `wttr.in`，不会卡住桌宠
- 城市可在右键菜单「设置城市」里修改，也保存在 `config.json` 的 `"city"` 字段
- 鱼会气泡播报：「汕头今天 26°，天气多云」

### 系统状态监控

- **CPU**：超过 90% 时冒泡提醒
- **内存**：超过 95% 时冒泡提醒
- **显卡（NVIDIA）**：温度超过 80°C 时冒泡提醒（`pynvml` 读取）
- 检测间隔 10 秒，不频繁打扰

## 配置

首次运行会在程序目录生成 `config.json`。可参考 [`config.example.json`](config.example.json)：

| 字段 | 说明 |
|------|------|
| `mode` | `wander` 自由散步 / `follow` 跟随鼠标 / `still` 原地待着 |
| `size` | 大小倍率：`0.55` / `0.7` / `0.9` |
| `topmost` | 是否窗口置顶 |
| `passthrough` | 是否鼠标穿透 |
| `autostart` | 是否开机自启 |
| `x` / `y` | 上次位置 |
| `ds_api_key` | DeepSeek / OpenAI 协议 API Key |
| `api_base` | 接口地址，默认 `https://api.deepseek.com/v1` |
| `api_model` | 模型名，默认 `deepseek-chat` |
| `city` | 天气城市，默认 `汕头` |

运行日志写在程序目录的 `pet.log`，启动失败或异常时可先看这里。

macOS 用 `.app` 打包版运行时，程序目录在 `.app` 内部、按惯例只读，所以配置和日志改放
`~/Library/Application Support/大肥鱼桌宠/`（`config.json`、`pet.log` 都在那里）。源码运行仍是程序目录。

## 打包成独立 exe

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name dafeiyu-pet --add-data "sprites;sprites" --icon icon.ico 桌宠.py
```

产物在 `dist/dafeiyu-pet.exe`。推送 `v*` 标签时，GitHub Actions 也会自动构建并发布 Release（见 `.github/workflows/build-release.yml`）。

### 打包 macOS `.app`

```bash
pip install pyinstaller
pyinstaller --noconfirm 桌宠-macos.spec
```

产物在 `dist/大肥鱼桌宠.app`。`桌宠-macos.spec` 里写了 `LSUIElement=True`（不占 Dock，只留菜单栏图标）、
`NSHighResolutionCapable=True`，图标用 `icon.icns`。推送 `v*` 标签时，`build-macos` job 会把它压成
`dafeiyu-pet-macos.zip` 一起发布。

> 未做代码签名/公证，第一次打开会提示「无法验证开发者」，右键 →「打开」即可；
> 从网上下载的 zip 还可能有 quarantine 标记，必要时 `xattr -dr com.apple.quarantine 大肥鱼桌宠.app`。

## 更换形象

把新的三视图（白底）放到程序目录，然后：

```bash
python preprocess.py    # 白底抠图 + 统一高度
python preprocess2.py   # 边缘去污 + 预乘 alpha 缩放出各尺寸精灵
```

素材不在程序目录时，也可以传入路径：

```bash
python preprocess.py <素材目录> [输出目录]
```

## 文件说明

| 文件 | 说明 |
|------|------|
| 桌宠.py | 主程序（全部逻辑） |
| preprocess.py | 白底三视图抠图脚本 |
| preprocess2.py | 精灵边缘去污 + 多尺寸生成脚本 |
| sprites/ | 精灵图（正面/侧面/背面 各尺寸 + 图标） |
| platform_support.py | 平台差异（字体族 / 开机自启：Windows `.lnk`、macOS LaunchAgent） |
| 启动桌宠.bat | Windows 启动脚本（自动选择 venv 或系统 Python，缺环境会提示） |
| 启动桌宠.command | macOS 双击启动脚本（同上，优先 `.venv/bin/python`） |
| requirements.txt | 依赖 |
| config.example.json | 配置示例 |
| 桌宠.spec | PyInstaller 打包配置（Windows 单文件 exe） |
| 桌宠-macos.spec | PyInstaller 打包配置（macOS `.app`，`LSUIElement`） |
| icon.icns | macOS 应用图标（由 icon.ico 生成） |
| test_pet.py | 基础自动化测试（菜单 / 配置保存 / 喂食动画 / 天气异步） |
| tools/package_source.py | 打源码 zip（UTF-8 文件名，供 CI 使用） |
| .github/workflows/build-release.yml | 打 tag 自动构建 exe 并发布 Release |

## 测试

```bash
python test_pet.py
```

CI 在 Windows 和 macOS 两个 runner 上都跑同一套测试（`.github/workflows/test.yml`，`QT_QPA_PLATFORM=offscreen`），
macOS 专属用例（LaunchAgent plist、字体、鼠标穿透）只在 macOS 上执行。

## 常见问题

**双击 `启动桌宠.bat` 没反应 / 一闪而过**
先确认装了 Python 3.11+，安装时勾选「Add Python to PATH」。临时排查可在 cmd 里运行：

```bash
python 桌宠.py
```

缺什么依赖会直接报出来。也可以直接下载 Releases 里的 exe。

**缺少 PySide6**
```bash
python -m pip install -r requirements.txt
```

**天气获取失败**
`wttr.in` 在国内网络下偶尔不稳定，稍后重试或换个网络即可；失败不会卡住桌宠。

**开机自启没有生效**
确认程序所在路径没有被移动 / 删除；重新勾选一次「开机自启」会重建启动快捷方式
（Windows 是启动目录 `.lnk`，macOS 是 `~/Library/LaunchAgents/com.dafeiyu.pet.plist`）。

**macOS：双击 `.command` 提示「无法打开，因为无法验证开发者」**
右键 →「打开」一次即可；或在「系统设置 → 隐私与安全性」里点「仍要打开」。

**macOS：开了鼠标穿透后点不到鱼了**
从屏幕右上角菜单栏的托盘图标右键，取消「鼠标穿透（点不到它）」。

**macOS：`.app` 的 config.json 在哪**
`~/Library/Application Support/大肥鱼桌宠/config.json`（同目录还有 `pet.log`）。

## 贡献与致谢

- **AI 对话 / 天气查询 / 系统监控 / PyInstaller 打包配置**：由 [Cpanoe](https://github.com/Cpanoe) 通过 [PR#3](https://github.com/1190fasheqi/dafeiyu-pet/pull/3) 贡献（DeepSeek API 聊天、wttr.in 天气、CPU/内存/GPU 监控、桌宠.spec）。
- 合并时维护方修复：
  - 线程安全：DeepSeek 回复由后台线程直接调用 Qt 界面改为经队列转发主线程（`_say_queue`）
  - 配置保护：`config.json` 保持不入仓库（本地配置含 API Key，防止泄露）
- 桌面宠物朝向修复由 [B-A-A-GE](https://github.com/B-A-A-GE) 通过 [PR#1](https://github.com/1190fasheqi/dafeiyu-pet/pull/1) 提交（未合并，当前为维护方修复版）。

## 台词梗来源

台词均取自 DeepSeek / 鲸鱼娘 / 大肥鱼社区梗（D指导去吃饭、吃白饭、梁文锋会议三连、"才不是大肥鱼"、思维链心声等），感谢社区整活。

## 协议与声明

代码使用 MIT 协议。

角色形象为 DeepSeek「鲸鱼娘·大肥鱼」二创，仅供学习交流，请勿用于商业用途；形象版权归原作者所有。

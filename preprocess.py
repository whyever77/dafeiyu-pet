# -*- coding: utf-8 -*-
"""三视图抠图+规格化：白底 → 透明 PNG，统一高度，裁掉空白边。

用法：
    python preprocess.py [素材目录] [输出目录]

不放参数时，默认从脚本所在目录读取 正面.png / 侧面.png / 背面.png，
输出到脚本目录下的 sprites/。
"""
import os
import sys

from PIL import Image, ImageDraw

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else BASE_DIR
OUT = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.join(BASE_DIR, "sprites")
TARGET_H = 340  # 桌宠显示高度(px)

os.makedirs(OUT, exist_ok=True)

def cutout(path):
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    # 1) 从四角做连通域泛洪，把背景整片变透明（人物内部的白不受影响）
    for sx, sy in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        ImageDraw.floodfill(im, (sx, sy), (0, 0, 0, 0), thresh=30)
    # 2) 去白边：贴着透明区的亮像素也变透明（消除抗锯齿白晕）
    for _ in range(3):
        px = im.load()
        changed = False
        for y in range(h):
            for x in range(w):
                r, g, b, a = px[x, y]
                if a == 0:
                    continue
                if r > 215 and g > 215 and b > 215:
                    # 检查邻域是否有透明像素
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3] == 0:
                            px[x, y] = (0, 0, 0, 0)
                            changed = True
                            break
        if not changed:
            break
    # 3) 裁掉透明边
    bbox = im.getbbox()
    if bbox is None:
        raise RuntimeError(f"{path}: 抠图后为空！")
    im = im.crop(bbox)
    # 4) 统一高度
    w2, h2 = im.size
    scale = TARGET_H / h2
    im = im.resize((max(1, round(w2 * scale)), TARGET_H), Image.LANCZOS)
    return im

for name in ["正面", "侧面", "背面"]:
    src_path = os.path.join(SRC, f"{name}.png")
    if not os.path.exists(src_path):
        raise SystemExit(f"找不到素材：{src_path}\n请把 正面.png / 侧面.png / 背面.png 放到程序目录，"
                         f"或运行 python preprocess.py <素材目录>")
    im = cutout(src_path)
    out_path = os.path.join(OUT, f"{name}.png")
    im.save(out_path)
    print(f"{name}: {im.size} -> {out_path}")

# 托盘小图标
Icon = cutout(os.path.join(SRC, "正面.png")).resize((64, 64), Image.LANCZOS)
Icon.save(os.path.join(OUT, "icon.png"))
print("icon: 64x64")

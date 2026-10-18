# -*- coding: utf-8 -*-
"""打源码 zip，使用 UTF-8 文件名，避免 Windows Compress-Archive 的中文乱码。"""
import os
import zipfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "dafeiyu-pet-source.zip")

FILES = [
    "桌宠.py",
    "preprocess.py",
    "preprocess2.py",
    "test_pet.py",
    "启动桌宠.bat",
    "requirements.txt",
    "README.md",
    "LICENSE",
    "icon.ico",
    "桌宠.spec",
    "config.example.json",
    ".gitignore",
    ".gitattributes",
    "docs/screenshot.png",
    "tools/package_source.py",
    ".github/workflows/build-release.yml",
    ".github/workflows/test.yml",
]


def collect():
    files = list(FILES)
    for root, _, names in os.walk(os.path.join(BASE, "sprites")):
        for name in names:
            files.append(os.path.relpath(os.path.join(root, name), BASE))
    return sorted(set(files))


def main():
    files = collect()
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in files:
            path = os.path.join(BASE, rel)
            if os.path.exists(path):
                z.write(path, rel.replace(os.sep, "/"))
    print(f"{OUT} ({len(files)} files, {os.path.getsize(OUT) // 1024} KB)")


if __name__ == "__main__":
    main()

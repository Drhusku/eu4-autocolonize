# -*- coding: utf-8 -*-
"""产出 mod 图标资产：thumbnail.png（640，Steam/mod 列表用）+ 游戏内小图标。"""
import os, sys, shutil
from PIL import Image
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass

BASE = r"E:\AI\eu4_autocolonize"
ART = os.path.join(BASE, "artwork")
FIN = os.path.join(ART, "final")
SRC = os.path.join(FIN, "v4_a_640.png")

# 1) mod 缩略图：EU4 惯例 640x640
thumb = os.path.join(BASE, "thumbnail.png")
im = Image.open(SRC).convert("RGBA")
im.save(thumb, "PNG")
print("thumbnail.png  %s  %dx%d  %d bytes" % (thumb, im.width, im.height, os.path.getsize(thumb)))

# 2) 游戏内图标（决议/事件可用）：多尺寸
gfx = os.path.join(BASE, "gfx", "interface")
os.makedirs(gfx, exist_ok=True)
for size, name in ((64, "autocolonize_icon_64.png"), (32, "autocolonize_icon_32.png")):
    small = im.resize((size, size), Image.LANCZOS)
    p = os.path.join(gfx, name)
    small.save(p, "PNG")
    print("%-32s %dx%d  %d bytes" % (name, size, size, os.path.getsize(p)))

# 3) 保留一张不裁切的方形大图（README 用）
readme_img = os.path.join(ART, "final", "icon_readme_512.png")
im.resize((512, 512), Image.LANCZOS).save(readme_img, "PNG")
print("icon_readme_512.png  %d bytes" % os.path.getsize(readme_img))

# 4) 记录素材来源与提示词（供 README/许可说明）
import json
manifest = {
    "selected": "v4_a",
    "note": "由智谱 CogView 生成，经圆形裁切去水印与缩放处理",
    "model": "cogview-3-flash / cogview-4",
    "prompt_file": "candidates/prompts_round7.json",
    "outputs": {
        "thumbnail.png": "640x640 mod 列表缩略图",
        "gfx/interface/autocolonize_icon_64.png": "游戏内图标 64px",
        "gfx/interface/autocolonize_icon_32.png": "游戏内图标 32px",
        "artwork/final/icon_readme_512.png": "README 配图",
    },
}
mp = os.path.join(ART, "ARTWORK_MANIFEST.json")
with open(mp, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
print("manifest -> %s" % mp)

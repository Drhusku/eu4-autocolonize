# -*- coding: utf-8 -*-
"""把用户提供的图标接入 mod 资产链。"""
import os, shutil, sys, json
from PIL import Image
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass

BASE = r"E:\AI\eu4_autocolonize"
USER = os.path.join(BASE, "v4_a_640.png")
ART  = os.path.join(BASE, "artwork")
FIN  = os.path.join(ART, "final")
GFX  = os.path.join(BASE, "gfx", "interface")
os.makedirs(FIN, exist_ok=True)
os.makedirs(GFX, exist_ok=True)

# 1) 备份 Captain 原版缩略图
old = os.path.join(BASE, "thumbnail.png")
if os.path.isfile(old):
    bak = os.path.join(FIN, "thumbnail_captain_backup.png")
    shutil.copy2(old, bak)
    print("backup ->", bak)

# 2) 用户版本设为 thumbnail.png
im = Image.open(USER).convert("RGBA")
im.save(os.path.join(BASE, "thumbnail.png"), "PNG")
print("thumbnail.png <- user icon  %dx%d" % im.size)

# 3) 存一份到 artwork/final 存档
im.save(os.path.join(FIN, "icon_user_final_640.png"), "PNG")
print("archived -> artwork/final/icon_user_final_640.png")

# 4) 游戏内小图标
for size in (64, 32):
    p = os.path.join(GFX, "autocolonize_icon_%d.png" % size)
    im.resize((size, size), Image.LANCZOS).save(p, "PNG")
    print("gfx -> %s" % p)

# 5) README 配图
im.resize((512, 512), Image.LANCZOS).save(os.path.join(FIN, "icon_readme_512.png"), "PNG")

# 6) 更新素材清单
mp = os.path.join(ART, "ARTWORK_MANIFEST.json")
man = json.load(open(mp, encoding="utf-8")) if os.path.isfile(mp) else {}
man["selected"] = "user_final (用户自制)"
man["note"] = "最终图标由用户提供：在 Captain 生成的 v4_a 基础上加了绿色「自动殖民」标题，殖民官表情改为笑哭、玩家为闭眼吐舌。"
man["outputs"] = {
    "thumbnail.png": "640x640 mod 列表缩略图（= 用户版本）",
    "gfx/interface/autocolonize_icon_64.png": "游戏内图标 64px",
    "gfx/interface/autocolonize_icon_32.png": "游戏内图标 32px",
    "artwork/final/icon_user_final_640.png": "用户版本存档",
    "artwork/final/icon_readme_512.png": "README 配图",
    "artwork/final/thumbnail_captain_backup.png": "Captain 初版缩略图备份",
}
json.dump(man, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("manifest updated")

# 7) 校验最终 thumbnail
t = Image.open(os.path.join(BASE, "thumbnail.png"))
print("VERIFY thumbnail.png: %s %s %s" % (t.format, t.mode, t.size))

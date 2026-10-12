# -*- coding: utf-8 -*-
"""图标后处理：圆形裁切去水印 + 输出 EU4 mod 缩略图尺寸。

水印「AI生成」位于右下角圆形画框之外，圆形裁切后自然消失。
"""
import os, sys
from PIL import Image, ImageDraw
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass

BASE = r"E:\AI\eu4_autocolonize\artwork"
CAND = os.path.join(BASE, "candidates")
OUT = os.path.join(BASE, "final")
os.makedirs(OUT, exist_ok=True)


def circular_crop(src, dst, out_size, cx=None, cy=None, radius=None, feather=2):
    """把方形图裁成圆形透明图标。"""
    im = Image.open(src).convert("RGBA")
    w, h = im.size
    cx = w // 2 if cx is None else cx
    cy = h // 2 if cy is None else cy
    radius = min(w, h) // 2 if radius is None else radius

    # 先按圆的包围盒裁出方形区域
    box = (cx - radius, cy - radius, cx + radius, cy + radius)
    box = (max(0, box[0]), max(0, box[1]), min(w, box[2]), min(h, box[3]))
    sq = im.crop(box)
    sq = sq.resize((out_size, out_size), Image.LANCZOS)

    # 生成圆形遮罩（4x 超采样抗锯齿）
    ss = 4
    mask = Image.new("L", (out_size * ss, out_size * ss), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((0, 0, out_size * ss - 1, out_size * ss - 1), fill=255)
    mask = mask.resize((out_size, out_size), Image.LANCZOS)

    out = Image.new("RGBA", (out_size, out_size), (0, 0, 0, 0))
    out.paste(sq, (0, 0), mask)
    out.save(dst, "PNG")
    return out


# 检测金框外沿：沿中心水平/垂直线找亮度突变
def find_frame_radius(path):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    px = im.load()
    cx, cy = w // 2, h // 2
    # 从中心向外扫描，找到最后一次出现"金色"的位置
    def is_gold(p):
        r, g, b = p
        return r > 90 and g > 70 and b < 130 and r >= b + 20
    last = 0
    for x in range(cx, w):
        if is_gold(px[x, cy]):
            last = x
    horiz = last - cx
    last = 0
    for y in range(cy, h):
        if is_gold(px[cx, y]):
            last = y
    vert = last - cy
    return cx, cy, max(horiz, vert)


for name in ["v4_a", "v5_d", "final_a", "v2_a"]:
    src = os.path.join(CAND, name + ".png")
    if not os.path.isfile(src):
        print("skip %s (missing)" % name)
        continue
    cx, cy, r = find_frame_radius(src)
    print("%s: center=(%d,%d) frame_radius=%d" % (name, cx, cy, r))
    # 用检测到的半径 +2px 余量
    for size in (640, 256):
        dst = os.path.join(OUT, "%s_%d.png" % (name, size))
        circular_crop(src, dst, size, cx=cx, cy=cy, radius=r + 2)
        print("   -> %s" % dst)

# 验证水印是否已去除：检查成品右下角区域是否有近白色像素
print("\n--- watermark check (bottom-right quadrant) ---")
for f in sorted(os.listdir(OUT)):
    p = os.path.join(OUT, f)
    im = Image.open(p).convert("RGBA")
    w, h = im.size
    px = im.load()
    whites = 0
    for x in range(int(w * 0.72), w):
        for y in range(int(h * 0.72), h):
            r_, g_, b_, a_ = px[x, y]
            if a_ > 200 and r_ > 200 and g_ > 200 and b_ > 200:
                whites += 1
    print("%-22s white_px_in_corner=%d" % (f, whites))

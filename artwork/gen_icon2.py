# -*- coding: utf-8 -*-
"""第二轮：强化「流汗黄豆」表情特征。"""
import json, os, sys, time
from urllib import request, error
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass

API = "https://open.bigmodel.cn/api/paas/v4/images/generations"
KEY = open(os.path.expanduser("~/.zhipu_key")).read().strip()
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "candidates")
os.makedirs(OUT, exist_ok=True)

# 流汗黄豆 = 经典 emoji 梗图脸：完全正圆的扁平黄色脸、两个小黑点眼睛、
# 尴尬的僵硬微笑、额角挂一颗巨大的蓝色汗珠
MEME = ("它们的头是完美正圆形的扁平黄色 emoji 脸，完全不是真人脸："
        "两个黑色小圆点眼睛，一条僵硬的尴尬微笑嘴线，"
        "额角挂着一颗巨大的蓝色汗珠，表情无语、无奈、强颜欢笑，"
        "就像网络流行的「流汗黄豆」表情包。")

STYLE = "欧式复古油画风格的游戏圆形徽章图标，金色做旧圆形边框，深色背景，构图紧凑居中，幽默诙谐。"

PROMPTS = [
    ("cand_05",
     STYLE + " 画面中央一位戴黑色三角帽、穿深色大衣的欧洲殖民时代玩家领主，"
     "右手高举一根皮鞭，表情得意洋洋、神气十足，身材高大。"
     "他身前并排站着三个矮小的殖民官，三个人穿着殖民时代的制服，"
     + MEME + " 三个殖民官仰头看着玩家，一副被逼无奈的样子。"),
    ("cand_06",
     STYLE + " 一位戴三角帽的玩家角色站在正中央，右手扬起皮鞭作势要抽，神情威风凛凛。"
     "他面前三个小个子殖民官缩成一团，穿着深色殖民官制服，"
     + MEME + " 三个殖民官的表情高度统一，都是同一种无语的流汗黄豆脸。"),
    ("cand_07",
     STYLE + " 中央是一个得意洋洋的殖民时代玩家，手举皮鞭，姿态强势。"
     "画面下方三个小小的殖民官并排站着，戴殖民时代帽子、穿制服，"
     + MEME + " 强烈的喜剧对比：玩家高大得意，殖民官矮小崩溃。"),
    ("cand_08",
     STYLE + " 一位戴黑色宽檐帽的玩家领主居中，手握皮鞭高高扬起，笑容得意。"
     "他身前三个殖民官排成一排，全部是圆形的黄色 emoji 脸，"
     "黑色小圆点眼睛、僵硬的尴尬微笑、额角一颗巨大的蓝色汗珠，"
     "表情极度无语，穿着殖民时代的深色制服和帽子。"),
]

def gen(prompt, size="1024x1024", retries=3):
    payload = json.dumps({"model": "cogview-3-flash", "prompt": prompt, "size": size}).encode()
    req = request.Request(API, data=payload, headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    last = None
    for i in range(retries):
        try:
            with request.urlopen(req, timeout=180) as r:
                return json.loads(r.read().decode())
        except error.HTTPError as e:
            last = "HTTP %s: %s" % (e.code, e.read().decode()[:300])
        except Exception as e:
            last = "%s: %s" % (type(e).__name__, str(e)[:200])
        time.sleep(3 * (i + 1))
    raise RuntimeError(last)

def download(url, path):
    req = request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with request.urlopen(req, timeout=180) as r:
        data = r.read()
    open(path, "wb").write(data)
    return len(data)

from PIL import Image
meta = []
for name, prompt in PROMPTS:
    print("--- %s" % name, flush=True)
    try:
        d = gen(prompt)
        p = os.path.join(OUT, name + ".png")
        n = download(d["data"][0]["url"], p)
        im = Image.open(p); im = im.convert("RGB"); im.save(p, "PNG")
        print("    OK %d bytes" % n, flush=True)
        meta.append({"name": name, "prompt": prompt, "bytes": n})
    except Exception as e:
        print("    FAIL %s" % e, flush=True)
        meta.append({"name": name, "prompt": prompt, "error": str(e)})
    time.sleep(2)

with open(os.path.join(OUT, "prompts_round2.json"), "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)
print("done %d/%d" % (sum(1 for m in meta if "error" not in m), len(meta)))

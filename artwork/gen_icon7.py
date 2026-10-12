# -*- coding: utf-8 -*-
"""第七轮：三张完全相同的 😅 脸 + 玩家挥鞭得意。用短句、强约束。"""
import json, os, sys, time
from urllib import request, error
from PIL import Image
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass

API = "https://open.bigmodel.cn/api/paas/v4/images/generations"
KEY = open(os.path.expanduser("~/.zhipu_key")).read().strip()
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "candidates")
os.makedirs(OUT, exist_ok=True)

# 关键：强调「三张脸一模一样，像复制粘贴」+ 😅 的具体形态
FACE = ("三个殖民官的脸是三颗一模一样的黄色圆形 emoji 表情头，像复制粘贴出来的："
        "纯黄色、光滑扁平、没有鼻子，两个小小的黑色圆点眼睛，"
        "嘴巴是一条短而僵硬的尴尬微笑，额头右上角挂着一颗蓝色水滴汗珠。"
        "这就是经典的 😅 流汗黄豆表情。")

STYLE = "游戏徽章图标，金色圆形画框，暗色背景，卡通讽刺画风。"

PROMPTS = [
    ("v4_a",
     STYLE + " 一位穿 18 世纪欧洲军官大衣、戴黑色三角帽的玩家领主站在画面中央，"
     "右手高举一根皮鞭，脸上是得意洋洋的大笑。"
     + FACE + " 三颗黄脸并排在他身前，穿着小号殖民官制服戴着小帽子，仰头看他。"),
    ("v4_b",
     STYLE + " 画面中央的欧洲玩家领主高举皮鞭、咧嘴得意大笑，戴着三角帽、穿蓝色大衣。"
     "他身前下方并排站着三个矮小的殖民官，三颗脑袋都是同样的黄色圆形 emoji 脸："
     "黑色小圆点眼睛、尴尬的僵硬微笑、额头一颗蓝色汗珠，表情无语无奈。"
     "三张脸完全相同。他们穿 18 世纪殖民官制服、戴帽子。"),
    ("v4_c",
     STYLE + " 一位戴三角帽的欧洲玩家高高举起皮鞭，笑容得意嚣张。"
     "他脚下三个小殖民官并排仰头，三颗黄色圆形 emoji 脑袋完全一样——"
     "黑色圆点眼、僵硬的尴尬微笑、额角一颗蓝色汗珠，一副无语到极点的样子。"
     "殖民官穿 18 世纪制服戴小帽。"),
    ("v4_d",
     STYLE + " 中央一位得意大笑的欧洲玩家领主，手举皮鞭过头顶，戴三角帽穿深色大衣。"
     "画面下方三个小个子殖民官排成一排，三人都是同一张黄色圆形 emoji 脸："
     "两点黑眼睛、尴尬假笑、额头一颗大蓝汗珠，表情无语。"
     "他们穿着殖民官制服和小帽子。"),
]

def gen(prompt, model="cogview-4", size="1024x1024", retries=3):
    payload = json.dumps({"model": model, "prompt": prompt, "size": size}).encode()
    req = request.Request(API, data=payload, headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    last = None
    for i in range(retries):
        try:
            with request.urlopen(req, timeout=200) as r:
                return json.loads(r.read().decode())
        except error.HTTPError as e:
            last = "HTTP %s: %s" % (e.code, e.read().decode()[:300])
        except Exception as e:
            last = "%s: %s" % (type(e).__name__, str(e)[:200])
        time.sleep(4 * (i + 1))
    raise RuntimeError(last)

def download(url, path):
    req = request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with request.urlopen(req, timeout=200) as r:
        data = r.read()
    open(path, "wb").write(data)
    return len(data)

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

with open(os.path.join(OUT, "prompts_round7.json"), "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)
print("done %d/%d" % (sum(1 for m in meta if "error" not in m), len(meta)))

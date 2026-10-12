# -*- coding: utf-8 -*-
"""第四轮：用 cogview-4 生成高精度图标，强化汗珠细节。"""
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

EMOJI = ("他们三人的脑袋是正圆形的黄色 emoji 表情头，光滑扁平像塑料 emoji，"
         "是经典的「流汗黄豆」表情：两只黑色小圆点眼睛，一条尴尬僵硬的微笑弧线，"
         "额头侧边挂着一颗又大又亮的蓝色水滴汗珠。三个人的表情一模一样，无语又无奈。"
         "他们穿着 18 世纪欧洲殖民官制服、戴着帽子，身材矮小。")

STYLE = ("复古油画质感的游戏徽章图标，金色雕花圆形画框，暗色背景，"
         "构图紧凑居中，人物半身，讽刺幽默画风，细节精致。")

PROMPTS = [
    ("final_a",
     STYLE + " 画面中央一位 18 世纪欧洲玩家领主，戴黑色三角帽、穿深蓝色军官大衣，"
     "右手把皮鞭高高扬过头顶，露出得意洋洋、心满意足的坏笑，身材高大魁梧。"
     + EMOJI + " 三个殖民官并排站在他身前，仰头看着他，一副被迫无奈的表情。"),
    ("final_b",
     STYLE + " 一位戴三角帽、穿深色大衣的欧洲玩家站在正中，单手高举皮鞭作势要抽，"
     "神态傲慢得意、笑容满面。他身前下方站着三个矮小的殖民官，"
     "三个脑袋都是正圆黄色 emoji 脸，两只黑色小圆点眼睛、尴尬僵硬的微笑、"
     "额角一颗巨大的蓝色汗珠，表情无语，都穿着殖民时代的深色制服和帽子。"),
    ("final_c",
     STYLE + " 中央是一位手举皮鞭的殖民时代欧洲领主，表情得意洋洋、威风凛凛。"
     "他面前三个小个子殖民官排成一排，三人头顶都是巨大的黄色圆形 emoji 表情，"
     "正是「流汗黄豆」：圆黄脸、两点黑眼睛、僵硬的微笑、额角挂着一颗大蓝汗珠，"
     "表情极其无语。他们穿殖民官制服、戴帽子，被玩家吓得缩成一团。"),
    ("final_d",
     STYLE + " 一位头戴黑色三角帽的欧洲玩家领主站在中央，右手握鞭高高举起，"
     "脸上是得意的笑。画面下方并排三个矮小的殖民官，"
     "每人的头都是正圆形的黄色 emoji 表情头——两只黑色小圆点眼睛、"
     "一条尴尬僵硬的微笑、额头侧边一颗又大又亮的蓝色汗珠，表情无语到极点。"
     "他们穿着 18 世纪殖民官制服，戴着帽子，仰头看着玩家。"),
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
        print("    OK %d bytes %sx%s" % (n, im.width, im.height), flush=True)
        meta.append({"name": name, "prompt": prompt, "bytes": n})
    except Exception as e:
        print("    FAIL %s" % e, flush=True)
        meta.append({"name": name, "prompt": prompt, "error": str(e)})
    time.sleep(2)

with open(os.path.join(OUT, "prompts_round4.json"), "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)
print("done %d/%d" % (sum(1 for m in meta if "error" not in m), len(meta)))

# -*- coding: utf-8 -*-
"""第六轮（收官）：死鱼眼 + 尴尬抿嘴假笑 + 额头一颗汗珠 = 标准「无语流汗黄豆」。"""
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

# 「无语流汗黄豆」三要素：半睁的死鱼眼 + 尴尬抿嘴的假笑 + 额头一颗蓝色汗珠
FACE = ("他们三人的脑袋是正圆形的鲜黄色 emoji 表情头，光滑扁平像塑料表情包。"
        "表情是网络梗图「流汗黄豆」：两只半睁着的黑色死鱼眼（眼神空洞、无语、生无可恋），"
        "嘴巴是一条尴尬僵硬的抿嘴假笑弧线（闭嘴微笑，不是张嘴大笑，也没有眼泪），"
        "额头侧边挂着一颗又大又亮的蓝色水滴形汗珠。"
        "三张脸的表情完全一样，都是无语到极点、强颜欢笑的样子。"
        "注意：绝对不要眼泪，只要额头一颗汗珠。"
        "他们穿着 18 世纪欧洲殖民官制服并戴着帽子，身材矮小。")

STYLE = "复古油画质感的游戏徽章图标，金色雕花圆形画框，暗色背景，构图紧凑居中，讽刺幽默画风。"

PROMPTS = [
    ("v3_a",
     STYLE + " 画面中央一位 18 世纪欧洲玩家领主，戴黑色三角帽、穿深蓝色军官大衣，"
     "右手把皮鞭高高扬过头顶作势要抽下去，脸上是得意洋洋、心满意足的坏笑，身材高大魁梧。"
     + FACE + " 三个殖民官并排站在他身前下方，仰头看着他，一副被迫无奈的表情。"),
    ("v3_b",
     STYLE + " 一位戴三角帽、穿深色大衣的欧洲玩家站在正中，单手高举皮鞭，"
     "神态傲慢得意、笑容满面。他身前下方并排站着三个矮小的殖民官，"
     + FACE + " 他们仰头看着玩家，表情无语到极点。"),
    ("v3_c",
     STYLE + " 中央一位戴黑色三角帽的欧洲玩家，右手扬鞭，笑得十分得意开心。"
     "他身前三个矮小的殖民官排成一排，三颗脑袋都是正圆形的鲜黄色 emoji 表情头，"
     "半睁的黑色死鱼眼、尴尬僵硬的抿嘴假笑、额头侧边一颗巨大的蓝色汗珠，"
     "三人表情完全相同，无语又无奈，都穿着 18 世纪殖民官制服、戴着帽子。"),
    ("v3_d",
     STYLE + " 一位得意洋洋的欧洲玩家领主高举皮鞭站在中间，笑容满面、神气十足。"
     "他脚边三个小殖民官挤在一起，三个圆圆的鲜黄色 emoji 脑袋仰着，"
     "每个都是「流汗黄豆」表情：圆黄脸、半睁的死鱼眼、尴尬的抿嘴假笑、"
     "额角挂着一颗大蓝色汗珠，一副被折磨到无语的滑稽样子，穿殖民官制服戴帽子。"),
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

with open(os.path.join(OUT, "prompts_round6.json"), "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)
print("done %d/%d" % (sum(1 for m in meta if "error" not in m), len(meta)))

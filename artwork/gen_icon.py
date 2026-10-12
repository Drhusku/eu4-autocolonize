# -*- coding: utf-8 -*-
"""生成 EU4 自动殖民 mod 图标候选图（智谱 CogView）。

用法: python gen_icon.py
输出: artwork/candidates/cand_XX.png + artwork/candidates/prompts.json
"""
import json, os, sys, time
from urllib import request, error

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

API = "https://open.bigmodel.cn/api/paas/v4/images/generations"
KEY = open(os.path.expanduser("~/.zhipu_key")).read().strip()
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "candidates")
os.makedirs(OUT, exist_ok=True)

STYLE = ("欧式复古油画风格的游戏圆形徽章图标，金色做旧圆形边框，深色背景，"
         "构图紧凑居中，人物半身像，适合做游戏 mod 图标，画面幽默诙谐。")

PROMPTS = [
    ("cand_01",
     STYLE + " 画面中央一位戴着黑色三角帽、穿深色大衣的欧洲殖民时代玩家角色，"
     "右手高高举起一根皮鞭，表情得意洋洋、神气十足。"
     "他面前并排站着三个殖民官，三个殖民官的脸都是网络流行的流汗黄豆表情："
     "圆圆的黄色脸庞、尴尬的苦笑嘴角、额头挂着一滴巨大的汗珠，一副无语无奈、"
     "被逼无奈的表情。三个殖民官身材矮小，仰头看着玩家。卡通夸张风格。"),
    ("cand_02",
     STYLE + " 一位头戴三角帽、身披深色斗篷的玩家领主站在画面中央，"
     "手中握着一条卷起的鞭子，神情威风。"
     "他身前三个小小的殖民官低着头，每个人的脸都是流汗黄豆表情——"
     "黄色圆脸、僵硬的微笑、脑门上挂着一滴大汗珠，眼神无语。"
     "画面像一幅讽刺漫画，人物比例夸张，玩家高大、殖民官矮小。"),
    ("cand_03",
     STYLE + " 一个表情威严的玩家角色手持皮鞭站在中间，"
     "三个殖民官围在他身边，全部长着流汗黄豆脸：黄色圆形脸孔、"
     "嘴角尴尬抽搐、额角一滴巨大的汗珠往下流，表情极其无语。"
     "殖民官们戴着殖民时代的帽子、穿着当时的服装。"
     "整体是轻松搞笑的卡通画风，金色圆形边框包裹整个场景。"),
    ("cand_04",
     STYLE + " 中央是一位戴三角帽的殖民时代玩家，手中鞭子扬起，表情满意而强势。"
     "他脚下前方三个小个子殖民官挤在一起，三张脸都是同一个流汗黄豆表情："
     "圆黄脸、无语的苦笑、额头一颗大汗珠。"
     "强烈的喜剧对比，玩家得意、殖民官崩溃无奈。油画笔触，明暗对比强烈。"),
]


def gen(prompt, size="1024x1024", retries=3):
    payload = json.dumps({"model": "cogview-3-flash", "prompt": prompt, "size": size}).encode()
    req = request.Request(API, data=payload, headers={
        "Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
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
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


meta = []
for name, prompt in PROMPTS:
    print("--- generating %s ..." % name, flush=True)
    try:
        d = gen(prompt)
        url = d["data"][0]["url"]
        p = os.path.join(OUT, name + ".png")
        n = download(url, p)
        print("    OK %s  %d bytes" % (p, n), flush=True)
        meta.append({"name": name, "prompt": prompt, "url": url, "bytes": n, "file": p})
    except Exception as e:
        print("    FAIL %s" % e, flush=True)
        meta.append({"name": name, "prompt": prompt, "error": str(e)})
    time.sleep(2)

with open(os.path.join(OUT, "prompts.json"), "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)
print("done: %d ok / %d total" % (sum(1 for m in meta if "error" not in m), len(meta)))

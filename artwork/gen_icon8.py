# -*- coding: utf-8 -*-
"""第八轮（用免费 flash 模型）：v4_a 构图微调。"""
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

FACE = ("三个殖民官并排站在画面下半部、完整地显示在画框内，"
        "他们三颗脑袋是三张完全相同的黄色圆形 emoji 表情脸："
        "纯黄色、光滑扁平、没有鼻子，两个黑色小圆点眼睛，"
        "嘴巴是尴尬僵硬的抿嘴假笑，每张脸的额头侧边各挂着一颗蓝色水滴汗珠。"
        "三张脸表情一模一样，都是无语、无奈、强颜欢笑。")

STYLE = "游戏徽章图标，粗金圆形画框，深蓝绿色背景，卡通讽刺画风，构图完整居中。"

PROMPTS = [
    ("v5_a",
     STYLE + " 一位穿深蓝色 18 世纪军官大衣、戴黑色三角帽的玩家领主站在画面中央偏上，"
     "右手把皮鞭高高扬过头顶，脸上是得意洋洋的大笑。" + FACE),
    ("v5_b",
     STYLE + " 画面中央偏上的欧洲玩家领主高举皮鞭过头顶，咧嘴得意大笑，"
     "戴黑色三角帽、穿深蓝色大衣、系白色领巾。"
     "他身前下方三个矮小的殖民官完整并排站立，三颗脑袋都是相同的黄色圆形 emoji 脸："
     "黑色小圆点眼睛、尴尬僵硬的抿嘴假笑、额角各一颗蓝色汗珠，表情无语无奈。"
     "他们穿小号殖民官制服、戴小帽子。"),
    ("v5_c",
     STYLE + " 一位戴黑色三角帽的欧洲玩家高高举起皮鞭，笑容得意嚣张，穿深蓝大衣。"
     "他脚下三个小殖民官完整并排仰头，三颗黄色圆形 emoji 脑袋完全相同——"
     "黑色圆点眼、尴尬的抿嘴假笑、额角各一颗蓝色汗珠，无语到极点。"
     "殖民官穿 18 世纪制服戴小帽。"),
    ("v5_d",
     STYLE + " 中央一位得意大笑的欧洲玩家领主，手举皮鞭过头顶，戴三角帽穿深蓝大衣。"
     "画面下方三个小个子殖民官完整排成一排，三人都是同一张黄色圆形 emoji 脸："
     "两点黑眼睛、尴尬抿嘴假笑、额头各一颗蓝汗珠，表情无语。"
     "他们穿着殖民官制服和小帽子。"),
]

def gen(prompt, model="cogview-3-flash", size="1024x1024", retries=3):
    payload = json.dumps({"model": model, "prompt": prompt, "size": size}).encode()
    req = request.Request(API, data=payload, headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    last = None
    for i in range(retries):
        try:
            with request.urlopen(req, timeout=200) as r:
                return json.loads(r.read().decode())
        except error.HTTPError as e:
            last = "HTTP %s: %s" % (e.code, e.read().decode()[:250])
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

with open(os.path.join(OUT, "prompts_round8.json"), "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)
print("done %d/%d" % (sum(1 for m in meta if "error" not in m), len(meta)))

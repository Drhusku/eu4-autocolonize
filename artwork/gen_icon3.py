# -*- coding: utf-8 -*-
"""第三轮：锁定「流汗黄豆」emoji 脸 + 玩家挥鞭。"""
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

# 「流汗黄豆」= 经典 😅 emoji：正圆扁平黄色脸、两点黑眼睛、僵硬的尴尬微笑、
# 额角一颗巨大的蓝色汗珠。关键是「emoji 质感」而非真人脸。
EMOJI = ("他们的脑袋是三个一模一样的正圆形黄色 emoji 表情头，表面光滑扁平像塑料 emoji，"
         "完全是 😅 这个表情的样子：两个黑色小圆点眼睛，一条僵硬尴尬的微笑弧线嘴，"
         "额头侧面挂着一颗巨大的蓝色泪滴状汗珠。表情无语、无奈、强颜欢笑。"
         "三个殖民官穿着 18 世纪欧洲殖民官制服并戴着帽子，身体矮小。")

STYLE = "欧式复古油画风格游戏徽章图标，金色做旧圆形画框，深色背景，构图紧凑居中，幽默讽刺画风。"

PROMPTS = [
    ("cand_09",
     STYLE + " 画面正中一位 18 世纪欧洲玩家领主，戴黑色三角帽、穿深蓝色大衣，"
     "右手把一根皮鞭高高举过头顶准备抽下，脸上是得意洋洋、心满意足的坏笑，身材高大。"
     + EMOJI + " 三个殖民官并排站在他身前下方，仰头看着他，一副被逼无奈的样子。"),
    ("cand_10",
     STYLE + " 一位戴三角帽的欧洲玩家站在中央，单手扬起皮鞭，神态傲慢得意。"
     + EMOJI + " 三个殖民官在他面前排成一排瑟瑟发抖，全部顶着那张无语的流汗黄豆脸。"),
    ("cand_11",
     STYLE + " 中央是一位手举皮鞭、表情满意的殖民时代欧洲领主。"
     "他身前三个矮小的殖民官，每人头上都是一个巨大的圆形黄色 emoji 表情，"
     "那表情正是 😅：圆黄脸、两点黑眼睛、尴尬僵硬的微笑、额角一颗大汗珠，"
     "三个人表情完全一致，都是无语到极点的流汗黄豆。他们穿着殖民时代制服戴帽子。"),
    ("cand_12",
     STYLE + " 一位得意洋洋的欧洲玩家领主高举皮鞭站在中间，笑容满面。"
     "他脚边三个小殖民官挤在一起，三个圆圆的黄色 emoji 脑袋仰着，"
     "每个都是 😅 表情：扁平正圆黄脸、黑色小点眼睛、僵硬的微笑、"
     "额角挂着一颗大蓝色汗珠，一副被折磨到无语的滑稽样子，穿殖民官制服戴帽子。"),
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

with open(os.path.join(OUT, "prompts_round3.json"), "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)
print("done %d/%d" % (sum(1 for m in meta if "error" not in m), len(meta)))

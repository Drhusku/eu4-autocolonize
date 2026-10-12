# -*- coding: utf-8 -*-
"""探测可用的图像生成模型。"""
import json, os, sys
from urllib import request, error
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
KEY = open(os.path.expanduser("~/.zhipu_key")).read().strip()

def try_model(model, prompt="a red circle", size="1024x1024"):
    payload = json.dumps({"model": model, "prompt": prompt, "size": size}).encode()
    req = request.Request("https://open.bigmodel.cn/api/paas/v4/images/generations",
                          data=payload, headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    try:
        with request.urlopen(req, timeout=120) as r:
            d = json.loads(r.read().decode())
            return "OK"
    except error.HTTPError as e:
        return "HTTP %s %s" % (e.code, e.read().decode()[:200])
    except Exception as e:
        return "%s %s" % (type(e).__name__, str(e)[:150])

for m in ["cogview-4-250304", "cogview-4", "cogview-3-flash", "cogview-3-plus", "cogview-3"]:
    print("%-22s -> %s" % (m, try_model(m)))

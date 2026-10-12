# -*- coding: utf-8 -*-
"""独立验证 T2 的「1444 无主空土省数」统计是否可靠。

方法：直接解析 history/provinces 与 common/tradenodes，不依赖 T2 的中间数据。
"""
import os, re, sys, glob, json
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass

EU4 = r"E:\SteamLibrary\steamapps\common\Europa Universalis IV"
HP = os.path.join(EU4, "history", "provinces")
TN = os.path.join(EU4, "common", "tradenodes", "00_tradenodes.txt")

def read(p):
    return open(p, "rb").read().decode("cp1252", errors="replace")

# ---------- 1. 解析每个省份 1444 的 owner ----------
# EU4 history 格式：顶层 owner = XXX 是默认值；日期块内 owner 覆盖。
prov_owner = {}      # pid -> owner or None(无主)
files = glob.glob(os.path.join(HP, "*.txt"))
for f in files:
    base = os.path.basename(f)
    m = re.match(r"^(\d+)\s*-\s*", base)
    if not m:
        continue
    pid = int(m.group(1))
    txt = read(f)
    # 顶层 owner（第一个日期块之前）
    head = re.split(r"(?m)^\s*\d+\.\d+\.\d+\s*=\s*\{", txt)[0]
    top = re.search(r"(?m)^\s*owner\s*=\s*([A-Z0-9]{3})", head)
    owner = top.group(1) if top else None
    # 找 <=1444.11.11 的最后一个日期块里的 owner
    for dm in re.finditer(r"(?ms)^\s*(\d+)\.(\d+)\.(\d+)\s*=\s*\{(.*?)^\s*\}", txt):
        y, mo, d = int(dm.group(1)), int(dm.group(2)), int(dm.group(3))
        if (y, mo, d) <= (1444, 11, 11):
            om = re.search(r"(?m)^\s*owner\s*=\s*([A-Z0-9]{3})", dm.group(4))
            if om:
                owner = om.group(1)
    prov_owner[pid] = owner

# ---------- 2. 解析贸易节点成员省 ----------
txt = read(TN)
# 节点块：^name={ ... } 顶层
nodes = {}
for nm in re.finditer(r"(?m)^([a-z_0-9]+)\s*=\s*\{", txt):
    name = nm.group(1)
    if name in ("outgoing", "path", "control", "members", "color"):
        continue
    start = nm.end()
    depth = 1
    i = start
    while i < len(txt) and depth > 0:
        if txt[i] == "{": depth += 1
        elif txt[i] == "}": depth -= 1
        i += 1
    block = txt[start:i]
    loc = re.search(r"(?m)^\s*location\s*=\s*(\d+)", block)
    mem = re.search(r"(?ms)^\s*members\s*=\s*\{(.*?)\}", block)
    members = [int(x) for x in re.findall(r"\d+", mem.group(1))] if mem else []
    nodes[name] = {"location": int(loc.group(1)) if loc else None, "members": members}

# ---------- 3. 统计每个节点的 1444 无主省数 ----------
rows = []
for name, info in nodes.items():
    mem = info["members"]
    unowned = [p for p in mem if p in prov_owner and prov_owner[p] is None]
    known = [p for p in mem if p in prov_owner]
    rows.append((name, info["location"], len(mem), len(known), len(unowned)))

rows.sort(key=lambda r: -r[4])
print("节点名                     loc    成员  有档案  1444无主")
print("-" * 62)
for name, loc, nm, known, un in rows:
    print("%-24s %-6s %-5d %-6d %d" % (name, loc, nm, known, un))

print()
print("=== T2 声称的数值 vs 我的实测（抽查关键节点）===")
check = {"siberia": 2, "girin": 2, "gulf_of_siam": 0, "canton": 0, "hangzhou": 0,
         "malacca": 6, "the_moluccas": 15, "mexico": None, "brazil": None,
         "australia": 35, "cape_of_good_hope": 14, "ivory_coast": 11}
for name, t2v in check.items():
    mine = next((r[4] for r in rows if r[0] == name), None)
    flag = ""
    if t2v is not None and mine is not None:
        flag = "  <== 差异!" if abs(mine - t2v) > 2 else "  ok"
    print("%-20s T2=%-6s 实测=%-6s%s" % (name, t2v, mine, flag))

json.dump({r[0]: {"location": r[1], "members": r[2], "unowned_1444": r[4]} for r in rows},
          open(r"E:\AI\eu4_autocolonize\docs\_node_verify.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\nsaved -> docs/_node_verify.json")

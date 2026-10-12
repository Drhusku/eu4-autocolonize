# -*- coding: utf-8 -*-
"""用实测数据评估：T2 剔除的节点里，哪些实际有可殖民省份。"""
import os, re, sys, glob, json
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
EU4 = r"E:\SteamLibrary\steamapps\common\Europa Universalis IV"
def read(p): return open(p, "rb").read().decode("cp1252", errors="replace")

# 无主省统计
HP = os.path.join(EU4, "history", "provinces")
owners = {}
for f in glob.glob(os.path.join(HP, "*.txt")):
    m = re.match(r"^(\d+)\s*-\s*", os.path.basename(f))
    if not m: continue
    pid = int(m.group(1)); t = read(f)
    head = re.split(r"(?m)^\s*\d+\.\d+\.\d+\s*=\s*\{", t)[0]
    top = re.search(r"(?m)^\s*owner\s*=\s*([A-Z0-9]{3})", head)
    o = top.group(1) if top else None
    for dm in re.finditer(r"(?ms)^\s*(\d+)\.(\d+)\.(\d+)\s*=\s*\{(.*?)^\s*\}", t):
        if (int(dm.group(1)),int(dm.group(2)),int(dm.group(3))) <= (1444,11,11):
            om = re.search(r"(?m)^\s*owner\s*=\s*([A-Z0-9]{3})", dm.group(4))
            if om: o = om.group(1)
    owners[pid] = o

# 节点
TN = os.path.join(EU4, "common", "tradenodes", "00_tradenodes.txt")
txt = read(TN)
nodes = {}
for nm in re.finditer(r"(?m)^([a-z_0-9]+)\s*=\s*\{", txt):
    name = nm.group(1)
    if name in ("outgoing","path","control","members","color"): continue
    start = nm.end(); depth = 1; i = start
    while i < len(txt) and depth > 0:
        if txt[i] == "{": depth += 1
        elif txt[i] == "}": depth -= 1
        i += 1
    block = txt[start:i]
    loc = re.search(r"(?m)^\s*location\s*=\s*(\d+)", block)
    mem = re.search(r"(?ms)^\s*members\s*=\s*\{(.*?)\}", block)
    members = [int(x) for x in re.findall(r"\d+", mem.group(1))] if mem else []
    nodes[name] = {"location": int(loc.group(1)) if loc else None,
                   "unowned": sum(1 for p in members if owners.get(p) is None)}

# T2 最终收录的 25 个
T2_KEPT = set("brazil laplata patagonia amazonas_node cuiaba lima mexico california rio_grande ohio mississippi_river chesapeake_bay carribean_trade panama st_lawrence james_bay australia polynesia_node cape_of_good_hope african_great_lakes ivory_coast zambezi gulf_of_aden the_moluccas malacca".split())

# 用户说明书点名的 7 个
USER_NAMED = ["australia","malacca","gulf_of_siam","canton","hangzhou","mexico","panama"]

print("=== 用户说明书明确点名的 7 个节点 ===")
for n in USER_NAMED:
    info = nodes.get(n)
    if not info:
        print("  %-18s 节点不存在!" % n); continue
    kept = "已收录" if n in T2_KEPT else "**被T2剔除**"
    print("  %-18s loc=%-6s 1444无主=%-3d  %s" % (n, info["location"], info["unowned"], kept))

print()
print("=== T2 剔除、但实测有 >=5 个可殖民省的节点（建议补回）===")
cand = [(n, i["location"], i["unowned"]) for n, i in nodes.items()
        if n not in T2_KEPT and i["unowned"] >= 5]
cand.sort(key=lambda x: -x[2])
for n, loc, un in cand:
    print("  %-22s loc=%-6s 无主=%d" % (n, loc, un))

print()
print("=== T2 收录、但实测无主省极少的节点（可保留，trigger 会自动隐藏）===")
for n in sorted(T2_KEPT):
    info = nodes.get(n)
    if info and info["unowned"] < 5:
        print("  %-22s loc=%-6s 无主=%d" % (n, info["location"], info["unowned"]))

json.dump({"nodes": nodes, "t2_kept": sorted(T2_KEPT), "user_named": USER_NAMED},
          open(r"E:\AI\eu4_autocolonize\docs\_node_audit.json","w",encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\nsaved -> docs/_node_audit.json")

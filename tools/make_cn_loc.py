# -*- coding: utf-8 -*-
"""生成 autocolonize 中文本地化（EU4 汉化编码 + UTF-8 BOM）。

复用 E:\AI\encode_cn_final.py 的编码规则（已独立验证）：
  非 ASCII -> [marker][b1][b2]，marker 0x10 原样/0x11 低+14/0x12 高-9/0x13 两者
  0x80-0x9F 以 cp1252 对应码位存储
"""
import os, re, sys, shutil
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass

CP1252_REV = {0x20AC:0x80,0x201A:0x82,0x0192:0x83,0x201E:0x84,0x2026:0x85,
              0x2020:0x86,0x2021:0x87,0x02C6:0x88,0x2030:0x89,0x0160:0x8A,
              0x2039:0x8B,0x0152:0x8C,0x017D:0x8E,0x2018:0x91,0x2019:0x92,
              0x201C:0x93,0x201D:0x94,0x2022:0x95,0x2013:0x96,0x2014:0x97,
              0x02DC:0x98,0x2122:0x99,0x0161:0x9A,0x203A:0x9B,0x0153:0x9C,
              0x017E:0x9E,0x0178:0x9F}
BYTE2CP = {b: cp for cp, b in CP1252_REV.items()}
LOW_BAD  = {0x00,0x0A,0x0B,0x0C,0x0D,0x1C,0x1D,0x1E,0x20,0x22,0x23,0x24,
            0x2F,0x3A,0x3B,0x3D,0x40,0x5B,0x5C,0x5D,0x5F,0x7B,0x7D,0x7E,
            0x80,0xA3,0xA4,0xA7,0xBD}
HIGH_BAD = {0x20,0x22,0x5B,0x5C,0x5D,0x5F,0x7B,0x7D,0x7E,0x80}

def cp2byte(c):
    return CP1252_REV.get(ord(c), ord(c))

def encode_char(ch):
    cp = ord(ch)
    if cp < 0x80:
        return [cp], False
    b1, b2 = cp & 0xFF, cp >> 8
    f1, f2 = b1 in LOW_BAD, b2 in HIGH_BAD
    if f1: b1 = (b1 + 14) & 0xFF
    if f2: b2 -= 9
    mk = 0x10 | (1 if f1 else 0) | (2 if f2 else 0)
    return [mk, BYTE2CP.get(b1, b1), BYTE2CP.get(b2, b2)], True

def encode(s):
    out = []
    for ch in s:
        t, _ = encode_char(ch); out.extend(t)
    return ''.join(chr(c) for c in out)

def decode(s):
    cps = [ord(c) for c in s]; out = []; i = 0
    while i < len(cps):
        cp = cps[i]
        if 0x10 <= cp <= 0x13 and i + 2 < len(cps):
            b1, b2 = cp2byte(chr(cps[i+1])), cp2byte(chr(cps[i+2]))
            if cp in (0x11, 0x13): b1 = (b1 - 14) & 0xFF
            if cp in (0x12, 0x13): b2 = (b2 + 9) & 0xFF
            out.append(chr(b1 | (b2 << 8))); i += 3
        else:
            out.append(chr(cp)); i += 1
    return ''.join(out)

ZH = {
 # 显示/隐藏开关（仿自动化 mod 风格，带颜色代码）
 "autocolonize_display_title": "\u00a7G\u3010\u81ea\u52a8\u6b96\u6c11\u3011\u00a7!\u00a7M\u663e\u793a\u00a7!\u76f8\u5173\u51b3\u8bae",
 "autocolonize_hide_title": "\u00a7G\u3010\u81ea\u52a8\u6b96\u6c11\u3011\u00a7!\u00a7M\u9690\u85cf\u00a7!\u76f8\u5173\u51b3\u8bae",
 "autocolonize_display_tooltip": "\u663e\u793a\u81ea\u52a8\u6b96\u6c11 mod \u7684\u5168\u90e8\u51b3\u8bae\u3002",
 "autocolonize_hide_tooltip": "\u9690\u85cf\u81ea\u52a8\u6b96\u6c11 mod \u7684\u5168\u90e8\u51b3\u8bae\uff0c\u4f7f\u51b3\u8bae\u5217\u8868\u66f4\u6574\u6d01\u3002",
 "autocolonize_decision_title": "\u00a7G\u3010\u81ea\u52a8\u6b96\u6c11\u3011\u00a7!\u00a7M\u542f\u7528\u00a7!\u81ea\u52a8\u6b96\u6c11",
 "autocolonize_decision_desc": "每年自动在你选定的区域内反复殖民无主土地。",
 "autocolonize_decision_stop_title": "关闭自动殖民",
 "autocolonize_decision_stop_desc": "关闭自动殖民官，并清除它的全部设置。",
 "autocolonize.1.title": "自动殖民 — 选择模式",
 "autocolonize.1.desc": "自动殖民官应该把精力投向何方？",
 "autocolonize.1.a": "按次大陆殖民",
 "autocolonize.1.b": "按贸易节点殖民",
 "autocolonize.1.c": "取消",
 "autocolonize.2.title": "自动殖民 — 选择排序",
 "autocolonize.2.desc": "殖民官应如何安排目标的优先级？",
 "autocolonize.2.a": "按距离（由近到远）",
 "autocolonize.2.b": "按发展度（从高到低）",
 "autocolonize.2.c": "取消",
 "autocolonize.3.title": "自动殖民 — 选择目标",
 "autocolonize.3.desc": "选择一个次大陆进行自动殖民。已无可殖民土地的目标会被隐藏。",
 "autocolonize.3.cancel": "全部目标已殖民完毕，或放弃 — 停止自动殖民",
 "autocolonize.4.title": "自动殖民 — 选择贸易节点",
 "autocolonize.4.desc": "选择一个贸易节点进行自动殖民。已无可殖民土地的节点会被隐藏。（当前目标殖民完毕后，此列表会再次弹出。）",
 "autocolonize.4.cancel": "全部目标已殖民完毕，或放弃 — 停止自动殖民",
 "autocolonize.5.title": "自动殖民脉冲",
 "autocolonize.5.desc": "已执行自动殖民。",
 "autocolonize.5.a": "继续",
 "autocolonize_tooltip_active": "自动殖民已启用",
 "autocolonize_tooltip_none": "未启用自动殖民。",
 # 次大陆 16
 "autocolonize_target_india_superregion": "印度",
 "autocolonize_target_east_indies_superregion": "东印度",
 "autocolonize_target_oceania_superregion": "大洋洲",
 "autocolonize_target_china_superregion": "中国",
 "autocolonize_target_far_east_superregion": "远东",
 "autocolonize_target_tartary_superregion": "鞑靼",
 "autocolonize_target_persia_superregion": "波斯",
 "autocolonize_target_south_america_superregion": "南美洲",
 "autocolonize_target_central_america_superregion": "中美洲",
 "autocolonize_target_andes_superregion": "安第斯",
 "autocolonize_target_north_america_superregion": "北美洲",
 "autocolonize_target_near_east_superregion": "近东",
 "autocolonize_target_eastern_europe_superregion": "东欧",
 "autocolonize_target_europe_superregion": "西欧",
 "autocolonize_target_africa_superregion": "非洲",
 "autocolonize_target_southern_africa_superregion": "南部非洲",
 # 贸易节点 31
 "autocolonize_target_brazil": "巴西",
 "autocolonize_target_laplata": "拉普拉塔",
 "autocolonize_target_patagonia": "巴塔哥尼亚",
 "autocolonize_target_amazonas_node": "亚马逊",
 "autocolonize_target_cuiaba": "库亚巴",
 "autocolonize_target_lima": "利马",
 "autocolonize_target_mexico": "墨西哥",
 "autocolonize_target_california": "加利福尼亚",
 "autocolonize_target_rio_grande": "里奥格兰德",
 "autocolonize_target_ohio": "俄亥俄",
 "autocolonize_target_mississippi_river": "密西西比河",
 "autocolonize_target_chesapeake_bay": "切萨皮克湾",
 "autocolonize_target_carribean_trade": "加勒比",
 "autocolonize_target_panama": "巴拿马",
 "autocolonize_target_st_lawrence": "圣劳伦斯湾",
 "autocolonize_target_james_bay": "哈德逊湾",
 "autocolonize_target_australia": "澳大利亚",
 "autocolonize_target_polynesia_node": "波利尼西亚",
 "autocolonize_target_cape_of_good_hope": "好望角",
 "autocolonize_target_african_great_lakes": "非洲大湖",
 "autocolonize_target_ivory_coast": "象牙海岸",
 "autocolonize_target_zambezi": "赞比西",
 "autocolonize_target_gulf_of_aden": "亚丁湾",
 "autocolonize_target_the_moluccas": "摩鹿加",
 "autocolonize_target_malacca": "马六甲",
 "autocolonize_target_siberia": "西伯利亚",
 "autocolonize_target_girin": "吉林",
 "autocolonize_target_philippines": "菲律宾",
 "autocolonize_target_canton": "广州",
 "autocolonize_target_hangzhou": "杭州",
 "autocolonize_target_gulf_of_siam": "暹罗湾",
}

BASE = r"E:\AI\eu4_autocolonize"
EN = os.path.join(BASE, "localisation", "autocolonize_l_english.yml")

# 读英文 key 集合，确保完全一致
en_keys = []
for line in open(EN, encoding="utf-8-sig"):
    m = re.match(r'^\s*([A-Za-z0-9_.\-]+)\s*:\s*\d*\s*"', line)
    if m: en_keys.append(m.group(1))

missing = [k for k in en_keys if k not in ZH]
extra   = [k for k in ZH if k not in en_keys]
print("英文 key: %d, 中文 key: %d" % (len(en_keys), len(ZH)))
print("中文缺失: %s" % (missing if missing else "无"))
print("中文多余: %s" % (extra if extra else "无"))

# 编码 + 往返自检
lines = ["l_english:"]
fails = 0
for k in en_keys:
    zh = ZH[k]
    enc = encode(zh)
    if decode(enc) != zh:
        fails += 1; print("!! 往返失败: %s" % k)
    for bad in ['"', "\n", "\r"]:
        if bad in enc:
            fails += 1; print("!! 编码含非法字符 %r: %s" % (bad, k))
    lines.append(' %s:0 "%s"' % (k, enc))
print("编码自检失败: %d" % fails)
content = "\n".join(lines) + "\n"

# 写 simp_chinese（契约命名）
sc = os.path.join(BASE, "localisation", "autocolonize_l_simp_chinese.yml")
with open(sc, "wb") as f:
    f.write(b"\xef\xbb\xbf"); f.write(content.encode("utf-8"))
print("写入 %s (%d B)" % (sc, os.path.getsize(sc)))

# 游戏语言是 l_english（用户装了汉化 mod），故中文也覆盖 l_english
shutil.copy(EN, EN + ".en-backup")
with open(EN, "wb") as f:
    f.write(b"\xef\xbb\xbf"); f.write(content.encode("utf-8"))
print("写入 %s (中文覆盖，英文原文备份为 .en-backup)" % EN)

# 回读验证
raw = open(sc, "rb").read()
txt = raw.decode("utf-8-sig")
print("BOM=%s, 大小=%d" % (raw[:3] == b"\xef\xbb\xbf", len(raw)))
n = 0
for m in re.finditer(r'^\s*([A-Za-z0-9_.\-]+)\s*:\s*\d*\s*"(.*?)"\s*$', txt, re.M):
    if n < 3:
        print("  回读 %s = %s" % (m.group(1), decode(m.group(2))))
    n += 1
print("回读 key 数: %d" % n)

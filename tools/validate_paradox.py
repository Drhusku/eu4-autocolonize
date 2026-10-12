#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EU4 自动殖民 mod 静态校验器（T3/T4 交付物的独立验证核心）。

用法:
    python tools/validate_paradox.py [mod_root] [--strict]

    --strict   要求所有预期文件都存在（缺失记 FAIL）；默认缺失记 SKIP。

退出码: 0 = 无 FAIL；1 = 存在 FAIL；2 = 致命错误（根目录不存在）。

版本说明
==========
基础版由 Captain 提供，verifier(T5) 于 2026-10-11 增强，补充「引用闭合」检查：
  B3  增强：反向闭合 —— 所有被【调用】的 scripted_effect / scripted_trigger
       必须已有【定义】；被调用的自定义 effect/trigger 名逐一在 events/decisions/
       脚本体内收集，与定义集求差。原来仅正向往外查必需定义存在。
  B2  增强：事件【引用】闭合 —— 所有 country_event = { id = autocolonize.X } /
       = autocolonize.X 的引用目标必须能被事件文件中的定义找到（防改错事件号）。
  B4  增强：localisation key【引用】闭合 —— events/decisions/on_actions 里用到的
       title / desc / option name / custom_tooltip / 决议 option name 等 key，
       必须能在 loc 文件集合里找到；中文 key 集合需与英文一致（含全部被引用 key）。
  B8  新增：中文编码往返 —— 按项目规则（marker 0x10-0x13 三字节编解码，参照
       tools/make_cn_loc.py 的 encode/decode，与 E:\\AI\\encode_cn_final.py 同源）
       对 loc 值的编码串做 decode → encode 往返，确认一一可逆、且不在文件中引入
       未受控的 '"
' 字符（防止引擎解析破坏）。

检查项:
    B0  预期文件齐备
    B1  .txt 花括号平衡
    B2  事件 id 唯一 + namespace + 事件【引用】闭合
    B3  scripted_effect / scripted_trigger：【定义】齐全 + 【调用】闭合（反向）
    B4  localisation key：中英集合一致 + 全部被引用 key 均在 loc 中
    B5  决议文件含 ai = no
    B6  年度执行事件含 ai = no 与 has_country_flag = autocolonize_active
    B7  禁用关键字扫描（1.37.5 不存在的语法）
    B8  中文编码往返自检
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

EXPECTED = [
    "events/autocolonize_events.txt",
    "common/scripted_effects/autocolonize_effects.txt",
    "common/scripted_triggers/autocolonize_triggers.txt",
    "decisions/autocolonize_decisions.txt",
    "common/on_actions/00_autocolonize_on_actions.txt",
    "localisation/autocolonize_l_english.yml",
    "localisation/autocolonize_l_simp_chinese.yml",
    "descriptor.mod",
]

# 依据：2026-10-11 在 EU4 1.37.5 原版脚本全量 grep，以下关键字零出现。
BANNED = {
    "is_owned_by": "1.37.5 无此 trigger；请用 is_empty = yes + is_colony = no",
    "any_province_in_superregion": "1.37.5 无此 scope",
    "every_province_in_superregion": "1.37.5 无此 scope",
    "random_province_in_superregion": "1.37.5 无此 scope",
}

REQUIRED_EFFECTS = [
    "autocolonize_clear_target",
    "autocolonize_reset_all",
    "autocolonize_run",
    "autocolonize_colonize_superregion",
    "autocolonize_colonize_trade_node",
]
REQUIRED_TRIGGERS = [
    "autocolonize_province_is_colonizable",
    "autocolonize_superregion_has_colonizable",
    "autocolonize_trade_node_has_colonizable",
]

# ---------------------------------------------------------------- 中文编码往返
# 复用 tools/make_cn_loc.py / E:\\AI\\encode_cn_final.py 的编解码规则。
# 非 ASCII 字符 -> [marker][b1][b2]；marker: 0x10 原样 / 0x11 低+14 / 0x12 高-9 / 0x13 两者。
LOW_BAD  = {0x00,0x0A,0x0B,0x0C,0x0D,0x1C,0x1D,0x1E,0x20,0x22,0x23,0x24,
            0x2F,0x3A,0x3B,0x3D,0x40,0x5B,0x5C,0x5D,0x5F,0x7B,0x7D,0x7E,
            0x80,0xA3,0xA4,0xA7,0xBD}
HIGH_BAD = {0x20,0x22,0x5B,0x5C,0x5D,0x5F,0x7B,0x7D,0x7E,0x80}
CP1252_REV = {0x20AC:0x80,0x201A:0x82,0x0192:0x83,0x201E:0x84,0x2026:0x85,
              0x2020:0x86,0x2021:0x87,0x02C6:0x88,0x2030:0x89,0x0160:0x8A,
              0x2039:0x8B,0x0152:0x8C,0x017D:0x8E,0x2018:0x91,0x2019:0x92,
              0x201C:0x93,0x201D:0x94,0x2022:0x95,0x2013:0x96,0x2014:0x97,
              0x02DC:0x98,0x2122:0x99,0x0161:0x9A,0x203A:0x9B,0x0153:0x9C,
              0x017E:0x9E,0x0178:0x9F}
BYTE2CP = {b: cp for cp, b in CP1252_REV.items()}

def _raw(cp):  # 逆映射 0x80-0x9F（文件以 cp1252 对应 Unicode 码位存储）
    return CP1252_REV.get(ord(cp), ord(cp))

def decode(s):
    cps = [ord(c) for c in s]; out = []; i = 0
    while i < len(cps):
        cp = cps[i]
        if 0x10 <= cp <= 0x13 and i + 2 < len(cps):
            b1, b2 = _raw(chr(cps[i+1])), _raw(chr(cps[i+2]))
            if cp in (0x11, 0x13): b1 = (b1 - 14) & 0xFF
            if cp in (0x12, 0x13): b2 = (b2 + 9) & 0xFF
            out.append(chr(b1 | (b2 << 8))); i += 3
        else:
            out.append(chr(cp)); i += 1
    return ''.join(out)

def encode(s):
    def enc_char(ch):
        cp = ord(ch)
        if cp < 0x80:
            return [cp]
        b1, b2 = cp & 0xFF, cp >> 8
        f1, f2 = b1 in LOW_BAD, b2 in HIGH_BAD
        if f1: b1 = (b1 + 14) & 0xFF
        if f2: b2 -= 9
        mk = 0x10 | (1 if f1 else 0) | (2 if f2 else 0)
        return [mk, BYTE2CP.get(b1, b1), BYTE2CP.get(b2, b2)]
    out = []
    for ch in s:
        out.extend(enc_char(ch))
    return ''.join(chr(c) for c in out)

# ---------------------------------------------------------------- 通用读取
class Report:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str, str]] = []
    def add(self, code, name, status, detail=""): self.rows.append((code, name, status, detail))
    def ok(self, code, name, detail=""): self.add(code, name, "PASS", detail)
    def fail(self, code, name, detail=""): self.add(code, name, "FAIL", detail)
    def skip(self, code, name, detail=""): self.add(code, name, "SKIP", detail)
    @property
    def failed(self): return [r for r in self.rows if r[2] == "FAIL"]
    def render(self):
        lines = []
        for code, name, status, detail in self.rows:
            mark = {"PASS": "[PASS]", "FAIL": "[FAIL]", "SKIP": "[SKIP]"}[status]
            lines.append(f"{mark} {code} {name}" + (f"  -- {detail}" if detail else ""))
        lines.append("")
        lines.append(f"TOTAL PASS={sum(1 for r in self.rows if r[2]=='PASS')} "
                     f"FAIL={sum(1 for r in self.rows if r[2]=='FAIL')} "
                     f"SKIP={sum(1 for r in self.rows if r[2]=='SKIP')}")
        return "\n".join(lines)

def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1")

def strip_comments(text: str) -> str:
    out = []
    for line in text.splitlines():
        buf = []; in_quote = False
        for ch in line:
            if ch == '"':
                in_quote = not in_quote
            if ch == "#" and not in_quote:
                break
            buf.append(ch)
        out.append("".join(buf))
    return "\n".join(out)

def loc_assigns(text: str) -> dict:
    """返回 {key: value}，value 不含引号包裹。"""
    result = {}
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        m2 = re.match(r'^([A-Za-z0-9_.-]+)\s*:\s*\d*\s*"(.*)"\s*$', s)
        if m2:
            result[m2.group(1)] = m2.group(2)
            if m2:
                result[m2.group(1)] = m2.group(2)
    return result

def loc_keys(text: str) -> set:
    return set(loc_assigns(text).keys())

# ---------------------------------------------------------------- 主函数
def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    strict = "--strict" in sys.argv[1:]
    default_root = Path(__file__).resolve().parent.parent
    root = Path(args[0]) if args else default_root
    if not root.is_dir():
        print(f"[FATAL] mod root not found: {root}")
        return 2

    rep = Report()

    present, missing = [], []
    for rel in EXPECTED:
        (present if (root / rel).is_file() else missing).append(rel)
    if strict:
        if missing:
            rep.fail("B0", "预期文件齐备", "缺失: " + ", ".join(missing))
        else:
            rep.ok("B0", "预期文件齐备", f"{len(present)} 个文件")
    else:
        if missing:
            rep.skip("B0", "预期文件齐备", "尚未产出: " + ", ".join(missing))
        else:
            rep.ok("B0", "预期文件齐备", f"{len(present)} 个文件")

    txt_files = sorted(p for p in root.rglob("*.txt") if p.is_file())
    yml_files = sorted(p for p in root.rglob("*.yml") if p.is_file()
                       and ".en-backup" not in p.name)

    # ------------------------------------------------ B1 花括号平衡
    if not txt_files:
        rep.skip("B1", "花括号平衡", "无 .txt 文件")
    else:
        bad = []
        for p in txt_files:
            body = strip_comments(read_text(p))
            d = body.count("{") - body.count("}")
            if d != 0:
                bad.append(f"{p.relative_to(root).as_posix()}(差 {d:+d})")
        (rep.ok("B1","花括号平衡",f"{len(txt_files)} 个文件") if not bad
         else rep.fail("B1","花括号平衡","; ".join(bad)))

    # ------------------------------------------------ B7 禁用关键字
    hits = []
    for p in txt_files:
        body = strip_comments(read_text(p))
        for kw in BANNED:
            if re.search(r"" + re.escape(kw) + r"", body):
                hits.append(f"{p.relative_to(root).as_posix()}:{kw}")
    (rep.ok("B7","禁用关键字扫描",f"已扫 {len(txt_files)} 个文件，无命中") if not hits
     else rep.fail("B7","禁用关键字扫描","; ".join(hits)))

    # ------------------------------------------------ 事件文件
    ev_path = root / "events/autocolonize_events.txt"
    have_events = ev_path.is_file()
    all_ids, defined_event_ids = set(), set()
    if have_events:
        body_full = read_text(ev_path)
        body = strip_comments(body_full)
        ns = re.findall(r"^\s*namespace\s*=\s*(\w+)", body, re.M)
        ids = re.findall(r"^\s*id\s*=\s*([\w.]+)", body, re.M)
        defined_event_ids = set(ids)
        problems = []
        if not ns:
            problems.append("缺少 namespace 声明")
        elif set(ns) != {"autocolonize"}:
            problems.append(f"namespace 应为 autocolonize，实为 {sorted(set(ns))}")
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            problems.append(f"重复 id: {sorted(dupes)}")
        for i in ids:
            if "." in i and not i.startswith("autocolonize."):
                problems.append(f"id 命名空间不符: {i}")
        # B2 引用闭合：收集所有 country_event = { id = X } / = autocolonize.X
        refs = set(re.findall(r"country_event\s*=\s*\{\s*id\s*=\s*([\w.]+)", body))
        refs |= set(re.findall(r"id\s*=\s*(autocolonize\.[0-9]+)", body))
        dangling = sorted(r for r in refs if r not in defined_event_ids)
        if dangling:
            problems.append("引用了未定义事件: " + ", ".join(f"{r}" for r in dangling))
        if problems:
            rep.fail("B2", "事件 id 唯一 + namespace + 引用闭合", "; ".join(problems))
        else:
            rep.ok("B2", "事件 id 唯一 + namespace + 引用闭合",
                   f"namespace={ns[0]}, {len(ids)} 个事件定义; 引用 {len(refs)} 处全部闭合")
    else:
        rep.skip("B2", "事件 id 唯一 + namespace + 引用闭合", "事件文件尚未产出")

    # ------------------------------------------------ B3 scripted 定义+调用闭合
    effects_def, triggers_def = set(), set()
    srefs = {}  # 反向：事件/决议里【调用】的自定义 effect/trigger 名 -> 计数
    # 收集"被调用"的名字时，必须排除三类非调用：
    #   1) 作为块定义出现的名字（行首 name = {）——如决议名 autocolonize_decision
    #   2) flag 名（has_country_flag / set_country_flag / clr_country_flag = X）
    #   3) localisation key（在 loc 文件中定义的 key）
    BLOCK_DEF = re.compile(r"^\s*([a-z_][a-z0-9_]*)\s*=\s*\{", re.M)
    FLAG_USE = re.compile(r"\b(?:has|set|clr)_country_flag\s*=\s*([a-z_][a-z0-9_]*)")
    CALL = re.compile(r"\b(autocolonize_[a-z_]+)\b")

    # loc key 全集（用于排除）
    loc_all = set()
    for lp in (root / "localisation").glob("*.yml"):
        if ".en-backup" in lp.name:
            continue
        try:
            loc_all |= set(loc_assigns(read_text(lp)).keys())
        except Exception:
            pass

    def collect_refs(body: str) -> None:
        defined_here = set(BLOCK_DEF.findall(body))
        flag_here = set(FLAG_USE.findall(body))
        for kw in CALL.findall(body):
            if kw in defined_here or kw in flag_here or kw in loc_all:
                continue
            srefs[kw] = srefs.get(kw, 0) + 1

    if have_events:
        collect_refs(strip_comments(read_text(ev_path)))

    dec_path = root / "decisions/autocolonize_decisions.txt"
    if dec_path.is_file():
        collect_refs(strip_comments(read_text(dec_path)))

    # 先完整读取两个文件的定义集合（effects 与 triggers 同属一个命名空间，
    # 闭合检查必须同时看到二者，否则会出现"检查 effects 时 triggers 还没读"的顺序误报）。
    B3_TARGETS = (
        ("B3a", "common/scripted_effects/autocolonize_effects.txt", REQUIRED_EFFECTS, True),
        ("B3b", "common/scripted_triggers/autocolonize_triggers.txt", REQUIRED_TRIGGERS, False),
    )
    file_bodies = {}
    for _code, _rel, _req, _is_eff in B3_TARGETS:
        _p = root / _rel
        if _p.is_file():
            _body = strip_comments(read_text(_p))
            file_bodies[_rel] = _body
            _defs = set(re.findall(r"^\s*([a-z_][a-z0-9_]*)\s*=\s*\{", _body, re.M))
            if _is_eff:
                effects_def |= _defs
            else:
                triggers_def |= _defs
    all_defined = effects_def | triggers_def

    for code, rel, required, is_effect in B3_TARGETS:
        if rel not in file_bodies:
            rep.skip(code, f"定义+引用闭合 {rel}", "文件尚未产出")
            continue
        body = file_bodies[rel]
        defined = set(re.findall(r"^\s*([a-z_][a-z0-9_]*)\s*=\s*\{", body, re.M))
        absent = [n for n in required if n not in defined]
        problems = []
        if absent:
            problems.append("必需定义缺失: " + ", ".join(absent))
        # 反向闭合：事件/决议里调用、但在（effects ∪ triggers）里都没有定义的名字
        missing_refs = sorted({n for n in srefs if n not in all_defined})
        if missing_refs:
            problems.append("被调用但无定义: " + ", ".join(missing_refs))
        if problems:
            rep.fail(code, f"定义+引用闭合 {rel}", "; ".join(problems))
        else:
            rep.ok(code, f"定义+引用闭合 {rel}",
                   f"必需定义 {len(required)} 个齐全; 事件/决议内引用 {len(srefs)} 个全部闭合")

    # ------------------------------------------------ B4 localisation
    en = root / "localisation/autocolonize_l_english.yml"
    zh = root / "localisation/autocolonize_l_simp_chinese.yml"
    en_keyset, zh_keyset = set(), set()
    if not en.is_file():
        rep.skip("B4", "localisation key 中英一致+引用闭合", "英文 loc 尚未产出")
    else:
        en_assign = loc_assigns(read_text(en))
        en_keyset = set(en_assign.keys())
        zh_assign = zh.is_file() and loc_assigns(read_text(zh)) or {}
        zh_keyset = set(zh_assign.keys())

        probs = []
        if not en_keyset:
            probs.append("英文 loc 未解析出任何 key")
        else:
            only_en = sorted(en_keyset - zh_keyset)
            only_zh = sorted(zh_keyset - en_keyset)
            if only_en or only_zh:
                probs.append(f"中英 key 不一致: 中文缺 {len(only_en)}{only_en[:6]} / 中文多 {len(only_zh)}{only_zh[:6]}")
        # 引用闭合：所有脚本引用的 loc key
        ref_keys = set()
        body_src = ""
        if have_events:
            body_src += strip_comments(read_text(ev_path)) + "\n"
        if dec_path.is_file():
            body_src += strip_comments(read_text(dec_path)) + "\n"
        for p in txt_files:
            if p.suffix == ".txt":
                body_src += strip_comments(read_text(p)) + "\n"
        # title / desc / name(选项名兼文件名) / custom_tooltip / tooltip
        for m in re.finditer(r'(title|desc|custom_tooltip|tooltip)s*=s*([w.]+)', body_src):
            ref_keys.add(m.group(2))
        for m in re.finditer(r'option\s*=\s*\{\s*name\s*=\s*([\w.]+)', body_src):
            ref_keys.add(m.group(1))
        # 决议 option name（决议文件合并进 body_src 已覆盖）
        missing_loc = sorted(k for k in ref_keys if k not in en_keyset)
        if missing_loc:
            probs.append("引用但 loc 缺失: " + ", ".join(f"{k}" for k in missing_loc[:10]))
        if probs:
            rep.fail("B4", "localisation key 中英一致+引用闭合", "; ".join(probs))
        else:
            nref = len(ref_keys)
            rep.ok("B4", "localisation key 中英一致+引用闭合",
                   f"中英各 {len(en_keyset)} key 一致; 脚本引用 {nref} 个 loc key 全部闭合")

    # ------------------------------------------------ B5 决议 ai = no
    if not dec_path.is_file():
        rep.skip("B5", "决议含 ai = no", "决议文件尚未产出")
    else:
        body = strip_comments(read_text(dec_path))
        if re.search(r"ai\s*=\s*no", body):
            rep.ok("B5", "决议含 ai = no")
        else:
            rep.fail("B5", "决议含 ai = no", "未找到 ai = no")

    # ------------------------------------------------ B6 年度事件守卫
    if not have_events:
        rep.skip("B6", "年度事件守卫", "事件文件尚未产出")
    else:
        body = strip_comments(read_text(ev_path))
        miss = []
        if not re.search(r"ai\s*=\s*no", body):
            miss.append("ai = no")
        if "autocolonize_active" not in body:
            miss.append("has_country_flag = autocolonize_active")
        (rep.ok("B6","年度事件守卫") if not miss else rep.fail("B6","年度事件守卫","缺少: " + ", ".join(miss)))

    # ------------------------------------------------ B9 hidden 语义检查
    # 教训（2026-10-11 实机试玩发现）：EU4 的 hidden = yes 事件会静默执行、不弹窗。
    # 交互式事件（含 option 且由决议/其他事件触发，期望玩家看到）绝不能带 hidden，
    # 否则玩家点决议后"什么都没发生"。仅内部执行事件（如年度脉冲）可 hidden。
    if not have_events:
        rep.skip("B9", "hidden 语义检查", "事件文件尚未产出")
    else:
        raw_ev = read_text(ev_path)
        body_ev = strip_comments(raw_ev)
        # 按 country_event 块切分，逐块检查
        blocks = re.split(r"(?m)^\s*country_event\s*=\s*\{", body_ev)
        suspects = []
        for blk in blocks[1:]:
            mid = re.search(r"\bid\s*=\s*([\w.]+)", blk)
            eid = mid.group(1) if mid else "?"
            if re.search(r"\bhidden\s*=\s*yes", blk):
                n_opt = len(re.findall(r"(?m)^\s*option\s*=\s*\{", blk))
                # 隐藏事件若还带多个 option，且不是已知的内部事件（.5 脉冲），高度可疑
                if n_opt > 0 and not eid.endswith(".5"):
                    suspects.append(f"{eid}({n_opt} 个 option)")
        if suspects:
            rep.fail("B9", "hidden 语义检查",
                     "以下事件带 hidden = yes 且有 option，玩家将看不到弹窗: " + ", ".join(suspects))
        else:
            rep.ok("B9", "hidden 语义检查",
                   "无「hidden + option」的交互式事件（内部脉冲事件豁免）")

    # ------------------------------------------------ B8 中文编码往返
    if not (en.is_file() and zh.is_file()):
        rep.skip("B8", "中文编码往返", "loc 文件未齐备")
    else:
        # 合并两个 loc 的 value 做往返；顺带做"解码文本合法"检查
        fails = 0
        cnt = 0
        sample_fail = []
        for assign in (loc_assigns(read_text(en)), loc_assigns(read_text(zh))):
            for k, v in assign.items():
                cnt += 1
                dec = decode(v)
                if encode(dec) != v:
                    fails += 1
                    if len(sample_fail) < 8:
                        sample_fail.append(f"{k}")
                # 解码后不允许残留会破坏 yml 的引号/换行/注释分隔
                for bad in '"\n' .replace("\\n", chr(10)):
                    if bad in dec:
                        fails += 1
                        if len(sample_fail) < 8:
                            sample_fail.append(f"{k}@非法字符 U+{ord(bad):04X}")
                        break
        (rep.ok("B8","中文编码往返",f"检查 {cnt} 个 loc value，往返解码 0 失败")
         if fails == 0 else
         rep.fail("B8","中文编码往返",f"{fails} 处失败: {sample_fail}"))

    print(rep.render())
    return 1 if rep.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

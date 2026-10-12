# 评审报告 R1 — 自动殖民 mod 核心实现（第 1 轮）

评审人：Captain（GLM）· 2026-10-12
评审对象：T3（implementer 实现）核心脚本 + T4（Captain 实现）中文本地化
评审方式：逐文件人工核查 + 原版脚本反证 + 实机试玩反馈

---

## 一、verdict：**needs_revision**（1 个 medium + 2 个 low，均可快速修复）

## 二、逐项核查

### 2.1 语法正确性 — 通过
对照原版 1.37.5 脚本逐个验证实现所用 trigger/effect：

| 用法 | 结论 | 证据 |
|---|---|---|
| is_empty/is_colony/is_wasteland/has_discovered | 通过 | docs/SYNTAX_FINDINGS.md §1 |
| any_province = { superregion = X } 触发过滤 | 通过 | 03_burgher_agendas.txt:1997 |
| <superregion名> = { } 效果遍历 | 通过 | 00_on_actions.txt:1829 |
| <节点location省id> = { any_trade_node_member_province } | 通过 | DOM_Japanese_Missions.txt:283 等 15 处 |
| development = N 在 random_province limit 内（省份作用域） | 通过 | 00_generic_agendas.txt:6170-6173 |
| create_colony = 200 | 通过 | events/Colonial.txt:47,995 |
| on_yearly_pulse 挂载 | 通过（合并机制） | 00_on_actions.txt:2048 |

### 2.2 逻辑闭环 — 通过
决议 → .1 选模式 → .2 选排序 → .3/.4 选目标 → 年度脉冲 .5 → autocolonize_run 分派 → 目标耗尽 else 分支清 flag 并弹续选。
- 31 节点全部使用硬编码 location 省 id + NOT = { province_id = <location> } 排除节点所在地 — 通过
- 排序实现：sort_development 先试 development>=10，无则兜底任意；sort_distance 为方案 A 近似（无专门分支，走兜底）— 通过
- 16 次大陆 + 31 贸易节点 = 47 目标选项，全部带 trigger 控制显隐 — 通过

### 2.3 说明书功能覆盖

| 说明书条目 | 判定 |
|---|---|
| 4.1 入口决议（含 potential） | 已实现 |
| 4.2 模式选择 → 排序选择 | 事件链 .1→.2→.3/.4 |
| 4.3 目标列表（trigger 显隐） | 47 个选项全部带 trigger |
| 4.4 年度脉冲 + 分段随机 + create_colony | on_yearly_pulse + development 分段 + create_colony=200 |
| 4.5 完成事件列出其他目标 | else 分支清 flag + 弹续选事件 |

### 2.4 性能与 AI 污染 — 通过
- 全部事件含 ai = no
- 决议 potential 含 ai = no
- 事件为 is_triggered_only，无 MTTH 轮询
- 年度脉冲仅在有 target flag 时才实际遍历（run 内 if 分派）

### 2.5 中文本地化可加载性 — 通过（本次修复后）
- UTF-8 BOM（回读 BOM=True）
- 三字符转义编码（低字节禁用集已修正为含 0x0B/0x0C/0x1C/0x1D/0x1E，依据汉化 mod 159011 三元组反推）
- 往返解码自检（validate_paradox B8 = PASS，144 个 loc value 0 失败）
- 中英 key 集合一致（72 = 72）
- yml 无断行残片（修复后 0 处）

## 三、Findings

### F1 [medium] 贸易节点/次大陆耗尽时的续选事件可能弹出空事件
问题：autocolonize_colonize_trade_node / autocolonize_colonize_superregion 的 else 分支里
country_event = { id = autocolonize.4 } / autocolonize.3。若该模式下**所有**目标都已无可殖民省份，
.4/.3 会正常弹出（mode flag 未被 clear_target 清除），但**所有选项的 trigger 均不满足**，
玩家看到一个只剩「停止自动殖民」的空事件，会误以为出错。

severity: medium
requiredFix: 在 .3 与 .4 各加一个**无条件兜底选项**「全部目标已殖民完毕 — 停止自动殖民」，
effect = autocolonize_reset_all。或 else 分支改弹专用完成事件。
file: events/autocolonize_events.txt（.3.cancel 约 195 行；.4.cancel 约 648 行）

### F2 [low] development 分段阈值单一
问题：说明书建议三档（>=10 / >=5 / 兜底），实现只有两档（>=10 / 兜底）。功能可用但排序粒度粗。
severity: low
requiredFix: 在 >=10 与兜底之间补一档 development = 5（else_if）。可选优化，不阻塞发布。
file: common/scripted_effects/autocolonize_effects.txt:81

### F3 [low] sort_distance（由近到远）没有专门分支
问题：方案 A 定义为「优先已探索 + 引擎距离自然筛选」，但实现里 distance 模式与无排序完全相同。
severity: low
requiredFix: 维持现状（DESIGN §8.7 与 README 已知限制已如实说明，可殖民判定已含 has_discovered，
实际增益约等于零）。无需代码改动。

## 四、中文本地化可加载性 — 通过
- BOM / 转义编码（禁用集修正后）/ 往返自检 0 失败 / 中英 72 key 一致 / 无断行残片 — 全通过
- validate_paradox --strict = **11/11 PASS**（含 B9 hidden 语义检查）

## 五、结论
实现质量整体良好：契约遵守严格、原版证据充分、31 节点映射全部正确、说明书 5 项功能全覆盖。
唯一需要修的是 **F1（空事件兜底）**，修完即可 pass。F2/F3 不阻塞发布。
修复后需重跑：validate_paradox.py --strict（应 11/11）+ 实机验证一次「目标耗尽」场景。

## 六、R2 findings 裁定（Captain 2026-10-12）

T12 复审提出 3 条 findings。Captain 逐条独立验证后裁定：**三条全部不采纳、不改代码**——T13 的正确产出是「记录备案」，不是修复。

### R2-F1 [medium] 误报 — 不采纳
复审称「裸 filter + limit 混写未在原版出现」。Captain 实测反例（原版均把裸 superregion/area 与其他条件混写、无 limit 包裹）：
- `common/estate_agendas/03_burgher_agendas.txt:2229` = `any_province = { superregion = china_superregion has_port = yes range = ROOT has_discovered = ROOT }`
- `common/scripted_effects/01_scripted_effects_for_on_actions.txt:4507` = `any_province = { area = PREV is_reformation_center = yes religion = zoroastrian }`
实现写法与原版一致，**不**把 superregion 归一进 limit。

### R2-F2 [medium] 误报 — 不采纳
l_english 装中文是既定决策，证据：
1. 用户 `settings.txt` 的 `language="l_english"`
2. 汉化 mod 2976470733 的 145 个本地化文件**全部用 _l_english.yml、零个 _l_simp_chinese.yml**
3. 用户自己的 exile_heir_mod 同样只用 `exile_heir_l_english.yml`
DESIGN §1 写「英文原文」是契约笔误。**不**改 loc 文件。

### R2-F3 [low] 接受备案 — 不改
行为等价（flag 匹配 vs $TARGET$ 形参），不改。

### 处置结果
T13 按 Captain 裁定执行：三条均**备案不修**；`events/`、`common/`、`localisation/` 下无任何功能性改动。期间 T13 曾临时尝试 R2-F1 的代码改动，已按裁定**回滚**至原写法（裸 superregion 平铺，与原版 03_burgher:2229 一致）。`validate_paradox.py --strict` = **11/11 PASS**，确认「无需改动」判断成立，t14（复审）可据此 pass 并解锁 t7（集成）。

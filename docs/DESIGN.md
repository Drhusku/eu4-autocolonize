# EU4 自动殖民 Mod — 接口契约（Captain 锁定）

> **本文件由 Captain 编写并锁定。实现者不得擅自更改第 2/3/4/5/6/7 节的任何标识符。**
> 若发现某条契约在 EU4 1.37.5 中不可实现，**不要自行改名**，在交付说明里写明冲突点，由 Captain 裁定。

## 0. 项目基本信息

| 项 | 值 |
|---|---|
| mod 源码根目录 | `E:\AI\eu4_autocolonize` |
| mod 内部名（descriptor 的 name） | `Auto Colonize 自动殖民` |
| 目标游戏版本 | EU4 **1.37.5**（本机 `E:\SteamLibrary\steamapps\common\Europa Universalis IV`） |
| 事件命名空间 | `autocolonize` |
| 安装目录 | `C:\Users\Husky\Documents\Paradox Interactive\Europa Universalis IV\mod\autocolonize` |
| 安装描述文件 | `...\mod\autocolonize.mod` |

## 1. 文件清单与写入归属（互斥，禁止越界写别人的文件）

| 文件 | 归属 | 说明 |
|---|---|---|
| `events/autocolonize_events.txt` | event-smith | 事件 1~5 |
| `common/scripted_effects/autocolonize_effects.txt` | event-smith | 效果 4 个 |
| `common/scripted_triggers/autocolonize_triggers.txt` | event-smith | 触发器 3 个 |
| `decisions/autocolonize_decisions.txt` | implementer | 入口决议 |
| `common/on_actions/00_autocolonize_on_actions.txt` | implementer | 脉冲挂载 |
| `localisation/autocolonize_l_english.yml` | implementer | 英文原文（UTF-8 **BOM**） |
| `descriptor.mod` | implementer | mod 元数据，**version 必须为 `1.0`** |
| `localisation/autocolonize_l_simp_chinese.yml` | loc-smith | 中文（专用编码，见第 9 节） |
| `tools/validate_paradox.py` | verifier | 静态校验器 |
| `docs/*.md` | 各研究任务 | 调研报告 |
| `thumbnail.png` | **Captain（已产出，勿动）** | mod 缩略图 640×640，由 CogView 生成后圆形裁切 |
| `gfx/interface/autocolonize_icon_*.png` | **Captain（已产出，勿动）** | 游戏内图标 64/32px |
| `artwork/**` | **Captain（已产出，勿动）** | 图标生成脚本、候选图与提示词存档 |

> **图标资产已由 Captain 完成，实现者与发布物料任务只需引用，不得重新生成或覆盖。**
> 素材来源与提示词见 `artwork/ARTWORK_MANIFEST.json` 与 `artwork/candidates/prompts_round*.json`。
> `descriptor.mod` 可保留 `picture="thumbnail.png"` 字段（该文件已存在于仓库根）。

## 2. 状态变量契约（country scope）

**重要事实：EU4 的 country_flag 是布尔量，不能存字符串。**
说明书里的 `autocolonize_target = australia` **无法实现**，改为「每个目标一个 flag」。

| Flag | 含义 |
|---|---|
| `autocolonize_active` | 总开关，存在即启用 |
| `autocolonize_mode_continent` | 当前模式 = 次大陆 |
| `autocolonize_mode_trade_node` | 当前模式 = 贸易节点 |
| `autocolonize_sort_distance` | 排序 = 由近到远 |
| `autocolonize_sort_development` | 排序 = 发展度由高到低 |
| `autocolonize_target_<TARGET_ID>` | 当前目标；**同一时刻有且仅有一个** |

- `<TARGET_ID>` 规则：次大陆直接用 superregion 脚本名（如 `oceania_superregion`）；贸易节点用节点脚本名（如 `malacca`）。
- 例：`autocolonize_target_oceania_superregion`、`autocolonize_target_malacca`。
- 设置新目标前**必须**先清除所有 `autocolonize_target_*` flag。

## 3. 事件 id 契约

| id | 类型 | 作用 |
|---|---|---|
| `autocolonize.1` | country_event，hidden，is_triggered_only | 模式选择（次大陆 / 贸易节点 / 取消） |
| `autocolonize.2` | country_event，hidden，is_triggered_only | 排序偏好选择（近→远 / 高→低） |
| `autocolonize.3` | country_event，is_triggered_only | 目标列表（选项由 trigger 控制显隐） |
| `autocolonize.4` | country_event，is_triggered_only | 殖民完成 / 无目标可殖民 |
| `autocolonize.5` | country_event，hidden，is_triggered_only | 年度执行（脉冲调用） |

- `autocolonize.1`/`.2` 用 `hidden = yes` + 选项里 `trigger` 引导，保持流程连贯。
- 所有事件 `is_triggered_only = yes`，**不得**用 MTTH，避免随机触发。

## 4. Scripted effects 契约（`common/scripted_effects/autocolonize_effects.txt`）

| 名称 | 参数 | 作用 |
|---|---|---|
| `autocolonize_clear_target` | 无 | 清除全部 `autocolonize_target_*` flag |
| `autocolonize_reset_all` | 无 | 清除 `autocolonize_*` 全部 flag（关闭功能） |
| `autocolonize_run` | 无 | 年度执行总入口：按 mode + target 分派 |
| `autocolonize_colonize_superregion` | `$TARGET$` | 在指定 superregion 内按排序偏好殖民一个省份 |
| `autocolonize_colonize_trade_node` | `$TARGET$` | 在指定贸易节点内按排序偏好殖民一个省份 |

## 5. Scripted triggers 契约（`common/scripted_triggers/autocolonize_triggers.txt`）

| 名称 | 作用域 | 作用 |
|---|---|---|
| `autocolonize_province_is_colonizable` | province | 该省份是"可被本国殖民的空地" |
| `autocolonize_superregion_has_colonizable` | country | 入参 `$TARGET$`：该 superregion 是否还有可殖民省份 |
| `autocolonize_trade_node_has_colonizable` | country | 入参 `$TARGET$`：该贸易节点是否还有可殖民省份 |

## 6. 本地化 key 契约

- 决议：`autocolonize_decision_title` / `autocolonize_decision_desc` / `autocolonize_decision_stop_title` / `autocolonize_decision_stop_desc`
- 事件：`autocolonize.1.title` `autocolonize.1.desc` `autocolonize.1.a` `autocolonize.1.b` …（同 .2/.3/.4）
- 目标选项：`autocolonize_target_<TARGET_ID>`（选项名，如 `autocolonize_target_oceania_superregion: "大洋洲"`）
- 提示：`autocolonize_tooltip_active` / `autocolonize_tooltip_none`
- **规则**：英文文件里写的 key，中文文件必须逐个覆盖，key 集合必须完全一致。

## 6b. 事件选项数量上限（Captain 已实测，解除说明书的过度担忧）

说明书 §4.5 担心"16 个次大陆 + 大量贸易节点的选项会超出 EU4 事件选项上限（通常约 10-20 个）"。**Captain 实测原版后确认：这个上限比说明书说的宽松得多，不需要为此拆分事件。**

实测数据（扫描原版 `events/` 全部文件，统计单个事件的 option 数）：

| 事件 | option 数 | 文件 |
|---|---|---|
| `flavor_gbr.200` | **33** | `events/FlavorGBR.txt` |
| `9469` | 27 | `events/Dynastic.txt` |
| `estate_privileges_and_agendas_events.9` | 22 | `events/EstatePrivilegesAndAgendasEvents.txt` |
| `flavor_gbr.16` | 22 | `events/FlavorGBR.txt` |
| `fetishist_flavor.601/603` | 18 | `events/Fetishist.txt` |
| `pirates.1` | 16 | `events/PirateEvents.txt` |

**最关键的对照**：`flavor_gbr.200` 的 33 个选项**正是"每种贸易品一个选项"的同类模式**（`flavor_gbr.200.grain` / `.wine` / `.wool` …），与本 mod「每个可殖民目标一个选项」结构完全一致；且它**32/33 个选项都带 `trigger` 控制显隐**（只有第 1 个无条件），这也正是本 mod 的做法。`Dynastic.txt:9469` 同样是 27 个带 `trigger` 的选项（每个宗教组一个）。

**结论与要求**：
1. `autocolonize.3`（目标列表）与 `autocolonize.4`（完成事件续选）**可以放心为全部 16 个次大陆 + 全部收录贸易节点各写一个带 `trigger` 的选项**，总数 30+ 完全在原版实践范围内，**不需要拆成两个事件页**。
2. 每个选项都必须带 `trigger`（仅保留一个无条件兜底选项），与原版 `flavor_gbr.200` 的做法一致——这样实际显示数量会远小于选项总数。
3. 选项的 `name` 统一用 §6 的 `autocolonize_target_<TARGET_ID>`，本地化文件里为每个目标准备一条。

## 7. 目标 ID 契约

- 次大陆（**已由 T1 核实并修正，以下 16 个名在 `map/superregion.txt` 中全部真实存在**）：
  `india_superregion`, `east_indies_superregion`, `oceania_superregion`, `china_superregion`, `far_east_superregion`, `tartary_superregion`, `persia_superregion`, `south_america_superregion`, `central_america_superregion`, `andes_superregion`, `north_america_superregion`, `near_east_superregion`, `eastern_europe_superregion`, `europe_superregion`, `africa_superregion`, `southern_africa_superregion`
  - **已修正的 4 处**（原稿名不存在，见 `docs/SYNTAX_FINDINGS.md` §2d）：`amazonia→south_america_superregion`、`levant→near_east_superregion`、`western_europe→europe_superregion`、`northern_africa→africa_superregion`。
  - 注意 `africa_superregion` 实际含 maghreb/niger/guinea/sahel/horn_of_africa 五个 region，**覆盖范围比"北非"大得多**，显示名请用"非洲"而非"北非"。
- 贸易节点：实际定义在 `common/tradenodes/00_tradenodes.txt`（**不是** `common/trade_nodes/`）。

### 7.1 贸易节点最终清单（**Captain 审定，31 个，T3 以此为准**）

T2 产出 `docs/TARGET_LIST.md` 后，Captain **独立重算了全部 80 个节点的「1444 无主省数」**（直接解析 `history/provinces/*` 的 1444.11.11 归属 + 节点 `members`），发现 T2 的统计口径有偏差：

- T2 对美洲节点用的是「**殖民区成员省数**」（如 `mexico` 记 76），但殖民区里的省份**绝大多数在 1444 已属于原住民国家**（实测 mexico 节点 77 个成员中，72 个属于 AZT/TLA/TAR 等，仅 5 个无主）。**本 mod 的 `create_colony` 只能打无主省**，所以正确口径是「1444 无主省数」，不是殖民区省数。
- T2 对旧大陆的统计也有偏差：它记 `siberia=2`、`girin=2`，Captain 实测为 **30 和 19**；T2 因此把这两个**本应收录**的节点剔除了。

**Captain 实测的「1444 无主省数」Top（决定收录与否的依据）**：

| 节点 | loc 省 id | 无主 | 节点 | loc 省 id | 无主 |
|---|---|---|---|---|---|
| california | 2021 | 63 | patagonia | 2868 | 19 |
| carribean_trade | 1516 | 61 | girin | 730 | 19 |
| mississippi_river | 1507 | 45 | polynesia_node | 1997 | 18 |
| james_bay | 1486 | 44 | chesapeake_bay | 1500 | 17 |
| brazil | 1531 | 41 | african_great_lakes | 4064 | 17 |
| st_lawrence | 1490 | 39 | philippines | 1397 | 11 |
| australia | 1411 | 37 | zambezi | 1191 | 10 |
| panama | 835 | 37 | ethiopia | 2772 | 9 |
| amazonas_node | 2935 | 35 | north_sea | 1975 | 8 |
| laplata | 1536 | 32 | timbuktu | 1132 | 7 |
| siberia | 1064 | 30 | zanzibar | 1448 | 6 |
| the_moluccas | 1357 | 30 | malacca | 1361 | 6 |
| cuiaba | 800 | 27 | comorin_cape | 1340 | 5 |
| rio_grande | 2499 | 27 | mexico | 1551 | 5 |
| ivory_coast | 1466 | 22 | canton | 1371 | 4 |
| ohio | 2526 | 20 | hangzhou | 684 | 1 |
| cape_of_good_hope | 1460 | 20 | gulf_of_siam | 1365 | 1 |

**最终收录 31 个**（T2 的 25 个 + Captain 补入 6 个）：

1. **美洲 16**：`brazil`(1531)、`laplata`(1536)、`patagonia`(2868)、`amazonas_node`(2935)、`cuiaba`(800)、`lima`(809)、`mexico`(1551)、`california`(2021)、`rio_grande`(2499)、`ohio`(2526)、`mississippi_river`(1507)、`chesapeake_bay`(1500)、`carribean_trade`(1516)、`panama`(835)、`st_lawrence`(1490)、`james_bay`(1486)
2. **大洋洲 2**：`australia`(1411)、`polynesia_node`(1997)
3. **非洲 5**：`cape_of_good_hope`(1460)、`african_great_lakes`(4064)、`ivory_coast`(1466)、`zambezi`(1191)、`gulf_of_aden`(4346)
4. **东印度 2**：`the_moluccas`(1357)、`malacca`(1361)
5. **Captain 补入 6**：`siberia`(1064, 无主30)、`girin`(730, 无主19)、`philippines`(1397, 无主11)、`canton`(1371)、`hangzhou`(684)、`gulf_of_siam`(1365)

**为什么补入后 3 个（canton / hangzhou / gulf_of_siam）无主省很少也要收录**：用户说明书 §4.3 明确点名了「广州」「杭州」「暹罗」三个节点作为示例。它们虽然 1444 无主省少（4/1/1），但**选项带 `trigger`，无可殖民省份时会自动隐藏**，不会干扰玩家；而删掉会让用户找不到自己点名的目标。**代价为零，收益是符合用户预期。**

**为什么只收录 31 个而不是全部 33 个 ≥5 无主的节点**：受 §6b 的事件选项数预算约束。`autocolonize.3` 在贸易节点模式下 = 31 个目标选项 + 1 个取消选项 = **32 个 option**，仍在原版实测最大值（33）之内。因此**主动舍弃**了 `ethiopia`(9)、`north_sea`(8)、`timbuktu`(7)、`zanzibar`(6)、`comorin_cape`(5) 五个低频节点。若日后要补，必须同时把事件拆成两页。

> **T3 注意**：以本节 31 个节点为准，**不要**直接用 `docs/TARGET_LIST.md` 的 25 个（那份漏了 siberia/girin/philippines/canton/hangzhou/gulf_of_siam）。

## 8. 已由侦查确认的硬事实（实现时不得违反）

1. `is_owned_by = no` 在 1.37.5 原版脚本中**零出现** → 判定空地请用 `is_empty = yes`（原版权威用例 `INC_can_be_colonized_without_natives`，`common/scripted_triggers/00_scripted_triggers.txt:4508`）+ `is_colony = no` 作双保险。`is_empty = yes` 已蕴含无主，叠加 `is_colony = no` 不会误杀正常空地。

   **⚠️ 补充（Captain 验证，T1 未覆盖）：必须叠加 `is_wasteland = no`。**
   `is_empty = yes` 会命中**不可通行的荒地**（wasteland），而 `create_colony` 打在荒地上是无效/异常行为。原版凡是要"挑一块能用的空地"的地方都显式排除荒地（如 `common/estate_agendas/003_vaisya_agendas.txt:1159` 等多处 `is_wasteland = no`）。
   因此 `autocolonize_province_is_colonizable` 的最终判定应为三件套：

   ```text
   is_empty = yes        # 承重：无主空地
   is_wasteland = no     # 排除不可通行荒地（必须）
   is_colony = no        # 双保险：排除正在被殖民的省份
   ```

   **另需 `has_discovered = ROOT` 守卫**：原版殖民事件在挑目标时都带 `has_discovered = ROOT`（`events/Colonial.txt:971,980`），避免选中玩家还没探索到的省份。请在可殖民判定或目标筛选处一并加上。

   **原版更省事的替代**：引擎自带的 `random_empty_neighbor_province` / `any_empty_neighbor_province` 语义即"可殖民且无主的相邻省份"（`events/Colonial.txt:24,970,978`），引擎已替你做完全部合法性校验。**但它的范围是"相邻省份"，无法跨洋到目标次大陆**，所以本 mod 的主方案仍是 `is_empty + is_wasteland + is_colony` 三件套；仅在"距离最近的空地"这类近场逻辑上可考虑用它。
2. `any_province_in_superregion` / `every_province_in_superregion` 在原版脚本中**零出现**。T1 已核实两种正确写法：
   - **效果遍历**：`<superregion名> = { limit = {...} <效果> }`（原版 `common/on_actions/00_on_actions.txt:1829,1877` 用 `china_superregion = { ... }`）。**这是 T3 必须采用的主方案。**
   - **触发过滤**：`any_province = { superregion = X ... }`（`common/estate_agendas/03_burgher_agendas.txt:1997`，该处原注释明说 superregion scope 受 load order 影响）。
3. `trade_node = <节点名>` 作为独立 trigger 在原版脚本中**零出现**。进入贸易节点的正确方式（**Captain 已独立验证**）：

   **关键机制：贸易节点作用域本身就是省份作用域。** wiki 原文 "Scopes to one valid tradenode (province)"（`E:\\AI\\.eu4wiki_cache\\raw_Scopes.txt:687`）。每个节点在 `common/tradenodes/00_tradenodes.txt` 里有一个 `location = <省id>`，**以该省 id 为作用域即进入该节点**，内部即可用 `every_trade_node_member_province` / `random_trade_node_member_province` 遍历成员省份。

   原版范例：`european_trade_node_scope`（`common/scripted_triggers/00_scripted_triggers.txt:1907-1931`）就是把 23 个节点的 location 省 id 逐个写成 `1293 = { $trigger$ }`、`1295 = { $trigger$ }` …；成员遍历见 `events/FlavorTUR.txt:2432,2444`。

   **对 T3 的硬性要求**：EU4 脚本**无法从节点名反查 location 省 id**（没有这种函数）。因此贸易节点模式必须**为每个收录节点硬编码其 location 省 id**，形如：

   ```text
   autocolonize_colonize_trade_node = {
       if = { limit = { has_country_flag = autocolonize_target_malacca }
           1361 = { every_trade_node_member_province = { limit = { ... } ... } } }
       if = { limit = { has_country_flag = autocolonize_target_canton }
           1371 = { every_trade_node_member_province = { limit = { ... } ... } } }
       # ... 每个收录节点一段
   }
   ```

   **✅ 该机制已获原版正面印证（Captain 验证）**：原版存在 **15 处** `<省id> = { every_trade_node_member_province = { ... } }` 的写法，例如：

   ```text
   # missions/DOM_Japanese_Missions.txt:283-292   （马六甲节点，省 id 1361）
   hidden_effect = {
       1361 = {
           every_trade_node_member_province = {
               limit = { NOT = { owned_by = ROOT }  NOT = { is_core = ROOT } }
               add_permanent_claim = ROOT
           }
       }
   }

   # missions/SCA_Finnish_Missions.txt:167-176      （波罗的海节点，省 id 1926）
   # missions/WOC_Dutch_Missions.txt:1465-1474     （英吉利海峡节点，省 id 1269）
   ```

   注意这三处的省 id（**1361 / 1926 / 1269**）与本文件下方映射表中的 `malacca 1361` / `baltic_sea 1926` / `english_channel 1269` **完全吻合**，构成对映射表的独立交叉验证。

   节点名 → location 省 id 的完整映射（**Captain 已从原版提取，共 80 个节点，T3 直接取用，不要自己重新解析**）：

   ```text
   african_great_lakes 4064 | kongo 4097 | zambezi 1191 | patagonia 2868 | amazonas_node 2935
   rio_grande 2499 | james_bay 1486 | california 2021 | girin 730 | mississippi_river 1507
   ohio 2526 | mexico 1551 | lhasa 677 | chengdu 679 | burma 584 | gulf_of_siam 1365
   canton 1371 | philippines 1397 | cuiaba 800 | lima 809 | polynesia_node 1997
   australia 1411 | nippon 1376 | hangzhou 684 | xian 700 | beijing 4233
   the_moluccas 1357 | siberia 1064 | yumen 707 | malacca 1361 | ganges_delta 1343
   doab 524 | lahore 507 | deccan 1948 | comorin_cape 1340 | gujarat 504
   katsina 1149 | ethiopia 2772 | gulf_of_aden 4346 | hormuz 1334 | zanzibar 1448
   cape_of_good_hope 1460 | basra 1335 | samarkand 454 | persia 4341 | aleppo 377
   alexandria 358 | astrakhan 464 | crimea 1322 | constantinople 1320 | kiev 280
   kazan 1082 | novgorod 33 | laplata 1536 | brazil 1531 | timbuktu 1132
   ivory_coast 1466 | tunis 341 | ragusa 137 | safi 1110 | pest 153 | krakow 262
   wien 134 | saxony 61 | baltic_sea 1926 | rheinland 1876 | panama 835
   carribean_trade 1516 | chesapeake_bay 1500 | st_lawrence 1490 | white_sea 1652
   north_sea 1975 | lubeck 45 | bordeaux 1276 | sevilla 1293 | champagne 186
   valencia 1295 | genua 1298 | venice 1308 | english_channel 1269
   ```

   （`girin 730` 已由 Captain 复核原文确认，见 `common/tradenodes/00_tradenodes.txt:234-235`。）
4. `create_colony = <发展度>` 是真实 effect（原版 `events/Colonial.txt` 用 `create_colony = 200`）。
5. 原版 `on_actions` 中 `on_yearly_pulse` / `on_monthly_pulse` 均存在，默认块为空。
6. 殖民距离（colonial range）在 province scope 下**无对应 trigger**；按说明书务实方案处理：不在 trigger 里判定距离，交给引擎在实际殖民时裁定。

7. **⚠️ 「由近到远」排序：说明书给的 `distance = { who = ROOT value = 50 }` 写法是错的，Captain 已核实。**
   全量检索 1.37.5 原版脚本（排除 patchnotes）得到的事实：
   - `distance = { ... }` 这种**块形式零命中**（38 处命中全部是 `border_distance = {` / `custom_ignore_coring_distance = {` 这类名字里含 "distance" 的**别的**触发器，不是 distance 本身）。
   - 真正存在的 `distance` 是 **`border_distance` 块内的子参数**，语法为 `distance = <数值>`，**且是国与国之间的距离**，不是省份到省份。原版用例：
     ```text
     NOT = { border_distance = { who = root  distance = 200 } }   # common/estate_agendas/02_noble_agendas.txt:521-526
     NOT = { border_distance = { who = FROM  distance = 200 } }   # common/cb_types/00_cb_types.txt:1211-1216
     ```
   - 原版**不存在**任何"省份到首都/省份到省份"的距离触发器（`province_distance` / `distance_to` / `colonial_distance` 等全部零命中）。

   **因此 T3 必须这样实现「由近到远」**（按优先级降级，不要硬造不存在的语法）：

   **方案 A（推荐，最省事且零风险）**：不做真距离，用**发现状态 + 邻近性**近似"近"：
   - 排序用 `has_discovered = ROOT`（原版真实触发器，多处使用如 `common/estate_agendas/0002_rajput_agendas.txt:867`）优先，未探索的排后。
   - 同一批已发现的省份中，用 `is_empty = yes` 的**邻接扩张**特性自然形成"从已有领地往外推"的效果——因为 `create_colony` 本身受引擎的殖民距离校验，实际能殖民的自然就是近的。

   **方案 B（更接近"由近到远"，实现成本中等）**：用 `border_distance` 做**国家层面的分段**：
   对每个候选省份的 `owner`（无主则跳过）或对本国与"该省份所在区域"的距离做粗筛，但**无主省份没有 owner，此路基本不通**。

   **方案 C（最贴近原意，但代码量大）**：**人工把每个目标区域的省份按距离分档硬编码**（例如大洋洲目标内，按到最近本国省份的航海距离分 3 档省 id 列表）。这是唯一能真正实现"由近到远"的办法，但需要为 16 个次大陆 + 若干贸易节点各维护一份省 id 分档表，工作量极大。

   **Captain 的裁定**：T3 **采用方案 A**。理由：① 方案 B 对无主省份不可行；② 方案 C 的工作量与 v1.0 的交付目标不匹配，且省 id 分档表容易出错；③ 引擎的殖民距离校验本身就把"太远殖民不了"的省份挡在外面，方案 A 的近似在实际游戏体验上已足够接近"由近到远"。
   **请在 T3 交付说明中如实写明**：「由近到远」为近似实现（优先已探索 + 引擎殖民距离自然筛选），非严格距离排序，原因是 1.37.5 无省份级距离触发器。这条限制也要写进 README 的"已知限制"。

8. **发展度排序可行**：`development = <数值>` 是真实 trigger（原版 `common/buildings/00_buildings.txt:686,690,694` 等多处）。「发展度从高到低」用分段筛选实现即可（如先试 `development = 10`，再 `development = 5`，最后兜底），这是说明书的建议方案，Captain 确认可行。

9. 原版脚本文件可能不是 UTF-8（`events/Colonial.txt` 为 cp1252）→ 读原版文件时注意编码。

## 9. 中文本地化硬规则（loc-smith 必读，来自本项目既有经验）

- 文件必须 **UTF-8 with BOM**，否则游戏不加载。
- 普通 UTF-8 中文会渲染成 `????????`；必须用**三字符转义**：`[marker][b1][b2]`（b1/b2 = 该字 UTF-16LE 低/高字节）。
- marker：`0x10` 原样；`0x11` 低字节命中禁用集（+14）；`0x12` 高字节命中禁用集（−9）；`0x13` 双命中。
- 低字节禁用集：`00 0A 0D 20 22 23 24 2F 3A 3B 3D 40 5B 5C 5D 5F 7B 7D 7E 80 A3 A4 A7 BD`
- 高字节禁用集：`20 22 5B 5C 5D 5F 7B 7D 7E 80`
- 字节 `0x80-0x9F` 以 cp1252 对应 Unicode 码位存储（如 0x85 → U+2026）。
- **现成工具**：`E:\AI\encode_cn_final.py`（编码 + 往返自检 + 写盘），必须先读它并复用，不要另起炉灶。
- 参照样例：汉化 mod `E:\SteamLibrary\steamapps\workshop\content\236850\2976470733`。

## 10. 验收基线（全项目）

1. 所有 `.txt` 花括号平衡、无未闭合 scope。
2. 所有事件 id 唯一、namespace 正确。
3. 所有被引用的 scripted_effect / scripted_trigger 都有定义。
4. 所有被引用的 localisation key 在英文文件中存在，且中英 key 集合一致。
5. 决议 `potential` 含 `ai = no`；年度事件含 `ai = no` + `has_country_flag = autocolonize_active`。
6. 不修改任何原版文件；所有新增内容走 mod 覆盖机制。

## 11. GitHub 发布契约（v1.0 / MIT）

| 项 | 值 |
|---|---|
| 仓库名 | `eu4-autocolonize` |
| 账号 | `Drhusku`（本机 `gh` 已登录） |
| 可见性 | **public** |
| 许可证 | **MIT**，`LICENSE` 置于仓库根，版权行 `Copyright (c) 2026 Drhusku` |
| 版本 | `v1.0`（git tag + GitHub Release） |
| 默认分支 | `main` |

**仓库根必须包含：**

1. `LICENSE` — 标准 MIT 全文（不得改动条款文字）。
2. `README.md` — 中文为主、附英文摘要，须含：功能说明、安装步骤（含 `path` 需按玩家本机改写这一 EU4 通病）、使用方法（决议→模式→排序→目标→年度自动殖民）、已知限制（殖民距离脚本层不可判定、驱逐少数民族未实现、完成事件选项数受引擎上限约束）、目录结构、许可证声明。
3. `.gitignore` — 忽略 `.tmp/`、`*.log`、`__pycache__/` 等。
4. mod 源码目录（`events/`、`common/`、`decisions/`、`localisation/`、`descriptor.mod`）。

**发布硬要求：**

- `descriptor.mod` 内 `version="1.0"`、`supported_version="v1.37.*"`。
- 推送前必须确认工作区干净（`git status` 无未提交改动）。
- 打 tag `v1.0` 并创建 Release，标题 `v1.0 — 首个公开版本`。
- **不得**把 `E:\AI\eu4_autocolonize` 之外的任何文件（含游戏原版文件、其他 mod、个人路径下的杂物）提交进仓库。
- 推送后必须回读仓库内容（`gh repo view`、`git ls-remote`）确认远端与本地一致。

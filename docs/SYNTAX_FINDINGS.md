# EU4 1.37.5 自动殖民 mod — 核心语法核实结论（SYNTAX_FINDINGS）

> 依据：游戏原版脚本（安装于 `E:\SteamLibrary\steamapps\common\Europa Universalis IV`）实地检索。
> 本机路径下全部文件路径相对该游戏根目录。除特别注明外均为**原版脚本 文件:行号**证据。
> 补充参考：本机已有 EU4 wiki 快照 `E:\AI\.eu4wiki_cache\raw_Scopes.txt`（作用域权威清单）。

---

## 0. 一句话总览

- 判定"可殖民的无主空地"：**`is_empty = yes`** 是承重项（原版即如此），`is_colony = no` 是保险丝（可选，二者语义不冲突，见 Q1）。
- 遍历 superregion：**没有 `any_province_in_superregion`**；换用 **`<superregion脚本名> = { limit = {...} <效果> }`（作用域直接按 superregion 名展开，原版 on_actions 在用）**，或触发里 `any_province = { superregion = X ... }`。
- 进入具体贸易节点：**不能 `trade_node = <节点名>`**；用**该节点的 location 省 id** 进入节点作用域，再 `every_trade_node_member_province`（原版如此）。
- `create_colony = 200` 是真实效果，隐患在**目标必须为空地**（`events/Colonial.txt:47,995`）。
- 殖民距离：**脚本层无触发可判**，交给引擎在 `create_colony` 时裁定。

---

## Q1. 判定"可被本国殖民的无主空地"的 trigger 组合

**结论：** 原版判定可殖民空地以 `is_empty = yes` 为核心（无主 = 无定居者），可叠加 `is_colony = no` 以进一步排除正在被殖民的省份（保险）。

原版权威用例（官方"可被殖民"脚本触发）：

```text
# common/scripted_triggers/00_scripted_triggers.txt:4508-4556
INC_can_be_colonized_without_natives = {
    is_empty = yes                          # ← 承重：无主空地
    OR = { ... }                            # ← 官方限定可殖民区域（按省 id）
    any_neighbor_province = {               # ← 邻接判定（可作范围代理，见 Q5）
        country_or_non_sovereign_subject_holds = ROOT
    }
}
```

证据：
- `is_empty` 在原版 events 中出现 136 处（如 `events/ExplorationEvents.txt:23`、`events/Anglican_events.txt:561`）。
- `is_colony = yes` / `is_colony = no` 是合法省份触发，`events/Colonial.txt:8`（=yes）与 `:14`（=no）。
- 引擎原生"可殖民且无主"的邻居作用域 `random_empty_neighbor_province = { }` 在原版大量用于殖民投放目标（`events/Colonial.txt:24,978` 等 10 处），其语义即"colonizable and uncolonized"（范围/殖民资格由引擎判定）。

**语义提示（避免实现者踩坑）：** 正在被殖民的省份属于其殖民者（有主），因此天然满足 `is_empty = no`。所以 `is_empty = yes` 与 `is_colony = no` 在逻辑上不冲突（is_colony=no 基本被 is_empty=yes 蕴含），叠加 `is_colony = no` 只是"双保险"，不会误杀正常空地。原版 `INC_can_be_colonized_without_natives` 就用的是 is_empty（未再写 is_colony）。

**mod 可照抄的写法：**

```text
# 省份作用域脚本触发 autocolonize_province_is_colonizable（实现者可用）
is_empty = yes
is_colony = no       # 等价 NOT = { is_colony = yes }；保险叠加（见上）
```

---

## Q2. 如何遍历某个 superregion 内的所有省份

**结论：** 说明书中的 `any_province_in_superregion` / `every_province_in_superregion` 在原版**零出现**（全游戏检索，0 命中）。正确写法有二：

### 2a. 作用域直接按 superregion 名展开（效果遍历，推荐，原版在用）

```text
# common/on_actions/00_on_actions.txt:1829-1834
china_superregion = {          # ← superregion 脚本名即作用域名（= map/superregion.txt 里的块名）
    limit = {
        NOT = { is_core = ROOT }
    }
    add_permanent_claim = ROOT  # 内部为省份作用域；把 add_permanent_claim 换成你的殖民逻辑即可
}
```

- 同文件 `:1877` 又一处 `china_superregion = { ... }`。
- 作用域列表佐证（次权威）：`E:\AI\.eu4wiki_cache\raw_Scopes.txt:225-230`：`<superregion> = { }`，多重子作用域，实例 `india_superregion = { }`。

### 2b. 触发式：`any_province` + `superregion = <名>` 过滤器

```text
# common/estate_agendas/03_burgher_agendas.txt:1997-2002
# 原文件注释原文：'india_superregion scope does not work due to load order'
any_province = {
    superregion = india_superregion   # 省份作用域内 superregion 触发过滤
    has_port = yes
    range = ROOT
    has_discovered = ROOT
}
```

- 同一 superregion 触发过滤也出现在 `common/achievements.txt:6840-6841`（`any_owned_province = { superregion = india_superregion }`）。
- 注意 `03_burgher_agendas.txt:1997` 的注释恰好印证：superregion **没有**独立"遍历"作用域关键字，走的是"任意省份 + superregion 过滤"。

### 2c. 触发式：superregion 双作用域 + `type = all`（用于"某 superregion 全体满足条件"）

```text
# common/achievements.txt:7110-7113
china_superregion = {
    type = all
    owned_by = ROOT
}
```
同样实例：`common/achievements.txt:7420`、`:9368`；`common/mercenary_companies/00_mercenaries.txt:1863,1877`。

### 2d. superregion 脚本名清单（重要——据 `map/superregion.txt` 核实）

原版 `map/superregion.txt` 共 25 个超级区，块名即作用域名。**与 DESIGN() 第 7 节存在 4 处名字需要修正（给 Captain/T2 的上报项）：**

| DESIGN() 给定名 | 原版实际块名（行号） | 说明 |
|---|---|---|
| `amazonia_superregion` | **`south_america_superregion`**（superregion.txt:86，文件内注释 # amazonia） | 改名 |
| `levant_superregion` | **`near_east_superregion`**（superregion.txt:116） | 改名（含 anatolia/mashriq/arabia/egypt） |
| `western_europe_superregion` | **`europe_superregion`**（superregion.txt:30） | 改名 |
| `northern_africa_superregion` | **`africa_superregion`**（superregion.txt:71，含 maghreb_region） | 无单一"北非"，用 africa（或 africa+近东 egypt） |
| 其余 12 个 | 与 DESIGN 一致 | india/east_indies/oceania/china/far_east/tartary/persia/andes/north_america/central_america/eastern_europe/southern_africa 均在 |

> DESIGN 目标清单里这 4 个 superregion 名不存在，实现时不能照抄，需改用上表实际名。

---

## Q3. 进入某个具体贸易节点 scope 并遍历其成员省份

**结论：** `trade_node = <节点名>` 作为独立触发在原版**零出现**（检索 0 命中，含行首 `trade_node =`）。正确的"进入+遍历"写法：

### 3a. 遍历"某贸易节点作用域内所有成员省份"

`any/every/random_trade_node_member_province` 都是真实省作用域，前提是**已处在某个贸易节点作用域**内：

```text
# events/FlavorTUR.txt:2432-2455   （home_trade_node 进入 + every_trade_node_member_province 遍历）
home_trade_node_effect_scope = {          # 进入本国主贸易港所在节点作用域
    add_trade_modifier = { ... }
    every_trade_node_member_province = {  # ← 遍历该节点所有成员省
        limit = { owned_by = ROOT }
        add_province_modifier = { ... }
    }
}
```

```text
# events/PropagateReligionEvents.txt:20-34   （any_active_trade_node + any_trade_node_member_province）
any_active_trade_node = {
    any_trade_node_member_province = {
        owned_by = ROOT
        NOT = { religion_group = muslim }
        has_port = yes
        NOT = { has_province_modifier = trading_settlement }
    }
}
```

进入贸易节点作用域的入口作用域（均可加 `limit` 过滤）：
- `home_trade_node` / `home_trade_node_effect_scope` —— 本国主贸易港节点（events/FlavorTUR.txt:2432）。
- `any_active_trade_node`（events/institutions.txt:1796,1815；PropagateReligionEvents.txt:20）
- `any_trade_node`（events/PrivateerEvents.txt:421）、`random_trade_node`（PrivateerEvents.txt:445）、`all_trade_node` / `random_active_trade_node`

### 3b. 如何进入"某个具体"贸易节点（如 malacca）—— 用节点 location 省 id

原版**没有**按节点脚本名直接 scope 的写法；进入特定节点的稳妥法 = 用**该节点的 `location` 省 id** 作为省作用域（引擎把节点 location 省视作节点作用域）。原版现成范例：

```text
# common/scripted_triggers/00_scripted_triggers.txt:1908-1932
european_trade_node_scope = {   # ← 就是靠"省 id 作用域"逐个进入欧洲各节点
    1293 = { $trigger$ }
    1295 = { $trigger$ }
    280  = { $trigger$ }
    ...  # 每个数字 = 该节点 location 省 id
}
```

节点 location 省 id 从 `common/tradenodes/00_tradenodes.txt` 读（malacca 节点定义在 :796，其 `location=1361` 在 :797；members= 在 :816）。

**mod 可照抄的写法（以 malacca 为例）：**

```text
1361 = {                                  # malacca 的 location 省 id（common/tradenodes/00_tradenodes.txt:797）
    random_trade_node_member_province = { # 或 every/any_trade_node_member_province
        limit = {
            is_empty = yes
            is_colony = no
            # ... 目标排序条件
        }
        create_colony = 200
    }
}
```

标识某节点 location 省的触发：`province_id = 1361`（原版 is_trade_node_province 即用 `province_id` 列表标识节点省，见 00_scripted_triggers.txt:1725-1811）。

**注意路径名：** DESIGN 写的是 `common/trade_nodes/`，实际目录是 **`common/tradenodes/`**（单个 `00_tradenodes.txt`）。

---

## Q4. create_colony effect 的正确用法与参数含义

**结论：** `create_colony = <数值>` 是真实效果，作用于**省作用域**，数值 = 殖民地人口/定居值，200 = 满殖民。目标省必须是"可殖民且无主"。

原版用法：

```text
# events/Colonial.txt:43-52
option = {
    name = "EVTOPTA6138"
    goto = empty_neighbor_target
    event_target:empty_neighbor_target = {
        create_colony = 200            # ← 第 47 行；对 event_target 指向的空地建立满殖民
        add_province_modifier = { ... }
    }
}
```

- **`events/Colonial.txt:47`** 与 **`events/Colonial.txt:995`** 各一处 `create_colony = 200`。
- 投放目标来自 `random_empty_neighbor_province = { save_event_target_as = empty_neighbor_target }`（Colonial.txt:24-26）——即"可殖民且无主"的邻居省。
- 含义：`create_colony = X` 把该省设为有主（殖民者所有），定居值 = X；X = `200` = 直接建成（原版殖民进度以 0-200 计，满 200 成城）。该效果会**消耗该省的殖民资格**（同一省不会反复生效）。

**mod 警告：** `create_colony` 对非空地可能行为异常（如已是城市），投放前务必确保目标是 `is_empty = yes` 的空地。

---

## Q5. 殖民距离在脚本层是否可判定

**结论：** **不可判定**（无专门的殖民距离/殖民范围省触发）。与 DESIGN 硬事实第 8.6 节一致。

证据：
- 全游戏检索 `colonial_range` /`colonization_range` /`can_be_coloniz` /`can_colonize` /`within_colonial` /`colonial_distance`：仅命中官方手写的按区域/省 id 判定 `INC_can_be_colonized_without_natives`（见 Q1）与 flavorMAL 的自定义 flag（`events/flavorMAL.txt:1773-1799`，非范围触发）。**没有任何"殖民范围"触发**。
- 原版殖民资格（含范围判定）被引擎内置于"可殖民"概念中，体现在 `random_empty_neighbor_province` 等作用域（wiki 快照 raw_Scopes.txt:748,770,1367,1388 均描述为 "colonizable and uncolonized"），**脚本层无法单独测试范围**。

**mod 务实方案（照 DESIGN 硬事实 8.6）：** 不写范围触发；直接挑选空地（`is_empty` + `is_colony`）投 `create_colony`，把是否在殖民范围内交给引擎在实际殖民时裁定（越范围会失败/无殖民者投放）。可选的弱代理 = 邻接判定：

```text
# 代理：优先在已稳省份邻接格殖民（原版 INC 触发就用它，见 Q1）
any_neighbor_province = {
    country_or_non_sovereign_subject_holds = ROOT
}
```

> 注意这只是"邻接本国领土"，并不等同殖民范围（殖民范围可覆盖数跳/跨海）。如需真正范围控制，只能借引擎能力（如以 country 逻辑处理）或把目标限定在已发现的邻接省。

---

## 附：与 DESIGN 说明书的语法冲突逐条对照

| DESIGN 写 | 原版核实 | 正确替代（证据） |
|---|---|---|
| `is_owned_by = no`（判定空地） | 原版零出现 | `is_empty = yes`（common/scripted_triggers/00_scripted_triggers.txt:4509；events/ExplorationEvents.txt:23） |
| `any_province_in_superregion`（遍历 superregion） | 零出现 | superregion 名作用域 `china_superregion = { limit=... }`（common/on_actions/00_on_actions.txt:1829）；或 `any_province = { superregion = X }`（common/estate_agendas/03_burgher_agendas.txt:1997） |
| `trade_node = <节点名>`（进具体节点） | 零出现 | 节点 location 省 id 作用域（common/scripted_triggers/00_scripted_triggers.txt:1908）+ `every_trade_node_member_province`（events/FlavorTUR.txt:2445） |
| superregion 目标清单（第 7 节部分名） | 4 个名字不存在 | 用 superregion.txt 实际块名（见 2d 表格） |
| `common/trade_nodes/` | 实际 `common/tradenodes/` | 单文件 00_tradenodes.txt |

---

## 附：引用证据索引（全部原版，可复核）

| 结论 | 文件:行号 |
|---|---|
| 可殖民空地核心触发 is_empty | common/scripted_triggers/00_scripted_triggers.txt:4508-4556（INC_can_be_colonized_without_natives） |
| is_empty 事件用例 | events/ExplorationEvents.txt:23 |
| is_colony 触发 | events/Colonial.txt:8（=yes）、:14（=no） |
| superregion 作用域遍历（效果） | common/on_actions/00_on_actions.txt:1829-1834、:1877 |
| superregion 触发过滤 | common/estate_agendas/03_burgher_agendas.txt:1997-2002；common/achievements.txt:6840-6841 |
| superregion type=all 双作用域 | common/achievements.txt:7110-7113、:7420、:9368 |
| superregion 脚本名定义 | map/superregion.txt（india :3 等，共 25 块） |
| any_province_in_superregion 零出现 | 全游戏检索 0 命中 |
| 贸易节点进入 | events/FlavorTUR.txt:2432（home_trade_node_effect_scope）；events/institutions.txt:1796（any_active_trade_node）；events/PrivateerEvents.txt:421（any_trade_node）、:445（random_trade_node） |
| 成员省遍历 | events/FlavorTUR.txt:2445（every_trade_node_member_province）；events/PropagateReligionEvents.txt:28（any_trade_node_member_province）、:54（random_trade_node_member_province） |
| 具体节点 = location 省 id | common/scripted_triggers/00_scripted_triggers.txt:1908-1932（european_trade_node_scope）；is_trade_node_province :1725 |
| 节点 location 值 | common/tradenodes/00_tradenodes.txt:796-797（malacca, location=1361） |
| trade_node= 零出现 | 检索 0 命中 |
| create_colony | events/Colonial.txt:47、:995 |
| empty_neighbor 投放目标 | events/Colonial.txt:24-26（random_empty_neighbor_province） |
| 殖民范围无触发 | 检索无 colonial_range 触发；wiki 快照 raw_Scopes.txt:748,1367（"colonizable and uncolonized" 语义在引擎） |

*（wiki 快照仅作作用域名/语义的正交佐证；全部脚本结论以上表"原版脚本 文件:行号"为准。）*

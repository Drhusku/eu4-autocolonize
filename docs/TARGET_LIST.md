# 次大陆与贸易节点目标清单（EU4 1.37.5 实际存在性核实）

> 依据：原版 `map/superregion.txt`、`common/tradenodes/00_tradenodes.txt`、`common/colonial_regions/00_colonial_regions.txt`、`history/provinces/*`、`localisation/areas_regions_l_english.yml`（均为 1.37.5 安装内容）。
> 直接结论：**可收录 16 个次大陆 + 25 个贸易节点**（脚本标识符可直接给 T3/T4）。

---

## 一、次大陆目标清单（16 个）

逐个核实 DESIGN 第 7 节 16 个名字：12 个拼写正确，4 个 DESIGN 名在 1.37.5 **不存在**（已给正确脚本标识符，T1 已上报）。显示名来自游戏本地化。

| # | DESIGN §7 名 | 最终脚本标识符（superregion 作用域名） | 存在性 | 原版文件:行号（存在性证据） | 显示名（loc） | 备注 |
|---|---|---|---|---|---|---|
| 1 | `india_superregion` | `india_superregion` | **存在** | `map/superregion.txt:3` | India（loc:2534） | — |
| 2 | `east_indies_superregion` | `east_indies_superregion` | **存在** | `map/superregion.txt:11` | East Indies（loc:2531） | — |
| 3 | `oceania_superregion` | `oceania_superregion` | **存在** | `map/superregion.txt:19` | Oceania（loc:2586） | — |
| 4 | `china_superregion` | `china_superregion` | **存在** | `map/superregion.txt:24` | China（loc:2528） | — |
| 5 | `western_europe_superregion` | `europe_superregion` | 不存在→改名 | `map/superregion.txt:30` | Western Europe（loc:2507） | DESIGN 名不存在 → 改名 |
| 6 | `eastern_europe_superregion` | `eastern_europe_superregion` | **存在** | `map/superregion.txt:44` | Eastern Europe（loc:2577） | — |
| 7 | `tartary_superregion` | `tartary_superregion` | **存在** | `map/superregion.txt:57` | Tartary（loc:2580） | — |
| 8 | `far_east_superregion` | `far_east_superregion` | **存在** | `map/superregion.txt:65` | Far East（loc:2583） | — |
| 9 | `northern_africa_superregion` | `africa_superregion` | 不存在→改名 | `map/superregion.txt:71` | Northern Africa（loc:2513） | DESIGN 名不存在（无单一北非）→ 用 africa_superregion |
| 10 | `southern_africa_superregion` | `southern_africa_superregion` | **存在** | `map/superregion.txt:79` | Southern Africa（loc:2516） | — |
| 11 | `amazonia_superregion` | `south_america_superregion` | 不存在→改名 | `map/superregion.txt:86` | Amazonia（loc:2519） | DESIGN 名不存在 → 改名 |
| 12 | `andes_superregion` | `andes_superregion` | **存在** | `map/superregion.txt:91` | Andes（loc:2522） | — |
| 13 | `north_america_superregion` | `north_america_superregion` | **存在** | `map/superregion.txt:97` | North America（loc:2510） | — |
| 14 | `central_america_superregion` | `central_america_superregion` | **存在** | `map/superregion.txt:108` | Central America（loc:2525） | — |
| 15 | `levant_superregion` | `near_east_superregion` | 不存在→改名 | `map/superregion.txt:116` | Levant（loc:2537） | DESIGN 名不存在 → 改名 |
| 16 | `persia_superregion` | `persia_superregion` | **存在** | `map/superregion.txt:126` | Persia（loc:2540） | — |

> 说明：superregion 的作用域/触发名 = 上表"最终脚本标识符"（即 `map/superregion.txt` 块名，如 `china_superregion = {}`）。DESIGN 用显示名给的名（amazonia/levant/western_europe/northern_africa）应改为：amazonia→`south_america_superregion`、levant→`near_east_superregion`、western_europe→`europe_superregion`、northern_africa→`africa_superregion`。

---

## 二、贸易节点目标清单（25 个）

收录原则：**节点成员省中存在大量可殖民空地**。新大陆/澳洲用 `common/colonial_regions` 的殖民区成员数（"殖民区"列，最权威）；非洲/亚洲用 `history/provinces` 实测 1444 无主空土省数（"空土"列）。两列为 "`−`" 表示该指标不适用于该节点。

| # | 脚本标识符 | 原版文件:行号 | location 省 id | 殖民区省份数 | 1444空土省数 | 显示名建议 | 方向 |
|---|---|---|---|---|---|---|---|
| 1 | `brazil` | `00_tradenodes.txt:1455` | 1531 | 43 | − | Brazil | 美洲 |
| 2 | `laplata` | `00_tradenodes.txt:1440` | 1536 | 31 | − | Rio de La Plata | 美洲 |
| 3 | `patagonia` | `00_tradenodes.txt:76` | 2868 | 20 | − | Patagonia | 美洲 |
| 4 | `amazonas_node` | `00_tradenodes.txt:100` | 2935 | 34 | − | Amazonas | 美洲 |
| 5 | `cuiaba` | `00_tradenodes.txt:539` | 800 | 41 | − | Cuiaba | 美洲 |
| 6 | `lima` | `00_tradenodes.txt:572` | 809 | 31 | − | Lima | 美洲 |
| 7 | `mexico` | `00_tradenodes.txt:323` | 1551 | 76 | − | Mexico | 美洲 |
| 8 | `california` | `00_tradenodes.txt:193` | 2021 | 73 | − | California | 美洲 |
| 9 | `rio_grande` | `00_tradenodes.txt:133` | 2499 | 42 | − | Rio Grande | 美洲 |
| 10 | `ohio` | `00_tradenodes.txt:295` | 2526 | 67 | − | Ohio | 美洲 |
| 11 | `mississippi_river` | `00_tradenodes.txt:271` | 1507 | 66 | − | Mississippi River | 美洲 |
| 12 | `chesapeake_bay` | `00_tradenodes.txt:1845` | 1500 | 55 | − | Chesapeake Bay | 美洲 |
| 13 | `carribean_trade` | `00_tradenodes.txt:1812` | 1516 | 60 | − | Caribbean | 美洲 |
| 14 | `panama` | `00_tradenodes.txt:1797` | 835 | 43 | − | Panama | 美洲 |
| 15 | `st_lawrence` | `00_tradenodes.txt:1872` | 1490 | 49 | − | Gulf of St. Lawrence | 美洲 |
| 16 | `james_bay` | `00_tradenodes.txt:166` | 1486 | 47 | − | Hudson Bay | 美洲 |
| 17 | `australia` | `00_tradenodes.txt:633` | 1411 | 46 | 35 | Australia | 大洋洲 |
| 18 | `polynesia_node` | `00_tradenodes.txt:596` | 1997 | 9 | 17 | Polynesian Triangle | 大洋洲 |
| 19 | `cape_of_good_hope` | `00_tradenodes.txt:1138` | 1460 | − | 14 | Cape of Good Hope | 非洲 |
| 20 | `african_great_lakes` | `00_tradenodes.txt:1` | 4064 | − | 17 | Great Lakes | 非洲 |
| 21 | `ivory_coast` | `00_tradenodes.txt:1495` | 1466 | − | 11 | Ivory Coast | 非洲 |
| 22 | `zambezi` | `00_tradenodes.txt:57` | 1191 | − | 8 | Zambezi | 非洲 |
| 23 | `gulf_of_aden` | `00_tradenodes.txt:1072` | 4346 | − | 7 | Gulf of Aden | 非洲 |
| 24 | `the_moluccas` | `00_tradenodes.txt:736` | 1357 | − | 15 | The Moluccas | 东印度 |
| 25 | `malacca` | `00_tradenodes.txt:796` | 1361 | − | 6 | Malacca | 东印度 |

> 节点 location 省 id = 进入该节点作用域的省 id（见 SYNTAX_FINDINGS Q3）。
> 东印度方向：`malacca`（DESIGN 举例的主节点）与 `the_moluccas` 虽 1444 空土省数不高（6/15），但节点含大量可殖民群岛空地，故收录。

---

## 三、被剔除项及理由

### 3.1 次大陆（DESIGN §7 不存在的 4 个，已改名）
| DESIGN §7 名 | 1.37.5 实际 | 理由 |
|---|---|---|
| `amazonia_superregion` | 不存在 → 用 `south_america_superregion`（superregion.txt:86，loc "Amazonia"） | 脚本标识符不同，DESIGN 名无此块 |
| `levant_superregion` | 不存在 → 用 `near_east_superregion`（superregion.txt:116，含 anatolia/mashriq/arabia/egypt） | 同上 |
| `western_europe_superregion` | 不存在 → 用 `europe_superregion`（superregion.txt:30，loc "Western Europe"） | 同上 |
| `northern_africa_superregion` | 无单一"北非"superregion → 用 `africa_superregion`（superregion.txt:71，含 maghreb_region） | 北非没有独立 superregion |

> 另：`map/superregion.txt` 还有 `new_world_superregion`（:135，内容为空/占位）与 11 个海洋 superregion（:140-181），均**不作为**殖民目标收录。

### 3.2 贸易节点（80 个中收录 25，剔除 55）
剔除依据：成员省**无/极少 1444 可殖民空地**（多为已开发旧大陆或纯欧洲/海洋节点）。括号内为实测 1444 无主空土省数。
- **纯欧洲/旧大陆已开发节点**：`sevilla`、`lubeck`、`bordeaux`、`champagne`、`valencia`、`genua`、`venice`、`english_channel`、`north_sea`、`baltic_sea`、`rheinland`、`saxony`、`wien`、`krakow`、`ragusa`、`pest`、`constantinople`、`kiev`、`kazan`、`novgorod`、`astrakhan`、`crimea`、`white_sea`、`aleppo`、`alexandria`、`tunis`、`safi`
- **亚洲已开发节点（空土近 0）**：`hangzhou`、`xian`、`beijing`、`chengdu`、`lhasa`、`nippon`、`canton`、`doab`、`lahore`、`deccan`、`comorin_cape`、`gujarat`、`ganges_delta`、`burma`、`gulf_of_siam`、`samarkand`、`basra`、`hormuz`、`persia`
- **非洲/西伯利亚空土过少（<5）**：`kongo(2)`、`zanzibar(2)`、`timbuktu(1)`、`ethiopia(2)`、`katsina(1)`、`siberia(2)`、`girin(2)`、`yumen(3)`
- **东印度边缘（空土偏少）**：`philippines(4)`、`doab?否` — 仅 `philippines(4)` 因少于阈值排除

剔除证据示例（`history/provinces` 1444 无主空土数）：safi=0、tunis=1、kongo=2、zanzibar=2、timbuktu=1、ethiopia=2、katsina=1、siberia=2、girin=2、yumen=3、philippines=4。

---

## 四、T3/T4 可直接使用的最终清单

- **次大陆（N=16）**：`india_superregion`、`east_indies_superregion`、`oceania_superregion`、`china_superregion`、`europe_superregion`、`eastern_europe_superregion`、`tartary_superregion`、`far_east_superregion`、`africa_superregion`、`southern_africa_superregion`、`south_america_superregion`、`andes_superregion`、`north_america_superregion`、`central_america_superregion`、`near_east_superregion`、`persia_superregion`
- **贸易节点（M=25）**：见第二节表；进入各节点作用域用其 `location` 省 id（表内列出）。

> 提示：目标 flag 契约（DESIGN 第 2 节）中次大陆用 `autocolonize_target_<superregion名>`、贸易节点用 `autocolonize_target_<节点名>`，均以上表最终脚本标识符为准（4 个次大陆名已按实际修正）。

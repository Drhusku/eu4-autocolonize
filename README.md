# EU4 自动殖民（Auto Colonize）

**为《欧陆风云 IV》（Europa Universalis IV）1.37.5 制作的 mod**：通过一个决议按你选定的“次大陆”或“贸易节点”为目标，每年自动在其中殖民一块无主空地，直到该区域可殖民的省份被清空，再让你续选下一个目标，全程自动化，无需一个个手动送殖民者。

## 功能特性

1. **决议启动**：游戏内点一个决议启用“自动殖民”，再点另一个决议随时彻底关闭。
2. **选择模式**：在“按次大陆殖民”与“按贸易节点殖民”两种模式中二选一。
3. **选择排序**：支持“由近到远”或“由发展度从高到低”两种优选顺序。
4. **选择目标**：弹出目标列表（16 个次大陆，或 31 个含大量可殖民空地的贸易节点），每个目标一个选项；已无可用空地的目标会自动隐藏。
5. **年度自动殖民**：启用后，每年自动在该目标内挑选一块可行的空地建立殖民地；目标被完全殖民后，自动弹出下一个目标选择（完成事件续选）。

## 安装方法

1. **把 mod 内容放到游戏 mod 目录**：将本仓库内的 mod 内容（`events/`、`common/`、`decisions/`、`localisation/`、`gfx/` 等，以及 `thumbnail.png`）整个复制到：

    Documents/Paradox Interactive/Europa Universalis IV/mod/autocolonize/

2. **放置并修改描述文件**：把仓库根目录的 `descriptor.mod` 复制或改名为 `autocolonize.mod`，放到：

    Documents/Paradox Interactive/Europa Universalis IV/mod/autocolonize.mod

3. **⚠️ 必须改写 `path` 字段（EU4 mod 的通用坑）**：打开 `autocolonize.mod`，把其中的

    path = “mod/autocolonize”

    改为**你自己本机上的实际路径**，例如：

    path = “C:/Users/<你的用户名>/Documents/Paradox Interactive/Europa Universalis IV/mod/autocolonize”

    每个玩家的路径不同，这个字段**必须按本人的机器改写**，否则启动器会找不到 mod 文件。

4. **启动游戏**：在 Paradox 启动器中勾选启用 `Auto Colonize 自动殖民`，进入游戏即可。

## 使用方法

1. 进入游戏，打开**决策**面板（`D` 键），找到 **Enable Auto Colonize（启用自动殖民）** 决议并点击。
2. 在弹出的对话框选择**模式**：按次大陆（Subcontinent）或按贸易节点（Trade Node）。
3. 接着选择**排序**：由近到远（Distance）或由发展度从高到低（Development）。
4. 在弹出的**目标列表**点击想要的区域（次大陆模式显示次大陆；贸易节点模式显示贸易节点）。无可殖民空地的目标不会显示。
5. 此后每年会自动殖民一个省份；当前目标被完全殖民后会自动再次弹出目标列表，让你选下一个目标，或点 **Stop Auto Colonize（停止自动殖民）** 关闭。
6. 想彻底关掉时，用第二个决策 **Disable Auto Colonize（关闭自动殖民）**。

## 支持的排序规则

EU4 脚本引擎**没有内置的排序函数**，“由近到远 / 由发展度从高到低”都是近似排序，而非精确排序：

- **由近到远（Distance）**：脚本层无法获得“省份到玩家”的精确距离（EU4 没有省份级距离触发器），因此采用近似策略：优先选择**已经探索（discovered）**的省份；真正的殖民距离校验交由游戏引擎在实际建立殖民地时裁定，实际效果近似“从近处往外推”。
- **由发展度从高到低（Development）**：优先选择发展度较高（≥10）的无主空地，其次再落到任意可行的空地，近似“先占好地”。

## 已知限制

- **殖民距离无法在脚本层判定**：脚本里无法直接测试“某省份是否在你的殖民范围内”（EU4 无此触发器）。mod 只负责挑选无主空地并交给引擎建立殖民地，距离是否达标由游戏引擎在实际殖民时裁定——距离过远的省份不会被建立。
- **驱逐少数民族未实现**：本版本没有实现“驱逐当地原住民”的功能。
- **完成事件的选项数受引擎上限约束**：单个事件的可选选项数量有上限（原版实测上限约 33 项）。贸易节点模式下目标列表已控制在 31 个目标 + 1 个取消选项（共 32 项）。
- **年度脉冲的时机取决于国家 tag order id**：autocolonize 挂在游戏的年度脉冲（on_yearly_pulse）上，而年度脉冲对每个国家触发的实际日期并不固定为 1 月 1 日，而是与国家的 tag order id 有关，因此“每年自动殖民一次”的精确触发时刻会依国家而异，不影响功能。
- **界面文本为中文，依赖汉化 mod 提供字体**：本 mod 的决议与事件文本使用中文（三字符转义编码写入 `l_english` 槽位，与主流汉化 mod 的做法一致），**依赖「Chinese Language Mod for 1.37」（创意工坊 2976470733）提供中文字体**。未安装该汉化 mod 的玩家，界面文字会显示为乱码。若你想在其他语言环境使用，可参考 `localisation/autocolonize_l_english.yml.en-backup`（英文原文）自行替换。

## 目录结构

    eu4-autocolonize/
    ├── descriptor.mod              # mod 描述文件（安装时改 path）
    ├── thumbnail.png               # 启动器缩略图
    ├── events/
    │   └── autocolonize_events.txt # 事件 .1~.5（模式/排序/目标/完成/年度）
    ├── common/
    │   ├── on_actions/00_autocolonize_on_actions.txt   # 年度脉冲挂载
    │   ├── scripted_effects/autocolonize_effects.txt   # 5 个脚本效果
    │   └── scripted_triggers/autocolonize_triggers.txt # 3 个脚本触发器
    ├── decisions/autocolonize_decisions.txt           # 启用/关闭决议
    ├── localisation/
    │   ├── autocolonize_l_english.yml                 # 英文文本
    │   └── autocolonize_l_simp_chinese.yml            # 简体中文文本
    ├── gfx/interface/autocolonize_icon_*.png          # 游戏内图标
    ├── docs/                                          # 内部设计/调研文档（面向开发者）
    └── tools/                                         # 内部静态校验脚本（面向开发者）

> 附带的 `docs/`（设计契约与语法调研）与 `tools/`（校验脚本）面向开发者；普通玩家只需要 `events/`、`common/`、`decisions/`、`localisation/`、`gfx/`、`descriptor.mod` 与 `thumbnail.png`。

## 兼容性

- **游戏版本**：EU4 **1.37.5**（`supported_version = “v1.37.*”` 已写入 `descriptor.mod`）。理论可向下兼容 1.37.x，但仅针对 1.37.5 实测。
- **语言**：内置简体中文与英文，两种均可正常显示。

## 许可证

本项目以 **MIT License** 开源发布，详见仓库根目录的 [LICENSE](LICENSE)。版权：**Copyright (c) 2026 Drhusku**。

---

## English Summary

**Auto Colonize** is an *Europa Universalis IV* mod (tested on **1.37.5**) that colonizes unclaimed land for you automatically. Enable it via a **decision**, choose a **mode** (*Subcontinent* or *Trade Node*), pick a **sorting** preference (*distance* or *development*, both approximate since EU4 has no built-in script sort), then choose a **target** from the list (16 subcontinents, or 31 trade nodes that contain colonizable land). Each in-game **year** the mod founds a colony in the chosen target; once the target is fully colonized, the list re-opens so you can pick the next target or stop.

**Installation**: place the mod content under `Documents/Paradox Interactive/Europa Universalis IV/mod/autocolonize/`, put `descriptor.mod` as `autocolonize.mod` inside the `mod/` folder, and **edit the `path` field in `autocolonize.mod` to your own machine’s actual path** (a common EU4 modding gotcha), then enable it in the launcher.

**Known limitations**: colonial range cannot be tested in script — the engine decides on each actual colonization; expelling natives is not implemented; completion-event option count is bounded by the engine limit (the trade-node list is capped at 32 options); the yearly pulse triggering each colonization is scheduled by tag order id, so its exact trigger date per country is not a fixed Jan 1 (functionality unaffected).

**License**: MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Drhusku.

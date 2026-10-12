# EU4 Auto Colonize — 安装与验证说明

## 一、本机已安装（Captain 完成）

- 源码目录：E:\\AI\\eu4_autocolonize
- 安装目录：C:\\Users\\Husky\\Documents\\Paradox Interactive\\Europa Universalis IV\\mod\\autocolonize
- 描述文件：...\\mod\\autocolonize.mod（path 已指向安装目录）
- 启用状态：已写入 dlc_load.json（同时在 Paradox 启动器播放集中勾选）
- 哈希比对：见 docs/INSTALL_HASHES.txt（9 个文件全部 MATCH）
- 静态校验：validate_paradox.py --strict = **11/11 PASS**（源与安装副本均通过）

## 二、其他玩家安装步骤

1. **复制 mod 内容**：把仓库里的 events/、common/、decisions/、localisation/、gfx/、descriptor.mod、thumbnail.png 整体复制到：

    Documents/Paradox Interactive/Europa Universalis IV/mod/autocolonize/

2. **创建描述文件**：在 mod/ 目录（与 autocolonize/ 同级）新建 autocolonize.mod，内容：

    name="Auto Colonize 自动殖民"
    version="1.0"
    tags={
        "Gameplay"
        "Missions And Decisions"
    }
    picture="thumbnail.png"
    supported_version="v1.37.*"
    path="C:/Users/<你的用户名>/Documents/Paradox Interactive/Europa Universalis IV/mod/autocolonize"

   **⚠️ 必须把 path 改成你自己机器的实际路径**（EU4 mod 通用坑），否则启动器找不到 mod。

3. **启用 mod**：打开 Paradox 启动器 → 播放集 → 勾选 Auto Colonize 自动殖民。

4. **依赖说明**：界面文本为中文，**需要安装「Chinese Language Mod for 1.37」（创意工坊 2976470733）**提供中文字体，否则中文会显示为乱码（详见 README 已知限制）。

## 三、游戏内验证清单（供实测）

| # | 验证点 | 预期 |
|---|---|---|
| 1 | 决议面板（D 键）出现「启用自动殖民」 | 可点击 |
| 2 | 点启用 | 弹出「自动殖民 — 选择模式」（两个选项 + 取消） |
| 3 | 选「按次大陆殖民」 | 弹出「自动殖民 — 选择排序」 |
| 4 | 选「由发展度从高到低」 | 弹出「自动殖民 — 选择目标」（16 个次大陆，无可殖民地的自动隐藏） |
| 5 | 选一个有殖民地的目标（如大洋洲） | 事件关闭；下一年自动在该区域建立殖民地 |
| 6 | 该区域全部殖民完毕 | 自动弹出目标列表让你续选（.3） |
| 7 | 全部目标殖民完毕 | 目标列表只剩「停止自动殖民」（文案已说明是「全部完毕或放弃」） |
| 8 | 点「关闭自动殖民」决议 | 决议消失（flag 清除），自动殖民停止 |
| 9 | 中文显示 | 全部中文正常（无 ???? 或残缺字） |

## 四、静态校验复跑命令

```bash
# 源码目录
python tools/validate_paradox.py "E:\\AI\\eu4_autocolonize" --strict

# 安装副本
python tools/validate_paradox.py "C:\\Users\\Husky\\Documents\\Paradox Interactive\\Europa Universalis IV\\mod\\autocolonize" --strict
```

预期输出：TOTAL PASS=11 FAIL=0 SKIP=0，退出码 0。

## 五、已知限制（详见 README）

1. 殖民距离无法在脚本层判定（引擎在实际殖民时裁定）
2. 驱逐少数民族未实现
3. 完成事件选项数受引擎上限约束（原版实测 33，本 mod 贸易节点 32）
4. 年度脉冲触发日期依国家 tag order id 而异
5. 界面为中文，依赖汉化 mod 提供字体（未装则乱码）
6. 「由近到远」为近似排序（优先已探索 + 引擎距离自然筛选）
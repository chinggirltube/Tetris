


# 🎮 Retro Tetris | 复古俄罗斯方块

---

## 🔖 项目简介

一款经典的 **复古风格俄罗斯方块** 游戏，采用 Python + Pygame 引擎开发。具备流畅的操作手感、优雅的用户界面以及完整的游戏功能，适合休闲娱乐与技术学习。

### ✨ 核心特色

| 特性 | 描述 |
|------|------|
| 🧱 经典玩法 | 7 种标准方块、随机抽取、消除行数计分 |
| 👻 影子辅助 | 显示当前方块落点位置，精准预判 |
| 🔊 音效系统 | 背景音乐、下落、消行、升级等独立音效 |
| ⚡ CRT视觉特效 | 模拟老式CRT显示器的扫描线效果 |
| 🎯 难度递增 | 随等级提升自动加速挑战性 |
| 🛠️ 高度可配置 | 所有参数集中在配置中心，修改便捷 |
| 💾 纯净架构 | 模块化设计，易于扩展和维护 |

---

## 🚀 快速开始

### 环境要求

- **Python**: ≥ 3.8
- **依赖库**: `pygame`
- **操作系统**: Windows / macOS / Linux

### 安装步骤

```bash
# 1. 克隆或下载本项目
git clone https://github.com/chinggirltube/Tetris.git
cd Tetris

# 2. 创建虚拟环境（可选但推荐）
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. 安装依赖
pip install pygame pyinstaller
```

### 启动游戏

```bash
# 直接运行
python main.py

# 或使用虚拟环境
python -m pygame.main  # 如有需要
```

---

## 🎹 操作说明

<table style="width:100%;">
<tr>
<th width="30%">按键</th>
<th>功能</th>
<th>备注</th>
</tr>
<tr>
<td><kbd>←</kbd> / <kbd>A</kbd></td>
<td>向左移动</td>
<td>支持长按连续移动</td>
</tr>
<tr>
<td><kbd>→</kbd> / <kbd>D</kbd></td>
<td>向右移动</td>
<td>支持长按连续移动</td>
</tr>
<tr>
<td><kbd>↓</kbd> / <kbd>S</kbd></td>
<td>向下移动（软降）</td>
<td>手动加速下落</td>
</tr>
<tr>
<td><kbd>Space</kbd> / <kbd>X</kbd> / <kbd>W</kbd></td>
<td>旋转方块</td>
<td>支持墙踢微调</td>
</tr>
<tr>
<td><kbd>↑</kbd></td>
<td>硬降落</td>
<td>瞬间掉落到底部</td>
</tr>
<tr>
<td><kbd>Esc</kbd></td>
<td>暂停/继续</td>
<td>游戏进行中有效</td>
</tr>
</table>

### 界面上的按钮操作

| 按钮名称                 | 功能描述              |
| ------------------------ | --------------------- |
| **Pause**                | 暂停当前游戏          |
| **Restart**              | 重新开始一局新游戏    |
| **Mute / Unmute**        | 开启/关闭所有声音     |
| **Ghost:On / Ghost:Off** | 开启/关闭影子方块提示 |

---

## 🗂️ 项目结构

```
Tetris/
├── main.py              # 🎮 主程序入口（含全部游戏逻辑）
├── assets/              # 📁 资源文件夹
│   ├── fonts/           # 字体文件 (.ttf)
│   └── sounds/          # 音效文件 (.mp3)
├── .gitignore           # Git忽略配置
└── README.md            # 📄 项目说明文档
```

> **注意**: 
> - 本项目的所有游戏逻辑都集成在 `main.py` 单一文件中，便于部署和移植。
> - 如需更换音效或字体，只需替换 `assets` 文件夹内的对应文件即可。

---

## ⚙️ 配置说明

游戏的所有可调参数已集中放置在 `main.py` 顶部的 **CONFIG 字典** 中，方便开发者进行自定义调整。

```python
CONFIG = {
    # --- 界面文本与字体 ---
    "title_text": "Retro Tetris",
    "font_sizes": {"large": 26, "medium": 24, "small": 16},
    
    # --- 布局与尺寸 ---
    "scale": 1.2,                  # 全局缩放比例
    "base_block_size": 30,         # 方块基础像素大小
    "sidebar_width": 220,          # 侧边栏宽度
    
    # --- 游戏难度与手感 ---
    "initial_fall_speed": 800,     # 初始下落速度(毫秒)
    "speed_increase_per_level": 70,# 每级速度增量
    "lock_delay": 500,             # 触底锁定延迟
    "move_sideways_delay": 180,    # 水平移动长按初始延迟
}
```

💡 **建议**: 修改任何参数后请重启游戏以生效。

---

## 🏆 得分规则

| 行为                      | 获得分数 (×当前等级) |
| ------------------------- | -------------------- |
| 消除 1 行                 | 100                  |
| 消除 2 行                 | 300                  |
| 消除 3 行                 | 500                  |
| 一次性消除 4 行 (Tetris!) | 800                  |

- **等级机制**: 每消除 **10 行** 上升一级，方块下落速度随之加快。
- **最高等级**: 理论上无上限，但随着速度加快游戏难度呈指数级增长。

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！如果您有以下类型的改进，非常感谢您的参与：

- 🐞 Bug 修复（例如按键响应问题、崩溃异常等）
- 🌟 新功能建议（如联机模式、排行榜统计等）
- 🎨 UI/UX 优化建议
- 📝 文档完善

---


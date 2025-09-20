# 桌面宠物

一个使用 Python + Tkinter 实现的轻量级桌面宠物，能够在屏幕上自由移动、与用户互动，并提供简单的健康提醒功能。

## 功能亮点
- 🐾 **桌面精灵**：悬浮于其他窗口之上，可任意拖动位置，自动在屏幕范围内轻盈游走。
- 😊 **心情系统**：支持心情值与亲密度，随互动动态变化，表现为不同的表情与提示语。
- 🍱 **交互动作**：双击抚摸、右键菜单喂食/午休/重置心情，宠物会做出反馈动画与对话气泡。
- ⏰ **健康提醒**：内置喝水、活动等提醒，按配置间隔弹出提示，可自行在配置中增删。
- 💾 **持久化状态**：自动在 `~/.desktop_pet/` 目录下记录心情、亲密度以及自定义配置。

## 快速开始
1. 安装依赖：本项目使用标准库 Tkinter，无需额外安装。建议 Python 3.10 及以上版本。
2. 克隆仓库并运行：

```bash
git clone https://github.com/your-name/desktop-pet.git
cd desktop-pet
python main.py
```

首次运行会在用户主目录下创建 `~/.desktop_pet/config.json` 与 `state.json`，用于保存配置与宠物状态。

## 交互说明
- **拖动**：按住左键拖动可移动宠物位置。
- **摸摸**：双击宠物会增加心情并播放弹跳动画。
- **右键菜单**：
  - `喂食`：快速提升心情。
  - `午休`：进入短暂休息状态，保持好心情。
  - `重置心情`：将心情恢复到默认值。
  - `退出`：关闭宠物并保存当前状态。

## 配置文件
默认配置位于 `desktop_pet/config.py`，在首次运行后会复制到 `~/.desktop_pet/config.json`：

```json
{
  "pet_name": "Mochi",
  "window": {"width": 220, "height": 220, "background": "#000000"},
  "movement": {"step": 5, "interval_ms": 70, "bounds_margin": 50},
  "reminders": [
    {"name": "stretch", "interval_minutes": 60, "message": "起来活动一下，放松身体~", "enabled": true},
    {"name": "hydrate", "interval_minutes": 45, "message": "喝点水补充能量！", "enabled": true}
  ]
}
```

- **窗口配置**：调整大小、背景色等。
- **移动参数**：控制在桌面上游走的速度与活动范围。
- **提醒配置**：可增删自定义提醒，字段含义：
  - `name`：内部名称；
  - `interval_minutes`：触发间隔（分钟）；
  - `message`：提醒内容，将以对话气泡形式显示；
  - `enabled`：是否启用该提醒；
  - `jitter`（可选）：增加一点随机抖动，默认 ±5 分钟。

修改配置文件后重新运行即可生效。

## 项目结构
```
desktop_pet/
├─ __init__.py          # 包导出
├─ app.py               # 应用主逻辑与窗口控制
├─ config.py            # 默认配置与状态持久化
├─ pet.py               # Tkinter 画布上的宠物绘制与动画
└─ reminders.py         # 提醒调度管理
main.py                 # 启动入口
```

## 开发说明
- 代码尽量保持无外部依赖，方便快速运行与二次开发。
- 若要扩展行为，可在 `PetView` 中加入新的动画或绑定自定义菜单项。
- 欢迎根据需要继续完善插件系统、音效、皮肤资源等高级功能。

## 许可证
MIT License（可根据实际需求调整）。

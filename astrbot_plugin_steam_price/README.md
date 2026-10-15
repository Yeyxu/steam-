# AstrBot Steam 游戏价格与折扣查询插件

专为 [AstrBot](https://github.com/Soulter/AstrBot) 设计的 Steam 游戏国区价格查询插件，支持自然语言 AI 对话唤醒以及 `/steam` 指令快捷查询。

---

## ✨ 功能特性

- 🤖 **大模型工具 (`@filter.llm_tool`)**：
  - 用户在群聊或私聊中用自然语言询问（如：“*博德之门3打折了吗？*”、“*黑神话悟空在 Steam 卖多少钱*”），AI 自动调用本工具获取真实国区数据并回答。
- ⚡ **快捷指令 (`@filter.command`)**：
  - 发送 `/steam <游戏名>` 立即返回图文排版卡片（游戏封面 + 当前价 + 原价 + 折扣率 + 平台 + 商店直链）。
- 🖼️ **富媒体图文混排**：
  - 使用 AstrBot 官方 `Comp.Image` 消息链原生发送游戏胶囊海报图。
- 📦 **开箱即用，零额外依赖**：
  - 基于 Python 原生标准库与 `asyncio.to_thread` 异步调度，无需额外部署或 `pip install` 繁重依赖。
- 🧠 **自带 Agent Skill 扩展**：
  - 内部集成了 `skills/steam-game-price/SKILL.md`，AstrBot v4.13+ 自动挂载识别。

---

## 🚀 安装部署方法

### 方式一：直接复制文件夹（推荐）

1. 将本文件夹 `astrbot_plugin_steam_price` 复制到您的 AstrBot 项目根目录下的 `data/plugins/` 目录中：
   ```text
   AstrBot/
   └── data/
       └── plugins/
           └── astrbot_plugin_steam_price/
               ├── metadata.yaml
               ├── main.py
               ├── README.md
               └── skills/
   ```
2. 打开 AstrBot WebUI 面板，进入 **「插件」** 页面，找到 **Steam游戏价格查询** 插件并点击 **「重载/启用」** 即可。

---

## 🎮 使用示例

### 1. 指令方式
- `/steam 赛博朋克2077`
- `/steam 失落城堡2`
- `/steam Dota 2`

### 2. 自然语言（AI Agent 自动识别）
- *“帮我看一下黑神话悟空在国区卖多少钱”*
- *“荒野大镖客2现在有没有打折？折扣是多少”*
- *“CS2是免费游戏吗”*

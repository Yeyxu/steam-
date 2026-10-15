---
name: steam-game-price
description: >-
  Use this skill when the user asks to query Steam game prices, search for Steam games,
  check discounts or historical sales for Steam games in the China region (CNY), or retrieve Steam App IDs.
---

# AstrBot Steam 游戏国区价格查询技能手册

本技能指导 AstrBot Agent 在用户提出 Steam 游戏查询需求时，如何通过内置的 `query_steam_price` 工具或接口获取国区最新价格与折扣信息。

---

## 🎯 触发时机与意图识别

当用户在聊天中提及以下意图时激活本技能：
- 询问 Steam 某游戏当前价格、是否打折、史低或促销状态（如“艾尔登法环多少钱”、“黑神话打折了吗”）。
- 搜索 Steam 游戏并获取其商店链接或 AppID。
- 询问免费游戏状态（如“CS2是免费的吗”）。

---

## 🛠️ 调用与处理指南

1. **调用大模型工具**：
   - 触发内部工具 `query_steam_price(game_name="...")`。
2. **提取参数**：
   - 从用户的自然语言中提取最核心的游戏名称（例如“帮我看看赛博朋克2077” $\rightarrow$ `赛博朋克2077`）。
3. **输出排版要求**：
   - 清晰汇报游戏全称、国区当前价格（原价/折扣价/优惠百分比）。
   - 若是免费游戏，明确告知用户为“免费游玩 (Free to Play)”。
   - 附带 Steam 商店直达链接 `https://store.steampowered.com/app/{id}/`。

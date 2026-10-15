import asyncio
import json
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
import astrbot.api.message_components as Comp
from astrbot.api.star import Context, Star


def _sync_search_steam(term: str, lang: str = "schinese", cc: str = "cn", timeout: int = 10) -> Dict[str, Any]:
    """同步网络请求 Steam 商店搜索接口"""
    encoded_term = urllib.parse.quote(term)
    url = f"https://store.steampowered.com/api/storesearch/?term={encoded_term}&l={lang}&cc={cc}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = resp.read().decode("utf-8", errors="replace")
            return json.loads(content)
    except Exception as e:
        logger.error(f"[SteamPrice] 请求 Steam API 失败: {e}")
        return {"error": str(e), "total": 0, "items": []}


def parse_game_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """解析并标准化单条 Steam 游戏数据"""
    app_id = item.get("id")
    name = item.get("name", "未知游戏")
    tiny_image = item.get("tiny_image", "")
    metascore = item.get("metascore") or "暂无评分"
    platforms = item.get("platforms", {})

    platform_list = []
    if platforms.get("windows"): platform_list.append("Win")
    if platforms.get("mac"): platform_list.append("Mac")
    if platforms.get("linux"): platform_list.append("Linux/SteamOS")
    platform_str = "/".join(platform_list) if platform_list else "未标明"

    store_url = f"https://store.steampowered.com/app/{app_id}/" if app_id else ""
    price_info = item.get("price")

    # 免费游戏 (Free to Play) 或未定价
    if not price_info:
        return {
            "id": app_id,
            "name": name,
            "is_free": True,
            "currency": "CNY",
            "initial_price": 0.0,
            "final_price": 0.0,
            "discount_percent": 0,
            "price_text": "免费游玩 (Free to Play)",
            "platforms": platform_str,
            "metascore": metascore,
            "tiny_image": tiny_image,
            "store_url": store_url,
        }

    currency = price_info.get("currency", "CNY")
    # Steam 价格单位为“分”，除以 100 得到元
    initial_price = price_info.get("initial", 0) / 100.0
    final_price = price_info.get("final", 0) / 100.0

    if initial_price > 0 and final_price < initial_price:
        discount_percent = int(round((1 - (final_price / initial_price)) * 100))
        price_text = f"¥{final_price:.2f} (原价 ¥{initial_price:.2f}，优惠 -{discount_percent}%)"
    elif final_price == 0:
        discount_percent = 0
        price_text = "免费游玩 (Free to Play)"
    else:
        discount_percent = 0
        price_text = f"¥{final_price:.2f}"

    return {
        "id": app_id,
        "name": name,
        "is_free": final_price == 0,
        "currency": currency,
        "initial_price": initial_price,
        "final_price": final_price,
        "discount_percent": discount_percent,
        "price_text": price_text,
        "platforms": platform_str,
        "metascore": metascore,
        "tiny_image": tiny_image,
        "store_url": store_url,
    }


class SteamPricePlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.context = context

    async def search_game(self, term: str) -> List[Dict[str, Any]]:
        """异步调用搜索并解析结果"""
        raw_data = await asyncio.to_thread(_sync_search_steam, term)
        items = raw_data.get("items", [])
        return [parse_game_item(item) for item in items]

    # ==========================
    # 1. 指令触发：/steam <游戏名>
    # ==========================
    @filter.command("steam")
    async def steam_command(self, event: AstrMessageEvent):
        """查询 Steam 游戏国区价格与打折信息。用法: /steam <游戏名称>"""
        raw_msg = event.message_str.strip()
        # 提取指令后的参数部分
        keyword = raw_msg
        if keyword.startswith("/steam") or keyword.startswith("steam"):
            parts = keyword.split(maxsplit=1)
            keyword = parts[1].strip() if len(parts) > 1 else ""

        if not keyword:
            yield event.plain_result("💡 请输入要查询的 Steam 游戏名称，例如：/steam 黑神话悟空")
            return

        games = await self.search_game(keyword)
        if not games:
            yield event.plain_result(f"未找到与「{keyword}」相关的 Steam 游戏，请检查游戏名称或输入英文原名重试。")
            return

        # 默认取匹配度最高的第一款主游戏
        top_game = games[0]

        # 构造图文混排消息链
        chain = []
        if top_game.get("tiny_image"):
            try:
                chain.append(Comp.Image.fromURL(top_game["tiny_image"]))
            except Exception as e:
                logger.warning(f"[SteamPrice] 加载封面图失败: {e}")

        text_content = (
            f"🎮 【{top_game['name']}】\n"
            f"💰 当前价格: {top_game['price_text']}\n"
            f"💻 支持平台: {top_game['platforms']}\n"
            f"⭐ 媒体评分: {top_game['metascore']}\n"
            f"🆔 AppID: {top_game['id']}\n"
            f"🔗 商店链接: {top_game['store_url']}"
        )

        # 如果搜索出多款，顺带附上其他候选名字
        if len(games) > 1:
            others = [f"{g['name']} ({g['price_text']})" for g in games[1:4]]
            text_content += f"\n\n🔍 其他可能相关: " + " | ".join(others)

        chain.append(Comp.Plain(text_content))
        yield event.chain_result(chain)

    # ==========================================
    # 2. LLM 工具触发 (@filter.llm_tool)
    # 当用户在普通对话中询问“某游戏多少钱/打折吗”，AI 自动调用
    # ==========================================
    @filter.llm_tool(name="query_steam_price")
    async def query_steam_price_tool(self, event: AstrMessageEvent, game_name: str) -> str:
        """查询 Steam 游戏在国区（中国区 CNY）的当前售价、原价、促销折扣、封面图与商店链接。

        Args:
            game_name(string): 需要查询的 Steam 游戏名称或关键词，例如 "黑神话悟空" 或 "赛博朋克2077"。
        """
        if not game_name or not game_name.strip():
            return "请提供有效的游戏名称。"

        games = await self.search_game(game_name.strip())
        if not games:
            return f"在 Steam 国区未检索到与「{game_name}」相关的游戏。可能是拼写有误或国区未上架。"

        top_game = games[0]

        # 如果当前会话上下文支持主动推送图片，可顺带推送封面胶囊图
        try:
            if top_game.get("tiny_image") and hasattr(event, "unified_msg_origin"):
                chain = [
                    Comp.Image.fromURL(top_game["tiny_image"]),
                    Comp.Plain(f"为您找到游戏「{top_game['name']}」的 Steam 信息：")
                ]
                await self.context.send_message(event.unified_msg_origin, chain)
        except Exception as e:
            logger.debug(f"[SteamPrice] llm_tool 尝试预推送封面图跳过: {e}")

        # 返回结构化文本给大模型进行汇总组织回答
        result_desc = (
            f"游戏名称: {top_game['name']}\n"
            f"AppID: {top_game['id']}\n"
            f"是否免费: {'是' if top_game['is_free'] else '否'}\n"
            f"当前价格: {top_game['price_text']}\n"
            f"原价: ¥{top_game['initial_price']:.2f}\n"
            f"现价: ¥{top_game['final_price']:.2f}\n"
            f"折扣百分比: -{top_game['discount_percent']}%\n"
            f"支持平台: {top_game['platforms']}\n"
            f"Metacritic 评分: {top_game['metascore']}\n"
            f"商店链接: {top_game['store_url']}\n"
            f"封面图URL: {top_game['tiny_image']}"
        )

        if len(games) > 1:
            more_candidates = [f"{g['name']}(AppID: {g['id']}, 价格: {g['price_text']})" for g in games[1:4]]
            result_desc += f"\n其他相关搜索结果: " + "; ".join(more_candidates)

        return result_desc

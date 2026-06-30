import logging

import discord
from discord import app_commands
from discord.ext import commands

from discord_ai_secretary.services.llm_client import LLMError
from discord_ai_secretary.services.message_fetcher import MessageFetchError, fetch_recent_messages


logger = logging.getLogger(__name__)


class SummaryCog(commands.Cog):
    def __init__(self, bot: commands.Bot, llm_client) -> None:
        self.bot = bot
        self.llm_client = llm_client

    @app_commands.command(name="summarize", description="現在のチャンネルの会話をAIで要約します。")
    @app_commands.describe(count="取得する直近メッセージ数（10から200）")
    async def summarize(self, interaction: discord.Interaction, count: app_commands.Range[int, 10, 200] = 50) -> None:
        await interaction.response.defer(thinking=True)

        try:
            messages = await fetch_recent_messages(interaction.channel, self.bot.user, count)
            if len(messages) < 2:
                await interaction.followup.send("要約できるメッセージが少なすぎます。")
                return
            summary = await self.llm_client.summarize(messages)
            await _send_text(interaction, summary)
        except MessageFetchError as exc:
            logger.exception("Failed to fetch messages for summarize")
            await interaction.followup.send(str(exc))
        except LLMError:
            logger.exception("Gemini summarize failed")
            await interaction.followup.send("AI要約に失敗しました。時間をおいて再試行してください。")


async def _send_text(interaction: discord.Interaction, text: str) -> None:
    max_length = 1900
    if len(text) <= max_length:
        await interaction.followup.send(text)
        return

    chunks = [text[i : i + max_length] for i in range(0, len(text), max_length)]
    for chunk in chunks[:3]:
        await interaction.followup.send(chunk)

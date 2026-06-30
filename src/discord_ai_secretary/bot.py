import asyncio
import logging

import discord
from discord.ext import commands

from discord_ai_secretary.cogs.summarize import SummaryCog
from discord_ai_secretary.cogs.tasks import TasksCog
from discord_ai_secretary.config import ConfigError, load_settings
from discord_ai_secretary.database import TaskDatabase
from discord_ai_secretary.services.llm_client import GeminiClient


logger = logging.getLogger(__name__)


class SecretaryBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self) -> None:
        settings = load_settings()
        database = TaskDatabase(settings.database_path)
        database.initialize()
        llm_client = GeminiClient(settings.gemini_api_key)

        await self.add_cog(SummaryCog(self, llm_client))
        await self.add_cog(TasksCog(self, llm_client, database))
        self.tree.add_command(ping)

        synced = await self.tree.sync()
        logger.info("Synced %s slash commands", len(synced))


@discord.app_commands.command(name="ping", description="Botの稼働確認をします。")
async def ping(interaction: discord.Interaction) -> None:
    await interaction.response.send_message("Pong!")


async def run_bot() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        settings = load_settings()
        bot = SecretaryBot()
        async with bot:
            await bot.start(settings.discord_bot_token)
    except ConfigError as exc:
        logger.error("%s", exc)
        raise SystemExit(1) from exc


def main() -> None:
    asyncio.run(run_bot())

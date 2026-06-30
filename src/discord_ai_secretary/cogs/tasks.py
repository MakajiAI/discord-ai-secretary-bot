import logging

import discord
from discord import app_commands
from discord.ext import commands

from discord_ai_secretary.database import DatabaseError, TaskDatabase
from discord_ai_secretary.services.llm_client import LLMError
from discord_ai_secretary.services.message_fetcher import MessageFetchError, fetch_recent_messages
from discord_ai_secretary.services.task_parser import TaskParseError


logger = logging.getLogger(__name__)


class TasksCog(commands.GroupCog, name="tasks"):
    def __init__(self, bot: commands.Bot, llm_client, database: TaskDatabase) -> None:
        self.bot = bot
        self.llm_client = llm_client
        self.database = database

    @app_commands.command(name="extract", description="現在のチャンネルの会話からタスクを抽出します。")
    @app_commands.describe(count="取得する直近メッセージ数（10から200）")
    async def extract(self, interaction: discord.Interaction, count: app_commands.Range[int, 10, 200] = 100) -> None:
        await interaction.response.defer(thinking=True)

        if interaction.guild_id is None:
            await interaction.followup.send("このコマンドはサーバー内で実行してください。")
            return

        try:
            messages = await fetch_recent_messages(interaction.channel, self.bot.user, count)
            if len(messages) < 2:
                await interaction.followup.send("タスク抽出に使えるメッセージが少なすぎます。")
                return

            tasks = await self.llm_client.extract_tasks(messages)
            if not tasks:
                await interaction.followup.send("タスクは見つかりませんでした。")
                return

            ids = self.database.add_tasks(str(interaction.guild_id), str(interaction.channel_id), tasks)
            await interaction.followup.send(_format_saved_tasks(ids, tasks))
        except MessageFetchError as exc:
            logger.exception("Failed to fetch messages for task extraction")
            await interaction.followup.send(str(exc))
        except TaskParseError:
            logger.exception("Failed to parse task JSON")
            await interaction.followup.send("AIのタスク抽出結果を読み取れませんでした。もう一度お試しください。")
        except LLMError:
            logger.exception("Gemini task extraction failed")
            await interaction.followup.send("AIによるタスク抽出に失敗しました。時間をおいて再試行してください。")
        except DatabaseError as exc:
            logger.exception("Failed to save tasks")
            await interaction.followup.send(str(exc))

    @app_commands.command(name="list", description="未完了タスクを一覧表示します。")
    async def list_tasks(self, interaction: discord.Interaction) -> None:
        if interaction.guild_id is None:
            await interaction.response.send_message("このコマンドはサーバー内で実行してください。", ephemeral=True)
            return

        try:
            tasks = self.database.list_open_tasks(str(interaction.guild_id), limit=20)
            if not tasks:
                await interaction.response.send_message("未完了タスクはありません。")
                return
            await interaction.response.send_message(_format_open_tasks(tasks))
        except DatabaseError as exc:
            logger.exception("Failed to list tasks")
            await interaction.response.send_message(str(exc), ephemeral=True)

    @app_commands.command(name="done", description="指定したIDのタスクを完了にします。")
    @app_commands.describe(task_id="完了にするタスクID")
    async def done(self, interaction: discord.Interaction, task_id: int) -> None:
        if interaction.guild_id is None:
            await interaction.response.send_message("このコマンドはサーバー内で実行してください。", ephemeral=True)
            return

        try:
            updated = self.database.mark_done(str(interaction.guild_id), task_id)
            if not updated:
                await interaction.response.send_message("指定された未完了タスクが見つかりません。", ephemeral=True)
                return
            await interaction.response.send_message(f"✅ Task #{task_id} を完了にしました。")
        except DatabaseError as exc:
            logger.exception("Failed to mark task done")
            await interaction.response.send_message(str(exc), ephemeral=True)


def _format_saved_tasks(ids: list[int], tasks: list[dict]) -> str:
    lines = ["✅ タスクを保存しました。", ""]
    for task_id, task in zip(ids, tasks, strict=False):
        assignee = task.get("assignee") or "未設定"
        due_date = task.get("due_date") or "未設定"
        lines.append(f"{task_id}. {task['title']}")
        lines.append(f"   Assignee: {assignee}")
        lines.append(f"   Due: {due_date}")
        lines.append("")
    return "\n".join(lines).strip()


def _format_open_tasks(tasks) -> str:
    lines = ["📝 Open Tasks", ""]
    for task in tasks:
        assignee = task.assignee or "未設定"
        due_date = task.due_date or "未設定"
        lines.append(f"{task.id}. {task.title}")
        lines.append(f"   Assignee: {assignee}")
        lines.append(f"   Due: {due_date}")
        lines.append("")
    return "\n".join(lines).strip()

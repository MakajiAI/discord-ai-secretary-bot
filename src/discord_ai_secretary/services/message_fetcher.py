from __future__ import annotations

import discord


class MessageFetchError(RuntimeError):
    """Raised when Discord messages cannot be fetched."""


async def fetch_recent_messages(channel, bot_user: discord.ClientUser | None, count: int) -> list[dict[str, str]]:
    if channel is None or not hasattr(channel, "history"):
        raise MessageFetchError("このチャンネルではメッセージを取得できません。")

    try:
        raw_messages = [message async for message in channel.history(limit=count)]
    except discord.Forbidden as exc:
        raise MessageFetchError("メッセージ取得権限がありません。") from exc
    except discord.HTTPException as exc:
        raise MessageFetchError("Discordメッセージの取得に失敗しました。") from exc

    messages = []
    for message in reversed(raw_messages):
        if bot_user is not None and message.author.id == bot_user.id:
            continue
        content = (message.content or "").strip()
        if not content:
            continue
        messages.append(
            {
                "author": message.author.display_name,
                "content": content,
                "created_at": message.created_at.isoformat(),
            }
        )
    return messages

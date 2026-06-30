from __future__ import annotations

import asyncio
import logging

import google.generativeai as genai

from discord_ai_secretary.services.task_parser import parse_tasks_json


logger = logging.getLogger(__name__)


class LLMError(RuntimeError):
    """Raised when Gemini fails to return a usable response."""


class GeminiClient:
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash") -> None:
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    async def summarize(self, messages: list[dict[str, str]]) -> str:
        prompt = (
            "あなたはDiscordサーバーの秘書です。以下の会話を日本語で簡潔に要約してください。\n"
            "必ず次の形式で返してください。\n\n"
            "📌 Summary\n"
            "会話の要約\n\n"
            "✅ Decisions\n"
            "決定事項。なければ「なし」。\n\n"
            "📝 Task Candidates\n"
            "タスク候補。なければ「なし」。\n\n"
            "会話:\n"
            f"{_format_messages(messages)}"
        )
        return await self._generate_text(prompt)

    async def extract_tasks(self, messages: list[dict[str, str]]) -> list[dict[str, str | None]]:
        prompt = (
            "あなたはDiscordサーバーの秘書です。以下の会話から実行すべきタスクだけを抽出してください。\n"
            "返答は説明文なしのJSONのみです。Markdownコードブロックも不要です。\n"
            "形式:\n"
            '{"tasks":[{"title":"READMEを作成する","assignee":"まかじ","due_date":null}]}\n'
            "assigneeやdue_dateが不明な場合はnullにしてください。タスクがない場合は {\"tasks\":[]} を返してください。\n\n"
            "会話:\n"
            f"{_format_messages(messages)}"
        )
        raw_text = await self._generate_text(prompt)
        return parse_tasks_json(raw_text)

    async def _generate_text(self, prompt: str) -> str:
        try:
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            text = getattr(response, "text", None)
            if not text:
                raise LLMError("Gemini returned an empty response")
            return text.strip()
        except LLMError:
            raise
        except Exception as exc:
            logger.exception("Gemini API call failed")
            raise LLMError("Gemini API call failed") from exc


def _format_messages(messages: list[dict[str, str]]) -> str:
    lines = []
    for message in messages:
        lines.append(f"[{message['created_at']}] {message['author']}: {message['content']}")
    return "\n".join(lines)

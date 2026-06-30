from dataclasses import dataclass
import os

from dotenv import load_dotenv


class ConfigError(RuntimeError):
    """Raised when required environment variables are missing."""


@dataclass(frozen=True)
class Settings:
    discord_bot_token: str
    gemini_api_key: str
    database_path: str = "data/bot.db"


def load_settings() -> Settings:
    load_dotenv()

    discord_bot_token = os.getenv("DISCORD_BOT_TOKEN")
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    database_path = os.getenv("DATABASE_PATH", "data/bot.db")

    missing = []
    if not discord_bot_token:
        missing.append("DISCORD_BOT_TOKEN")
    if not gemini_api_key:
        missing.append("GEMINI_API_KEY")

    if missing:
        raise ConfigError(f"Missing required environment variables: {', '.join(missing)}")

    return Settings(
        discord_bot_token=discord_bot_token,
        gemini_api_key=gemini_api_key,
        database_path=database_path,
    )

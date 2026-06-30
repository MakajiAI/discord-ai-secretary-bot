import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from discord_ai_secretary.bot import main  # noqa: E402


if __name__ == "__main__":
    main()

import json
import os
import random
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

PREFIX_WORD = "Кузнецов"

JSON_FILE = "sergay.json"


def load_phrases(file_path: str) -> list[str]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    phrases = []

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                for value in item.values():
                    if isinstance(value, str) and value.strip():
                        phrases.append(value.strip())
            elif isinstance(item, str) and item.strip():
                phrases.append(item.strip())

    if not phrases:
        raise ValueError("В JSON не найдено ни одной строки с фразой")

    return phrases


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        phrases = load_phrases(JSON_FILE)
        phrase = random.choice(phrases)
        text = f"{PREFIX_WORD} {phrase}".strip()
    except Exception as e:
        text = f"Ошибка: {e}"

    await update.message.reply_text(text)


def main() -> None:
    load_dotenv()
    token = os.getenv("TG_TOKEN")

    if not token:
        raise ValueError("Не найден TG_TOKEN в .env")

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()


if __name__ == "__main__":
    main()

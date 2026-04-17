import json
import os
import random
import subprocess
import urllib.request
import requests
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

PREFIX_WORD = "серГЕЙ"
JSON_FILE = "sergay.json"
SERVICE_NAME = "sergay-bot"

# Токен для связи с сайтом (тот, что мы прописывали в api.php)
SITE_API_TOKEN = "super_secret_bot_token_123"

MESSAGE_100 = "Это сотое оскарбление для серГЕЯ пидоровича, человек каторый это добавил может идти нахуй, а серГЕЙ сын шлюхи"

WAITING_NEW_PHRASE = 1
P_TITLE = 2
P_PHOTOS = 3


def load_phrases(file_path: str) -> list[str]:
    path = Path(file_path)

    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    phrases = []

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                item_id = item.get("id")
                if isinstance(item_id, int):
                    value = item.get(str(item_id))
                    if isinstance(value, str) and value.strip():
                        phrases.append(value.strip())
                else:
                    for value in item.values():
                        if isinstance(value, str) and value.strip():
                            phrases.append(value.strip())
            elif isinstance(item, str) and item.strip():
                phrases.append(item.strip())

    return phrases


def load_raw_data(file_path: str) -> list:
    path = Path(file_path)

    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("JSON должен содержать список")

    return data


def save_new_phrase(file_path: str, phrase: str) -> None:
    phrase = phrase.strip()
    if not phrase:
        raise ValueError("Пустую фразу добавлять нельзя")

    data = load_raw_data(file_path)

    existing_phrases = set()
    max_id = 0

    for item in data:
        if isinstance(item, dict):
            item_id = item.get("id")
            if isinstance(item_id, int):
                max_id = max(max_id, item_id)
                value = item.get(str(item_id))
                if isinstance(value, str):
                    existing_phrases.add(value.strip())

    if phrase in existing_phrases:
        raise ValueError("Такая фраза уже есть в базе")

    new_id = max_id + 1
    data.append({
        "id": new_id,
        str(new_id): phrase
    })

    path = Path(file_path)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def restart_service() -> None:
    subprocess.Popen(
        ["systemctl", "restart", SERVICE_NAME],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def run_gitup() -> tuple[bool, str]:
    result = subprocess.run(
        ["bash", "gitup.sh"],
        capture_output=True,
        text=True,
    )

    output = (result.stdout or "").strip()
    error = (result.stderr or "").strip()

    if result.returncode == 0:
        return True, output or "gitup выполнен"
    return False, error or output or "Ошибка выполнения gitup"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Вот список команд:\n\n"
        "Получить фразу — /phrase\n"
        "Добавить фразу — /new\n"
        "Добавить картинки на сайт — /new_p\n"
    )
    await update.message.reply_text(text)


async def phrase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        phrases = load_phrases(JSON_FILE)
        if not phrases:
            text = "Фразы пока не добавлены"
        else:
            phrase_text = random.choice(phrases)
            text = f"{PREFIX_WORD} {phrase_text}".strip()
    except Exception as e:
        text = f"Ошибка: {e}"

    # Шанс 30% прикрепить картинку
    if random.random() < 0.3 and not text.startswith("Ошибка"):
        try:
            req = urllib.request.Request("https://www.vlv-s.site/api.php?action=random")
            with urllib.request.urlopen(req, timeout=5) as response:
                api_data = json.loads(response.read().decode('utf-8'))
                img_url = api_data.get("url")

            if img_url:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=img_url,
                    caption=text
                )
                return
        except Exception as e:
            print(f"Ошибка загрузки фото из API: {e}")

    await update.message.reply_text(text)


async def new_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите фразу:")
    return WAITING_NEW_PHRASE


async def new_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    phrase_text = (update.message.text or "").strip()

    if not phrase_text:
        await update.message.reply_text("Фраза пустая. Введите фразу:")
        return WAITING_NEW_PHRASE

    try:
        save_new_phrase(JSON_FILE, phrase_text)
        await update.message.reply_text(f"Добавленно {PREFIX_WORD} {phrase_text}")
        
        if len(load_phrases(JSON_FILE)) == 100 and MESSAGE_100.strip():
            await update.message.reply_text(MESSAGE_100)
            
        restart_service()
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

    return ConversationHandler.END


async def new_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Отменено")
    return ConversationHandler.END


# --- ЛОГИКА ДЛЯ /new_p (Загрузка картинок) ---
async def new_p_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['new_p_photos'] = []
    await update.message.reply_text("Введите заголовок для новых картинок (он применится ко всем загружаемым сейчас фото):")
    return P_TITLE

async def new_p_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['new_p_title'] = update.message.text.strip()
    await update.message.reply_text(
        "Принято! Теперь отправляй мне картинки.\n"
        "Можешь отправить одну или выделить сразу несколько в галерее.\n\n"
        "Когда все нужные картинки загрузятся, отправь команду /done"
    )
    return P_PHOTOS

async def new_p_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.photo:
        # Сохраняем ID самого большого размера картинки
        photo_id = update.message.photo[-1].file_id
        context.user_data['new_p_photos'].append(photo_id)
    return P_PHOTOS

async def new_p_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    photos = context.user_data.get('new_p_photos', [])
    title = context.user_data.get('new_p_title', 'Новое фото')

    if not photos:
        await update.message.reply_text("Ты не отправил ни одной картинки. Операция отменена.")
        return ConversationHandler.END

    await update.message.reply_text(f"⏳ Скачиваю и отправляю {len(photos)} фото на сервер. Это может занять пару минут...")

    try:
        files_payload = []
        for i, pid in enumerate(photos):
            new_file = await context.bot.get_file(pid)
            p_bytes = await new_file.download_as_bytearray()
            # Формируем пакет файлов так же, как отправляет браузер (массив photos[])
            files_payload.append(('photos[]', (f'img_tg_{i}.jpg', p_bytes, 'image/jpeg')))

        data_payload = {
            'title': title,
            'description': '',
            'api_token': SITE_API_TOKEN
        }

        resp = requests.post("https://www.vlv-s.site/api.php?action=upload", files=files_payload, data=data_payload)
        resp_json = resp.json()

        if resp_json.get('success'):
            await update.message.reply_text("✅ Успех! Картинки добавлены в галерею на сайт.")
        else:
            await update.message.reply_text(f"❌ Сайт вернул ошибку: {resp_json}")

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка соединения или загрузки: {e}")

    # Очищаем данные
    context.user_data.clear()
    return ConversationHandler.END


async def gitup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Запускаю gitup...")

    ok, output = run_gitup()

    if len(output) > 3500:
        output = output[:3500] + "\n\n...вывод обрезан"

    if ok:
        await update.message.reply_text(f"gitup выполнен\n\n{output}")
    else:
        await update.message.reply_text(f"Ошибка gitup\n\n{output}")


def main() -> None:
    load_dotenv()
    token = os.getenv("TG_TOKEN")

    if not token:
        raise ValueError("Не найден TG_TOKEN в .env")

    app = ApplicationBuilder().token(token).build()

    new_handler = ConversationHandler(
        entry_points=[CommandHandler("new", new_start)],
        states={
            WAITING_NEW_PHRASE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, new_save)
            ],
        },
        fallbacks=[CommandHandler("cancel", new_cancel)],
    )

    new_p_handler = ConversationHandler(
        entry_points=[CommandHandler("new_p", new_p_start)],
        states={
            P_TITLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, new_p_title)
            ],
            P_PHOTOS: [
                MessageHandler(filters.PHOTO, new_p_photo),
                CommandHandler("done", new_p_done)
            ]
        },
        fallbacks=[CommandHandler("cancel", new_cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("phrase", phrase))
    app.add_handler(CommandHandler("gitup", gitup))
    app.add_handler(new_handler)
    app.add_handler(new_p_handler)

    app.run_polling()


if __name__ == "__main__":
    main()

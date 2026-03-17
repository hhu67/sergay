import json
from pathlib import Path

JSON_FILE = "sergay.json"


def add_phrase(text: str):
    path = Path(JSON_FILE)

    if not path.exists():
        print("Файл sergay.json не найден")
        return

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("JSON должен быть списком")
        return

    last_id = max(item["id"] for item in data)
    new_id = last_id + 1

    new_item = {
        "id": new_id,
        str(new_id): text
    }

    data.append(new_item)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Добавлено: {new_item}")


if __name__ == "__main__":
    phrase = input("Введите новую фразу: ").strip()

    if phrase:
        add_phrase(phrase)
    else:
        print("Фраза пустая")

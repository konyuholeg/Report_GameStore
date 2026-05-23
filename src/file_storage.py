import json
import os

STORAGE_DIR = os.path.join(os.path.dirname(__file__), "storage")
os.makedirs(STORAGE_DIR, exist_ok=True)

FILES = {
    "games":           os.path.join(STORAGE_DIR, "games.json"),
    "categories":      os.path.join(STORAGE_DIR, "categories.json"),
    "orders":          os.path.join(STORAGE_DIR, "orders.json"),
    "customers":       os.path.join(STORAGE_DIR, "customers.json"),
    "stock_movements": os.path.join(STORAGE_DIR, "stock_movements.json"),
    "deliveries":      os.path.join(STORAGE_DIR, "deliveries.json"),
}


def read(collection: str) -> list:
    path = FILES[collection]
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write(collection: str, data: list) -> None:
    with open(FILES[collection], "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def next_id(collection: str) -> int:
    data = read(collection)
    if not data:
        return 1
    return max(item["id"] for item in data) + 1
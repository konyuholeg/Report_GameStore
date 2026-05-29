import json
import os

FILES = {
    "games": "src/storage/games.json",
    "categories": "src/storage/categories.json",
    "orders": "src/storage/orders.json",
    "customers": "src/storage/customers.json",
    "stock_movements": "src/storage/stock_movements.json",
    "deliveries": "src/storage/deliveries.json",
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
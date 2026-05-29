from models.game import Game, Category
from file_storage import read, write, next_id


class GameController:

    def get_all_games(self, category_id=None):
        data = read("games")
        if category_id:
            data = [g for g in data if g["category_id"] == category_id]
        return [self.dict_to_game(g) for g in data]

    def get_all_categories(self):
        return [Category(**c) for c in read("categories")]

    def find_by_id(self, game_id):
        for g in read("games"):
            if g["id"] == game_id:
                return self.dict_to_game(g)
        return None

    def search(self, query):
        q = query.lower()
        return [self.dict_to_game(g) for g in read("games")
                if q in g["title"].lower() or q in g["developer"].lower()]

    def update_stock(self, game_id, quantity_delta):
        data = read("games")
        for g in data:
            if g["id"] == game_id:
                g["stock_qty"] = g.get("stock_qty", 0) + quantity_delta
                break
        write("games", data)

    def add_game(self, title, developer, category_id, price,
                 stock_qty, description, image_url):
        data = read("games")
        new_game = {
            "id": next_id("games"),
            "title": title,
            "developer": developer,
            "category_id": int(category_id),
            "price": float(price),
            "stock_qty": int(stock_qty),
            "description": description,
            "image_url": image_url,
        }
        data.append(new_game)
        write("games", data)
        return self.dict_to_game(new_game)

    def dict_to_game(self, d):
        cats = {c.id: c for c in self.get_all_categories()}
        cat = cats.get(d["category_id"], Category(id=0, name="Без категорії"))
        return Game(
            id=d["id"], title=d["title"], developer=d["developer"],
            category=cat, price=d["price"], stock_qty=d.get("stock_qty", 0),
            description=d.get("description", ""),
            image_url=d.get("image_url", ""),
            release_date=d.get("release_date", ""),
        )


GameRepository = GameController
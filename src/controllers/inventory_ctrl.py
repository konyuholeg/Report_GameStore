from datetime import datetime
from models.inventory import Stock
from controllers.game_ctrl import GameController
from file_storage import read, write, next_id


class InventoryController:
    def __init__(self):
        self.game_ctrl = GameController()

    def get_all_stock(self):
        return [
            Stock(game_id=g.id, game_title=g.title, quantity=g.stock_qty)
            for g in self.game_ctrl.get_all_games()
        ]

    def add_stock(self, game_id, quantity, reason=""):
        self.game_ctrl.update_stock(game_id, quantity)
        data = read("stock_movements")
        data.append({
            "id": next_id("stock_movements"),
            "game_id": game_id,
            "movement_type": "in",
            "quantity": quantity,
            "reason": reason,
            "created_at": str(datetime.now()),
        })
        write("stock_movements", data)
        return True

    def get_low_stock(self, threshold=5):
        return [s for s in self.get_all_stock() if s.quantity <= threshold]
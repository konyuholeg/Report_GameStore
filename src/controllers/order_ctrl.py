from datetime import datetime
from models.order import Order, OrderItem
from controllers.game_ctrl import GameController
from file_storage import read, write, next_id


class OrderController:
    def __init__(self):
        self.game_ctrl = GameController()

    def create_order(self, customer_id, items, address):
        order_items = []
        for item in items:
            game = self.game_ctrl.find_by_id(item["game_id"])
            if not game:
                raise ValueError("Гра не знайдена")
            if game.stock_qty < item["quantity"]:
                raise ValueError(f"Недостатньо запасів для '{game.title}'")
            order_items.append(
                OrderItem(game.id, game.title, item["quantity"], game.price)
            )
        order = Order(id=0, customer_id=customer_id, items=order_items,
                      delivery_address=address)
        data = read("orders")
        order.id = next_id("orders")
        order.created_at = datetime.now()
        data.append(self._order_to_dict(order))
        write("orders", data)
        return order

    def _order_to_dict(self, order):
        return {
            "id": order.id,
            "customer_id": order.customer_id,
            "status": order.status,
            "total_amount": order.total_amount(),
            "delivery_address": order.delivery_address,
            "notes": order.notes,
            "created_at": str(order.created_at),
            "items": [
                {
                    "game_id": item.game_id,
                    "game_title": item.game_title,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                }
                for item in order.items
            ],
        }
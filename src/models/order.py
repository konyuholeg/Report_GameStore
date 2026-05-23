from datetime import datetime


class OrderStatus:
    PENDING   = "pending"
    CONFIRMED = "confirmed"
    SHIPPED   = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItem:
    def __init__(self, game_id, game_title, quantity, unit_price):
        self.game_id = game_id
        self.game_title = game_title
        self.quantity = quantity
        self.unit_price = unit_price

    def total(self):
        return self.quantity * self.unit_price

    def __repr__(self):
        return f"OrderItem(game_id={self.game_id}, qty={self.quantity})"


class Order:
    def __init__(self, id, customer_id, items, status=None,
                 created_at=None, delivery_address="", notes=""):
        self.id = id
        self.customer_id = customer_id
        self.items = items
        self.status = status if status is not None else OrderStatus.PENDING
        self.created_at = created_at if created_at is not None else datetime.now()
        self.delivery_address = delivery_address
        self.notes = notes

    def total_amount(self):
        return sum(item.total() for item in self.items)

    def __repr__(self):
        return f"Order(id={self.id}, customer_id={self.customer_id})"
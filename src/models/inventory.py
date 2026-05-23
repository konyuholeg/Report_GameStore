class MovementType:
    IN  = "in"
    OUT = "out"


class Stock:
    def __init__(self, game_id, game_title, quantity, min_threshold=5):
        self.game_id = game_id
        self.game_title = game_title
        self.quantity = quantity
        self.min_threshold = min_threshold

    def __repr__(self):
        return f"Stock(game_id={self.game_id}, qty={self.quantity})"


class StockMovement:
    def __init__(self, id, game_id, movement_type, quantity, reason, created_at):
        self.id = id
        self.game_id = game_id
        self.movement_type = movement_type
        self.quantity = quantity
        self.reason = reason
        self.created_at = created_at
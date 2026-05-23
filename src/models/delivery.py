class DeliveryStatus:
    SHIPPED   = "відправлено"
    DELIVERED = "доставлено"
    FAILED    = "не доставлено"


class Delivery:
    def __init__(self, id, order_id, status, carrier="",
                 estimated_date="", delivered_at=""):
        self.id = id
        self.order_id = order_id
        self.status = status
        self.carrier = carrier
        self.estimated_date = estimated_date
        self.delivered_at = delivered_at
class DeliveryStatus:
    PENDING    = "pending"
    SHIPPED    = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED  = "delivered"
    FAILED     = "failed"


class Delivery:
    def __init__(self, id, order_id, status, carrier="",
                 tracking_number="", estimated_date="", delivered_at=""):
        self.id = id
        self.order_id = order_id
        self.status = status
        self.carrier = carrier
        self.tracking_number = tracking_number
        self.estimated_date = estimated_date
        self.delivered_at = delivered_at
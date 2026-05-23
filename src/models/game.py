class Category:
    def __init__(self, id, name, description=""):
        self.id = id
        self.name = name
        self.description = description

    def __repr__(self):
        return f"Category(id={self.id}, name={self.name})"


class Game:
    def __init__(self, id, title, developer, category, price,
                 stock_qty, description="", image_url="", release_date=""):
        self.id = id
        self.title = title
        self.developer = developer
        self.category = category
        self.price = price
        self.stock_qty = stock_qty
        self.description = description
        self.image_url = image_url
        self.release_date = release_date

    def __repr__(self):
        return f"Game(id={self.id}, title={self.title})"
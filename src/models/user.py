

class Customer:
    def __init__(self, id, name, email, phone="", address="",
                 password="", role="user"):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.password = password
        self.role = role

    def __repr__(self):
        return f"Customer(id={self.id}, name={self.name})"
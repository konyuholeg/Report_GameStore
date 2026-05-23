from file_storage import read, write, next_id


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


def ensure_admin():
    if not any(c["email"] == "admin@gamestore.com" for c in read("customers")):
        customers = read("customers")
        customers.append({
            "id": next_id("customers"), "name": "Адміністратор",
            "email": "admin@gamestore.com", "phone": "", "address": "",
            "password": "admin123", "role": "admin",
        })
        write("customers", customers)
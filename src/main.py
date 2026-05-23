import flet as ft
from file_storage import read, write, next_id
from views.app_view import AppView
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ""))


def main(page: ft.Page):
    page.title = "GameStore"
    page.window_width = 1280
    page.window_height = 850
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = ft.Colors.GREY_100

    if not any(c["email"] == "admin@gamestore.com" for c in read("customers")):
        customers = read("customers")
        customers.append({
            "id": next_id("customers"), "name": "Адміністратор",
            "email": "admin@gamestore.com", "phone": "", "address": "",
            "password": "admin123", "role": "admin",
        })
        write("customers", customers)

    AppView(page).create_view()


if __name__ == "__main__":
    ft.run(main)
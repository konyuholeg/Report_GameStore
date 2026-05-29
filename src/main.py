import flet as ft
from file_storage import read, write, next_id
from views.app_view import create_header, GRADIENT
from views.catalog_view import CatalogView
from views.order_view import OrderView
from views.profile_view import ProfileView
from views.admin_view import AdminView


def main(page: ft.Page):
    page.title = "GameStore"
    page.window_width = 1280
    page.window_height = 850
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = "#a18dc5"

    if not any(c["email"] == "admin@gamestore.com" for c in read("customers")):
        customers = read("customers")
        customers.append({
            "id": next_id("customers"), "name": "Адміністратор",
            "email": "admin@gamestore.com", "phone": "", "address": "",
            "password": "admin123", "role": "admin",
        })
        write("customers", customers)

    state = {"user": None}
    catalog_view = CatalogView(page, None)

    search_input = ft.TextField(
        hint_text="Пошук ігор...", border=ft.InputBorder.OUTLINE,
        border_radius=24,
        border_color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
        focused_border_color=ft.Colors.WHITE,
        height=42, width=480, content_padding=ft.Padding(20, 0, 20, 0),
        bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
        prefix_icon="search",
        color=ft.Colors.WHITE,
        hint_style=ft.TextStyle(color=ft.Colors.with_opacity(1.0, ft.Colors.WHITE)),
        on_change=lambda e: catalog_view.search_from_header(e.control.value),
    )

    header = ft.Container(height=60)
    current_view = ft.Container(expand=True)

    def show_view(route: str):
        u = state["user"]
        if route == "catalog":
            current_view.content = catalog_view.create_view()
        elif route == "orders":
            current_view.content = OrderView(
                page, u, show_view, on_login_success
            ).create_view()
        elif route == "profile":
            pv = ProfileView(page, u, logout, on_login_success)
            current_view.content = pv.create_view() if u else pv.create_view_guest()
        elif route == "admin":
            if u and u.role == "admin":
                header.height = 0
                header.content = None
                header.gradient = None
                current_view.content = AdminView(page, u, logout).create_view()
        page.update()

    def on_login_success(user):
        state["user"] = user
        catalog_view.set_user(user)
        if user.role == "admin":
            show_view("admin")
        else:
            update_header(user)
            show_view("catalog")

    def logout(e=None):
        state["user"] = None
        catalog_view.set_user(None)
        header.height = 60
        header.gradient = GRADIENT
        update_header(None)
        show_view("catalog")

    def update_header(user):
        new_header = create_header(user, search_input, show_view, on_login_success, logout, page)
        header.content = new_header.content
        header.gradient = new_header.gradient
        header.height = new_header.height
        header.padding = new_header.padding
        page.update()

    catalog_view.show_view = show_view
    catalog_view.on_login_success = on_login_success
    update_header(None)
    page.add(ft.Column([header, current_view], expand=True, spacing=0))
    show_view("catalog")


if __name__ == '__main__':
    ft.run(main, view=ft.AppView.WEB_BROWSER)
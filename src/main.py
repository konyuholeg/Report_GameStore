import flet as ft
from file_storage import read, write, next_id
from views.catalog_view import CatalogView
from views.order_view import OrderView
from views.profile_view import ProfileView
from views.admin_view import AdminView
from views.app_view import build_header


def main(page: ft.Page):
    page.title = "GameStore"
    page.window_width = 1280
    page.window_height = 850
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = "#4a00e0"

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
        hint_text="Пошук ігор", border=ft.InputBorder.OUTLINE,
        hint_style=ft.TextStyle(color=ft.Colors.WHITE),
        border_radius=24,
        border_color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
        focused_border_color=ft.Colors.WHITE,
        height=42, width=480, content_padding=ft.Padding(20, 0, 20, 0),
        bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
        prefix_icon="search",
        color=ft.Colors.WHITE,
        on_change=lambda e: catalog_view.search_from_header(e.control.value),
    )

    def navigate(route: str):
        page.navigate(f"/{route}")

    def on_login_success(user):
        state["user"] = user
        catalog_view.set_user(user)
        navigate("admin" if user.role == "admin" else "catalog")

    def logout(e=None):
        state["user"] = None
        catalog_view.set_user(None)
        navigate("catalog")

    def route_change(e=None):
        route = page.route.lstrip("/") or "catalog"
        u = state["user"]

        # Якщо не адмін намагається зайти на /admin — редирект
        if route == "admin" and (not u or u.role != "admin"):
            page.navigate("/catalog")
            return

        # Якщо адмін на не-адмін маршруті — редирект
        if u and u.role == "admin" and route != "admin":
            page.navigate("/admin")
            return

        page.views.clear()

        if route == "admin" and u and u.role == "admin":
            page.views.append(
                ft.View(
                    route="/admin",
                    padding=0,
                    bgcolor=ft.Colors.GREY_100,
                    controls=[AdminView(page, u, logout).create_view()],
                )
            )
        else:
            header = build_header(
                user=u,
                search_input=search_input,
                navigate=navigate,
                on_login_success=on_login_success,
                logout=logout,
                page=page,
            )

            if route == "orders":
                content = OrderView(page, u, navigate, on_login_success).create_view()
            elif route == "profile":
                pv = ProfileView(page, u, logout, on_login_success)
                content = pv.create_view() if u else pv.create_view_guest()
            else:
                catalog_view.show_view = navigate
                catalog_view.on_login_success = on_login_success
                content = catalog_view.create_view()

            page.views.append(
                ft.View(
                    route=f"/{route}",
                    padding=0,
                    bgcolor="#4a00e0",
                    controls=[
                        ft.Column([header, ft.Container(content=content, expand=True)],
                                  expand=True, spacing=0)
                    ],
                )
            )

        page.update()

    page.on_route_change = route_change
    route_change()


if __name__ == '__main__':
    ft.run(main, view=ft.AppView.WEB_BROWSER)
import flet as ft
from views.catalog_view import CatalogView
from views.order_view import OrderView
from views.profile_view import ProfileView
from views.auth_view import AuthView
from views.admin_view import AdminView


class AppView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.state = {"user": None}
        self.catalog_view = CatalogView(page, None)
        self.current_view = ft.Container(expand=True)
        self.header = ft.Container(
            height=60, bgcolor=ft.Colors.WHITE,
            padding=ft.Padding(24, 0, 24, 0),
            shadow=ft.BoxShadow(blur_radius=8, offset=ft.Offset(0, 2),
                               color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
        )
        self.search_input = ft.TextField(
            hint_text="Пошук ігор...", border=ft.InputBorder.OUTLINE,
            border_radius=24, border_color=ft.Colors.GREY_300,
            focused_border_color=ft.Colors.GREY_600,
            height=42, width=480, content_padding=ft.Padding(20, 0, 20, 0),
            bgcolor=ft.Colors.GREY_50, prefix_icon="search",
            on_change=lambda e: self.catalog_view.search_from_header(e.control.value),
        )

    def _nav_btn(self, text, route):
        return ft.TextButton(
            text, on_click=lambda e: self.show_view(route),
            style=ft.ButtonStyle(color=ft.Colors.GREY_700),
        )

    def create_header(self, user=None):
        if user:
            right = ft.Row([
                self._nav_btn("Каталог", "catalog"),
                self._nav_btn("Кошик", "orders"),
                self._nav_btn("Кабінет", "profile"),
                ft.Container(
                    content=ft.Container(width=1, height=24, bgcolor=ft.Colors.GREY_300),
                    padding=ft.Padding(4, 0, 4, 0),
                ),
                ft.TextButton("Вийти", on_click=self.logout,
                              style=ft.ButtonStyle(color=ft.Colors.RED_400)),
            ], spacing=2)
        else:
            right = ft.Row([
                self._nav_btn("Каталог", "catalog"),
                self._nav_btn("Кошик", "orders"),
                self._nav_btn("Кабінет", "profile"),
                ft.Container(
                    content=ft.Container(width=1, height=24, bgcolor=ft.Colors.GREY_300),
                    padding=ft.Padding(4, 0, 4, 0),
                ),
                ft.Button(
                    "Увійти",
                    on_click=lambda e: AuthView(self.page, self.on_login_success).show_dialog(),
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.INDIGO_700, color=ft.Colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
            ], spacing=2)

        self.header.content = ft.Row([
            ft.Text("GameStore", size=20, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.INDIGO_700),
            ft.Container(width=24),
            self.search_input,
            ft.Container(expand=True),
            right,
        ], vertical_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
        self.page.update()

    def show_view(self, route: str):
        u = self.state["user"]
        if route == "catalog":
            self.current_view.content = self.catalog_view.create_view()
        elif route == "orders":
            self.current_view.content = OrderView(
                self.page, u, self.show_view, self.on_login_success
            ).create_view()
        elif route == "profile":
            pv = ProfileView(self.page, u, self.logout)
            self.current_view.content = pv.create_view() if u else pv.create_view_guest()
        self.page.update()

    def on_login_success(self, user):
        self.state["user"] = user
        self.catalog_view.set_user(user)
        if user.role == "admin":
            self.header.height = 0
            self.header.content = None
            self.current_view.content = AdminView(self.page, user, self.logout).create_view()
            self.page.update()
        else:
            self.create_header(user)
            self.show_view("catalog")

    def logout(self, e=None):
        self.state["user"] = None
        self.catalog_view.set_user(None)
        self.header.height = 60
        self.create_header(None)
        self.show_view("catalog")

    def create_view(self):
        self.catalog_view.show_view = self.show_view
        self.catalog_view.on_login_success = self.on_login_success
        self.create_header(None)
        self.page.add(ft.Column([self.header, self.current_view], expand=True, spacing=0))
        self.show_view("catalog")
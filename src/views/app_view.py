import flet as ft
from views.auth_view import AuthView

GRADIENT = ft.LinearGradient(
    begin=ft.Alignment(-1, -1),
    end=ft.Alignment(1, 1),
    colors=["#4a00e0", "#8e2de2"],
)


def build_header(user, search_input, navigate, on_login_success, logout, page):
    def nav_btn(text, route):
        return ft.TextButton(
            text, on_click=lambda e: navigate(route),
            style=ft.ButtonStyle(color=ft.Colors.WHITE),
        )

    if user:
        right = ft.Row([
            nav_btn("Каталог", "catalog"),
            nav_btn("Кошик",   "orders"),
            nav_btn("Кабінет", "profile"),
            ft.Container(
                content=ft.Container(width=1, height=24,
                                     bgcolor=ft.Colors.with_opacity(0.4, ft.Colors.WHITE)),
                padding=ft.Padding(4, 0, 4, 0),
            ),
            ft.TextButton("Вийти", on_click=logout,
                          style=ft.ButtonStyle(
                              color=ft.Colors.with_opacity(0.8, ft.Colors.WHITE))),
        ], spacing=2)
    else:
        right = ft.Row([
            nav_btn("Каталог", "catalog"),
            nav_btn("Кошик",   "orders"),
            nav_btn("Кабінет", "profile"),
            ft.Container(
                content=ft.Container(width=1, height=24,
                                     bgcolor=ft.Colors.with_opacity(0.4, ft.Colors.WHITE)),
                padding=ft.Padding(4, 0, 4, 0),
            ),
            ft.Button(
                "Увійти",
                on_click=lambda e: AuthView(page, on_login_success).show_dialog(),
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.WHITE,
                    color=ft.Colors.INDIGO_700,
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
            ),
        ], spacing=2)

    return ft.Container(
        height=60,
        padding=ft.Padding(24, 0, 24, 0),
        gradient=GRADIENT,
        content=ft.Row([
            ft.Text("GameStore", size=20, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE),
            ft.Container(width=24),
            search_input,
            ft.Container(expand=True),
            right,
        ], vertical_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
    )
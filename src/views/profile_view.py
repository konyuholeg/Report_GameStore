import flet as ft
from file_storage import read


class ProfileView:
    def __init__(self, page: ft.Page, user, on_logout, on_login_success=None):
        self.page = page
        self.user = user
        self.on_logout = on_logout
        self.on_login_success = on_login_success

    def get_user_orders(self):
        return [o for o in read("orders")
                if o.get("customer_id") == self.user.id and o.get("status") != "cart"]

    def order_card(self, order):
        status_colors = {
            "pending": ft.Colors.ORANGE, "confirmed": ft.Colors.BLUE,
            "shipped": ft.Colors.PURPLE, "delivered": ft.Colors.GREEN,
            "cancelled": ft.Colors.RED,
        }
        status_labels = {
            "pending": "Очікує", "confirmed": "Підтверджено",
            "shipped": "Відправлено", "delivered": "Доставлено",
            "cancelled": "Скасовано",
        }
        status = order.get("status", "pending")
        carrier = order.get("carrier", "")

        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(f"Замовлення #{order['id']}", size=14,
                                weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Text(status_labels.get(status, status),
                                            size=11, color=ft.Colors.WHITE),
                            bgcolor=status_colors.get(status, ft.Colors.GREY),
                            padding=ft.Padding(8, 3, 8, 3), border_radius=6,
                        ),
                        ft.Container(expand=True),
                        ft.Text(f"{order.get('total_amount', 0)} ₴",
                                size=14, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREEN_700),
                    ]),
                    ft.Column([
                        ft.Text(f"• {i['game_title']} x{i['quantity']} - "
                                f"{i['quantity'] * i['unit_price']} ₴",
                                size=12, color=ft.Colors.GREY_700)
                        for i in order.get("items", [])
                    ], spacing=2),
                    ft.Text(f"Доставка: {carrier}", size=11,
                            color=ft.Colors.GREY_500) if carrier else ft.Container(height=0),
                ], spacing=8),
                padding=ft.Padding(16, 12, 16, 12),
            )
        )

    def create_view(self):
        orders = self.get_user_orders()
        order_cards = [self.order_card(o) for o in orders] if orders else [
            ft.Container(
                content=ft.Text("Замовлень поки немає", color=ft.Colors.GREY_500, size=14),
                padding=ft.Padding(0, 8, 0, 8),
            )
        ]

        return ft.Column([
            ft.Container(
                content=ft.Text("Кабінет", size=20, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREY_800),
                padding=ft.Padding(20, 12, 20, 12), bgcolor=ft.Colors.WHITE,
                shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.GREY_200,
                                   offset=ft.Offset(0, 2)),
            ),
            ft.Container(
                content=ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("Мої замовлення", size=15,
                                        weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
                                ft.Container(expand=True),
                                ft.Text(f"Всього: {len(orders)}", size=12,
                                        color=ft.Colors.GREY_500),
                            ]),
                            ft.Divider(),
                            ft.Column(order_cards, spacing=8,
                                      scroll=ft.ScrollMode.AUTO, expand=True),
                        ], spacing=12, expand=True),
                        padding=ft.Padding(20, 16, 20, 16), expand=True,
                    ),
                    elevation=2, expand=True,
                ),
                expand=True, padding=ft.Padding(16, 16, 16, 16),
                bgcolor=ft.Colors.TRANSPARENT,
            ),
        ], expand=True, spacing=0)

    def create_view_guest(self):
        from views.auth_view import AuthView
        auth_view = AuthView(self.page, self.on_login_success)

        return ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Text("Увійдіть щоб переглянути кабінет", size=16,
                            color=ft.Colors.GREY_500),
                    ft.Button(
                        "Увійти / Зареєструватись",
                        on_click=lambda e: auth_view.show_dialog(),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.INDIGO_700,
                            color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
                alignment=ft.Alignment.CENTER, expand=True,
            )
        ], expand=True)
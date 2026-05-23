import flet as ft
from file_storage import read, write
from controllers.inventory_ctrl import InventoryController
from datetime import datetime


class AdminView:
    def __init__(self, page: ft.Page, user, on_logout):
        self.page = page
        self.user = user
        self.on_logout = on_logout
        self.content_area = ft.Container(expand=True)

    def _show_section(self, section: str):
        sections = {
            "orders":    self._create_orders,
            "inventory": self._create_inventory,
            "customers": self._create_customers,
            "delivery":  self._create_delivery,
        }
        self.content_area.content = sections.get(section, self._create_orders)()
        self.page.update()

    def _change_order_status(self, order_id, status, list_ref):
        orders = read("orders")
        for o in orders:
            if o["id"] == order_id:
                o["status"] = status
                break
        write("orders", orders)
        list_ref.controls = self._create_order_cards(list_ref)
        self.page.update()

    def _create_order_cards(self, list_ref):
        orders = [o for o in read("orders") if o.get("status") != "cart"]
        status_labels = {
            "pending": "Очікує", "confirmed": "Підтверджено",
            "shipped": "Відправлено", "delivered": "Доставлено",
            "cancelled": "Скасовано",
        }
        status_colors = {
            "pending": ft.Colors.ORANGE, "confirmed": ft.Colors.BLUE,
            "shipped": ft.Colors.PURPLE, "delivered": ft.Colors.GREEN,
            "cancelled": ft.Colors.RED,
        }
        next_status = {
            "pending": "confirmed", "confirmed": "shipped", "shipped": "delivered",
        }
        if not orders:
            return [ft.Text("Замовлень немає", color=ft.Colors.GREY_500)]

        cards = []
        for o in orders:
            status = o.get("status", "pending")
            ns = next_status.get(status)
            actions = []
            if ns:
                actions.append(ft.TextButton(
                    f"→ {status_labels[ns]}",
                    on_click=lambda e, oid=o["id"], s=ns: self._change_order_status(oid, s, list_ref),
                    style=ft.ButtonStyle(color=ft.Colors.INDIGO_700),
                ))
            if status not in ("cancelled", "delivered"):
                actions.append(ft.TextButton(
                    "Скасувати",
                    on_click=lambda e, oid=o["id"]: self._change_order_status(oid, "cancelled", list_ref),
                    style=ft.ButtonStyle(color=ft.Colors.RED_400),
                ))
            cards.append(ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"Замовлення #{o['id']}", size=14, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Text(status_labels.get(status, status),
                                                size=11, color=ft.Colors.WHITE),
                                bgcolor=status_colors.get(status, ft.Colors.GREY),
                                padding=ft.Padding(8, 3, 8, 3), border_radius=6,
                            ),
                            ft.Container(expand=True),
                            ft.Text(f"{o.get('total_amount', 0)} ₴",
                                    size=14, weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.GREEN_700),
                        ]),
                        ft.Text(
                            f"Клієнт ID: {o.get('customer_id')} | "
                            f"Телефон: {o.get('phone', '—')} | "
                            f"Адреса: {o.get('delivery_address', '—')} | "
                            f"Доставка: {o.get('carrier', '—')}",
                            size=12, color=ft.Colors.GREY_600,
                        ),
                        ft.Column([
                            ft.Text(f"• {i['game_title']} x{i['quantity']}",
                                    size=12, color=ft.Colors.GREY_700)
                            for i in o.get("items", [])
                        ], spacing=2),
                        ft.Row(actions, spacing=8),
                    ], spacing=6),
                    padding=ft.Padding(16, 12, 16, 12),
                ), elevation=2,
            ))
        return cards

    def _create_orders(self):
        list_ref = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
        list_ref.controls = self._create_order_cards(list_ref)
        return ft.Column([
            ft.Container(
                content=ft.Text("Замовлення", size=18, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREY_800),
                padding=ft.Padding(16, 12, 16, 12), bgcolor=ft.Colors.WHITE,
                shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.GREY_200,
                                   offset=ft.Offset(0, 2)),
            ),
            ft.Container(content=list_ref, expand=True,
                         padding=ft.Padding(16, 16, 16, 16),
                         bgcolor=ft.Colors.GREY_100),
        ], expand=True, spacing=0)

    def _create_inventory(self):
        ctrl = InventoryController()

        def add_stock(game_id, qty_field, list_ref):
            try:
                qty = int(qty_field.value or 0)
                if qty <= 0:
                    return
                ctrl.add_stock(game_id, qty, "Поповнення")
                qty_field.value = ""
                list_ref.controls = create_stock_cards(list_ref)
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Запас поповнено"),
                    bgcolor=ft.Colors.GREEN_700, open=True,
                )
                self.page.update()
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(str(ex)),
                    bgcolor=ft.Colors.RED_600, open=True,
                )
                self.page.update()

        def create_stock_cards(list_ref):
            stocks = ctrl.get_all_stock()
            cards = []
            for s in stocks:
                color = ft.Colors.RED_400 if s.quantity <= 5 else ft.Colors.GREEN_600
                qty_field = ft.TextField(
                    hint_text="Кількість", width=100, height=36,
                    border_radius=8, content_padding=ft.Padding(8, 0, 8, 0),
                    keyboard_type=ft.KeyboardType.NUMBER,
                )
                cards.append(ft.Card(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(s.game_title, size=14, weight=ft.FontWeight.BOLD),
                                ft.Row([
                                    ft.Text("Залишок:", size=12, color=ft.Colors.GREY_600),
                                    ft.Text(f"{s.quantity} шт.", size=13,
                                            weight=ft.FontWeight.BOLD, color=color),
                                ], spacing=4),
                            ], expand=True, spacing=4),
                            qty_field,
                            ft.Button(
                                "Поповнити",
                                on_click=lambda e, gid=s.game_id, qf=qty_field: add_stock(gid, qf, list_ref),
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.INDIGO_700, color=ft.Colors.WHITE,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=ft.Padding(16, 12, 16, 12),
                    ), elevation=2,
                ))
            return cards

        list_ref = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
        list_ref.controls = create_stock_cards(list_ref)
        return ft.Column([
            ft.Container(
                content=ft.Text("Склад", size=18, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREY_800),
                padding=ft.Padding(16, 12, 16, 12), bgcolor=ft.Colors.WHITE,
                shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.GREY_200,
                                   offset=ft.Offset(0, 2)),
            ),
            ft.Container(content=list_ref, expand=True,
                         padding=ft.Padding(16, 16, 16, 16),
                         bgcolor=ft.Colors.GREY_100),
        ], expand=True, spacing=0)

    def _create_customers(self):
        customers = [c for c in read("customers") if c.get("role") != "admin"]
        orders = read("orders")
        cards = []
        for c in customers:
            user_orders = [o for o in orders
                           if o.get("customer_id") == c["id"] and o.get("status") != "cart"]
            cards.append(ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        ft.CircleAvatar(
                            content=ft.Text(c["name"][0].upper(),
                                            color=ft.Colors.WHITE, size=18),
                            bgcolor=ft.Colors.INDIGO_700, radius=24,
                        ),
                        ft.Container(width=12),
                        ft.Column([
                            ft.Text(c["name"], size=14, weight=ft.FontWeight.BOLD),
                            ft.Text(c["email"], size=12, color=ft.Colors.GREY_500),
                            ft.Text(c.get("phone", "—"), size=12, color=ft.Colors.GREY_500),
                        ], expand=True, spacing=3),
                        ft.Text(f"Замовлень: {len(user_orders)}", size=12,
                                color=ft.Colors.GREY_600),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(16, 12, 16, 12),
                ), elevation=2,
            ))

        list_view = ft.Column(
            controls=cards if cards else [ft.Text("Клієнтів немає", color=ft.Colors.GREY_500)],
            spacing=8, scroll=ft.ScrollMode.AUTO, expand=True,
        )
        return ft.Column([
            ft.Container(
                content=ft.Text("Клієнти", size=18, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREY_800),
                padding=ft.Padding(16, 12, 16, 12), bgcolor=ft.Colors.WHITE,
                shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.GREY_200,
                                   offset=ft.Offset(0, 2)),
            ),
            ft.Container(content=list_view, expand=True,
                         padding=ft.Padding(16, 16, 16, 16),
                         bgcolor=ft.Colors.GREY_100),
        ], expand=True, spacing=0)

    def _create_delivery(self):
        orders = [o for o in read("orders")
                  if o.get("status") not in ("cart", "cancelled")]

        def update_delivery_status(did, status, list_ref):
            devs = read("deliveries")
            for d in devs:
                if d["id"] == did:
                    d["status"] = status
                    if status == "delivered":
                        d["delivered_at"] = str(datetime.now())
                    break
            write("deliveries", devs)
            list_ref.controls = create_delivery_cards(list_ref)
            self.page.update()

        def create_delivery(order_id, list_ref):
            devs = read("deliveries")
            devs.append({
                "id": len(devs) + 1,
                "order_id": order_id,
                "status": "shipped",
                "carrier": "Нова Пошта",
                "tracking_number": "",
                "created_at": str(datetime.now()),
            })
            write("deliveries", devs)
            list_ref.controls = create_delivery_cards(list_ref)
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Доставку створено"),
                bgcolor=ft.Colors.GREEN_700, open=True,
            )
            self.page.update()

        def create_delivery_cards(list_ref):
            deliveries = read("deliveries")
            delivered_ids = {d["order_id"] for d in deliveries}
            cards = []
            for d in deliveries:
                status = d.get("status", "pending")
                actions = []
                if status == "shipped":
                    actions.append(ft.TextButton(
                        "Доставлено",
                        on_click=lambda e, did=d["id"]: update_delivery_status(did, "delivered", list_ref),
                        style=ft.ButtonStyle(color=ft.Colors.GREEN_700),
                    ))
                cards.append(ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"Доставка — Замовлення #{d['order_id']}",
                                        size=14, weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                ft.Text(status, size=12, color=ft.Colors.BLUE_700),
                            ]),
                            ft.Text(f"Перевізник: {d.get('carrier', '—')}",
                                    size=12, color=ft.Colors.GREY_600),
                            ft.Row(actions, spacing=8),
                        ], spacing=6),
                        padding=ft.Padding(16, 12, 16, 12),
                    ), elevation=2,
                ))
            for o in orders:
                if o["id"] not in delivered_ids:
                    cards.append(ft.Card(
                        content=ft.Container(
                            content=ft.Row([
                                ft.Text(f"Замовлення #{o['id']} — потребує доставки",
                                        size=14, color=ft.Colors.ORANGE_700,
                                        weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                ft.Button(
                                    "Створити доставку",
                                    on_click=lambda e, oid=o["id"]: create_delivery(oid, list_ref),
                                    style=ft.ButtonStyle(
                                        bgcolor=ft.Colors.INDIGO_700, color=ft.Colors.WHITE,
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                    ),
                                ),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=ft.Padding(16, 12, 16, 12),
                        ), elevation=2,
                    ))
            return cards if cards else [ft.Text("Доставок немає", color=ft.Colors.GREY_500)]

        list_ref = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
        list_ref.controls = create_delivery_cards(list_ref)
        return ft.Column([
            ft.Container(
                content=ft.Text("Доставка", size=18, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREY_800),
                padding=ft.Padding(16, 12, 16, 12), bgcolor=ft.Colors.WHITE,
                shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.GREY_200,
                                   offset=ft.Offset(0, 2)),
            ),
            ft.Container(content=list_ref, expand=True,
                         padding=ft.Padding(16, 16, 16, 16),
                         bgcolor=ft.Colors.GREY_100),
        ], expand=True, spacing=0)

    def create_view(self):
        self._show_section("orders")
        sidebar = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Text("GameStore", size=16, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.INDIGO_700),
                        ft.Text("Адмін панель", size=11, color=ft.Colors.GREY_500),
                    ], spacing=2),
                    padding=ft.Padding(16, 16, 16, 8),
                ),
                ft.Divider(),
                *[
                    ft.TextButton(
                        label,
                        on_click=lambda e, s=section: self._show_section(s),
                        style=ft.ButtonStyle(color=ft.Colors.GREY_700),
                    )
                    for label, section in [
                        ("Замовлення", "orders"),
                        ("Склад", "inventory"),
                        ("Доставка", "delivery"),
                        ("Клієнти", "customers"),
                    ]
                ],
                ft.Container(expand=True),
                ft.Divider(),
                ft.TextButton(
                    "Вийти",
                    on_click=self.on_logout,
                    style=ft.ButtonStyle(color=ft.Colors.RED_400),
                ),
            ], expand=True),
            width=200, bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.GREY_200,
                               offset=ft.Offset(2, 0)),
        )
        return ft.Row([sidebar, self.content_area], expand=True, spacing=0)
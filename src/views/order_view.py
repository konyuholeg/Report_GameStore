import flet as ft
from file_storage import read, write



class OrderView:
    def __init__(self, page: ft.Page, current_user=None, show_view=None, on_login_success=None):
        self.page = page
        self.current_user = current_user
        self.show_view = show_view
        self.on_login_success = on_login_success
        self.list_view = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    def _get_cart(self):
        if not self.current_user:
            return None
        for o in read("orders"):
            if o.get("customer_id") == self.current_user.id and o.get("status") == "cart":
                return o
        return None

    def _remove_item(self, game_id: int):
        orders = read("orders")
        for o in orders:
            if o.get("customer_id") == self.current_user.id and o.get("status") == "cart":
                o["items"] = [i for i in o["items"] if i["game_id"] != game_id]
                o["total_amount"] = sum(i["quantity"] * i["unit_price"] for i in o["items"])
                break
        write("orders", orders)
        self.list_view.controls = self._create_items()
        self.page.update()

    def _update_qty(self, game_id: int, delta: int):
        orders = read("orders")
        for o in orders:
            if o.get("customer_id") == self.current_user.id and o.get("status") == "cart":
                for item in o["items"]:
                    if item["game_id"] == game_id:
                        item["quantity"] = max(1, item["quantity"] + delta)
                o["total_amount"] = sum(i["quantity"] * i["unit_price"] for i in o["items"])
                break
        write("orders", orders)
        self.list_view.controls = self._create_items()
        self.page.update()

    def _checkout(self, e):
        cart = self._get_cart()
        if not cart:
            return

        total = cart.get("total_amount", 0)
        delivery_method = {"value": "Нова Пошта"}
        payment_method = {"value": "cash"}
        error_text = ft.Text("", color=ft.Colors.RED_400, size=12)

        saved_phone = ""
        for c in read("customers"):
            if c["id"] == self.current_user.id:
                saved_phone = c.get("phone", "")
                break

        phone_field = ft.TextField(
            label="Номер телефону",
            value=saved_phone if saved_phone else "+380",
            border_radius=8,
            content_padding=ft.Padding(12, 0, 12, 0),
            keyboard_type=ft.KeyboardType.PHONE,
        )

        address_field = ft.TextField(
            label="Адреса доставки",
            hint_text="м. Київ, вул. Хрещатик 1",
            border_radius=8,
            content_padding=ft.Padding(12, 0, 12, 0),
            value=self.current_user.address if self.current_user.address else "",
        )

        card_number_field = ft.TextField(
            label="Номер картки", hint_text="XXXX XXXX XXXX XXXX",
            border_radius=8, content_padding=ft.Padding(12, 0, 12, 0),
            keyboard_type=ft.KeyboardType.NUMBER, max_length=19, visible=False,
        )
        cvv_field = ft.TextField(
            label="CVV", hint_text="XXX", border_radius=8,
            content_padding=ft.Padding(12, 0, 12, 0),
            keyboard_type=ft.KeyboardType.NUMBER,
            password=True, max_length=3, width=120, visible=False,
        )
        expiry_field = ft.TextField(
            label="Термін дії", hint_text="MM/YY", border_radius=8,
            content_padding=ft.Padding(12, 0, 12, 0),
            max_length=5, width=120, visible=False,
        )
        card_fields = ft.Column([
            card_number_field,
            ft.Row([expiry_field, cvv_field], spacing=12),
        ], spacing=10, visible=False)

        overlay_ref = {"obj": None}

        def _close_dialog():
            o = overlay_ref["obj"]
            if o and o in self.page.overlay:
                self.page.overlay.remove(o)
            self.page.update()

        def select_payment(method):
            payment_method["value"] = method
            is_card = method == "card"
            card_fields.visible = is_card
            card_number_field.visible = is_card
            cvv_field.visible = is_card
            expiry_field.visible = is_card
            for name, btn in payment_btns.items():
                btn.style = ft.ButtonStyle(
                    bgcolor=ft.Colors.INDIGO_700 if name == method else ft.Colors.GREY_200,
                    color=ft.Colors.WHITE if name == method else ft.Colors.GREY_700,
                    shape=ft.RoundedRectangleBorder(radius=8),
                )
            self.page.update()

        payment_btns = {
            "cash": ft.Button(
                "Готівка",
                on_click=lambda e: select_payment("cash"),
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.INDIGO_700, color=ft.Colors.WHITE,
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
            ),
            "card": ft.Button(
                "Карткою",
                on_click=lambda e: select_payment("card"),
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.GREY_200, color=ft.Colors.GREY_700,
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
            ),
        }

        def select_delivery(method):
            delivery_method["value"] = method
            for n, b in delivery_btns.items():
                b.style = ft.ButtonStyle(
                    bgcolor=ft.Colors.INDIGO_700 if n == method else ft.Colors.GREY_200,
                    color=ft.Colors.WHITE if n == method else ft.Colors.GREY_700,
                    shape=ft.RoundedRectangleBorder(radius=8),
                )
            self.page.update()

        delivery_btns = {
            "Нова Пошта": ft.Button(
                "Нова Пошта",
                on_click=lambda e: select_delivery("Нова Пошта"),
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.INDIGO_700, color=ft.Colors.WHITE,
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
            ),
            "Укрпошта": ft.Button(
                "Укрпошта",
                on_click=lambda e: select_delivery("Укрпошта"),
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.GREY_200, color=ft.Colors.GREY_700,
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
            ),
            "Самовивіз": ft.Button(
                "Самовивіз",
                on_click=lambda e: select_delivery("Самовивіз"),
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.GREY_200, color=ft.Colors.GREY_700,
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
            ),
        }

        def confirm(e):
            phone = phone_field.value.strip()
            if not phone or phone == "+380":
                error_text.value = "Введіть номер телефону"
                self.page.update()
                return
            if not address_field.value.strip():
                error_text.value = "Введіть адресу доставки"
                self.page.update()
                return
            if payment_method["value"] == "card":
                card_num = card_number_field.value.replace(" ", "")
                if len(card_num) < 16 or not card_num.isdigit():
                    error_text.value = "Введіть коректний номер картки (16 цифр)"
                    self.page.update()
                    return
                if len(cvv_field.value) != 3 or not cvv_field.value.isdigit():
                    error_text.value = "Введіть коректний CVV (3 цифри)"
                    self.page.update()
                    return
                if len(expiry_field.value) != 5 or expiry_field.value[2] != "/":
                    error_text.value = "Введіть термін дії картки (MM/YY)"
                    self.page.update()
                    return

            orders = read("orders")
            confirmed_items = []
            for o in orders:
                if o.get("customer_id") == self.current_user.id and o.get("status") == "cart":
                    o["status"] = "pending"
                    o["phone"] = phone
                    o["delivery_address"] = address_field.value.strip()
                    o["carrier"] = delivery_method["value"]
                    o["payment_method"] = payment_method["value"]
                    confirmed_items = o.get("items", [])
                    break
            write("orders", orders)

            if confirmed_items:
                games = read("games")
                for item in confirmed_items:
                    for game in games:
                        if game["id"] == item["game_id"]:
                            game["stock_qty"] = max(0, game["stock_qty"] - item["quantity"])
                            break
                write("games", games)

            customers = read("customers")
            for c in customers:
                if c["id"] == self.current_user.id:
                    c["phone"] = phone
                    break
            write("customers", customers)

            _close_dialog()
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Замовлення успішно оформлено!"),
                bgcolor=ft.Colors.GREEN_700, open=True,
            )
            self.list_view.controls = self._create_items()
            self.page.update()

        modal = ft.Container(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Оформлення замовлення", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Сума до сплати: {total} ₴",
                            size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                    ft.Divider(),
                    ft.Text("Спосіб доставки", size=13, weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_700),
                    ft.Row(list(delivery_btns.values()), spacing=8, wrap=True),
                    ft.Text("Спосіб оплати", size=13, weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_700),
                    ft.Row(list(payment_btns.values()), spacing=8),
                    card_fields,
                    phone_field,
                    address_field,
                    error_text,
                    ft.Row([
                        ft.TextButton(
                            "Скасувати",
                            on_click=lambda e: _close_dialog(),
                            style=ft.ButtonStyle(color=ft.Colors.GREY_700),
                        ),
                        ft.Button(
                            "Підтвердити",
                            on_click=confirm,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.INDIGO_700, color=ft.Colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                        ),
                    ], alignment=ft.MainAxisAlignment.END, spacing=8),
                ], spacing=12, scroll=ft.ScrollMode.AUTO, tight=True),
                bgcolor=ft.Colors.WHITE,
                border_radius=16,
                padding=ft.Padding(24, 24, 24, 24),
                width=440,
            ),
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
            expand=True,
            alignment=ft.Alignment.CENTER,
        )

        overlay_ref["obj"] = modal
        self.page.overlay.append(modal)
        self.page.update()

    def _get_game_image(self, game_id: int):
        for g in read("games"):
            if g["id"] == game_id:
                return g.get("image_url", "")
        return ""

    def _create_items(self):
        cart = self._get_cart()
        if not cart or not cart.get("items"):
            return [ft.Container(
                content=ft.Column([
                    ft.Text("Кошик порожній", size=18, color=ft.Colors.GREY_500),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.Alignment.CENTER, expand=True,
            )]

        items = []
        for item in cart["items"]:
            image_url = self._get_game_image(item["game_id"])
            if image_url:
                img = ft.Container(
                    content=ft.Image(src=image_url, width=48, height=48, fit="cover"),
                    width=48, height=48, border_radius=6,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                )
            else:
                img = ft.Container(
                    width=48, height=48, bgcolor=ft.Colors.INDIGO_100, border_radius=6,
                    content=ft.Text(item["game_title"][:2].upper(), size=14,
                                    weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_700,
                                    text_align=ft.TextAlign.CENTER),
                    alignment=ft.Alignment.CENTER,
                )

            items.append(ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        img,
                        ft.Container(width=8),
                        ft.Text(item["game_title"], size=14, weight=ft.FontWeight.BOLD,
                                max_lines=2, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                        ft.Row([
                            ft.TextButton("−",
                                on_click=lambda e, gid=item["game_id"]: self._update_qty(gid, -1),
                                style=ft.ButtonStyle(color=ft.Colors.GREY_700)),
                            ft.Text(str(item["quantity"]), size=14,
                                    weight=ft.FontWeight.BOLD, width=30,
                                    text_align=ft.TextAlign.CENTER),
                            ft.TextButton("+",
                                on_click=lambda e, gid=item["game_id"]: self._update_qty(gid, 1),
                                style=ft.ButtonStyle(color=ft.Colors.GREY_700)),
                        ], spacing=0),
                        ft.Text(f"{item['quantity'] * item['unit_price']} ₴",
                                size=15, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREEN_700, width=80,
                                text_align=ft.TextAlign.RIGHT),
                        ft.TextButton("x",
                            on_click=lambda e, gid=item["game_id"]: self._remove_item(gid),
                            style=ft.ButtonStyle(color=ft.Colors.RED_400)),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(16, 12, 16, 12),
                ), elevation=2,
            ))

        total = cart.get("total_amount", 0)
        items.append(ft.Card(
            content=ft.Container(
                content=ft.Row([
                    ft.Text(f"Разом: {total} ₴", size=18, weight=ft.FontWeight.BOLD),
                    ft.Button(
                        "Оформити замовлення",
                        on_click=self._checkout,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.INDIGO_700, color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.Padding(16, 16, 16, 16),
            ), elevation=2,
        ))
        return items

    def create_view(self):
        if not self.current_user:
            from views.auth_view import AuthView
            auth_view = AuthView(self.page, self.on_login_success)
            return ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Text("Увійдіть щоб переглянути кошик", size=16,
                                color=ft.Colors.GREY_500),
                        ft.Button(
                            "Увійти / Зареєструватись",
                            on_click=lambda e: auth_view.show_dialog(),
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.INDIGO_700, color=ft.Colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
                    alignment=ft.Alignment.CENTER, expand=True,
                )
            ], expand=True)

        self.list_view = ft.Column(
            controls=self._create_items(),
            spacing=8, scroll=ft.ScrollMode.AUTO, expand=True,
        )
        return ft.Column([
            ft.Container(
                content=ft.Text("Кошик", size=20, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREY_800),
                padding=ft.Padding(20, 12, 20, 12), bgcolor=ft.Colors.WHITE,
                shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.GREY_200,
                                   offset=ft.Offset(0, 2)),
            ),
            ft.Container(
                content=self.list_view, expand=True,
                padding=ft.Padding(16, 16, 16, 16), bgcolor=ft.Colors.GREY_100,
            ),
        ], expand=True, spacing=0)
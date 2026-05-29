import re
import flet as ft
from file_storage import read, write



def validate_phone(phone: str) -> bool:
    return bool(re.match(r"^\+380\d{9}$", phone))


def validate_address(address: str) -> bool:
    return bool(re.match(r"^.{5,}$", address.strip()))


def validate_card_number(number: str) -> bool:
    return bool(re.match(r"^\d{16}$", number))


def validate_cvv(cvv: str) -> bool:
    return bool(re.match(r"^\d{3}$", cvv))


def validate_expiry(expiry: str) -> bool:
    return bool(re.match(r"^(0[1-9]|1[0-2])\/\d{2}$", expiry))


class OrderView:
    def __init__(self, page: ft.Page, current_user=None, show_view=None, on_login_success=None):
        self.page = page
        self.current_user = current_user
        self.show_view = show_view
        self.on_login_success = on_login_success
        self.list_view = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    def get_cart(self):
        if not self.current_user:
            return None
        for o in read("orders"):
            if o.get("customer_id") == self.current_user.id and o.get("status") == "cart":
                return o
        return None

    def remove_item(self, game_id):
        orders = read("orders")
        for o in orders:
            if o.get("customer_id") == self.current_user.id and o.get("status") == "cart":
                o["items"] = [i for i in o["items"] if i["game_id"] != game_id]
                o["total_amount"] = sum(i["quantity"] * i["unit_price"] for i in o["items"])
                break
        write("orders", orders)
        self.list_view.controls = self.create_items()
        self.page.update()

    def update_qty(self, game_id, delta):
        games = read("games")
        stock = next((g["stock_qty"] for g in games if g["id"] == game_id), 0)

        orders = read("orders")
        for o in orders:
            if o.get("customer_id") == self.current_user.id and o.get("status") == "cart":
                for item in o["items"]:
                    if item["game_id"] == game_id:
                        new_qty = item["quantity"] + delta
                        if delta > 0 and item["quantity"] >= stock:
                            self.page.snack_bar = ft.SnackBar(
                                content=ft.Text(
                                    f"Більше на складі немає (доступно: {stock} шт.)",
                                    color=ft.Colors.WHITE,
                                ),
                                bgcolor=ft.Colors.RED_700, open=True, duration=2500,
                            )
                            self.page.update()
                            return
                        item["quantity"] = max(1, new_qty)
                o["total_amount"] = sum(i["quantity"] * i["unit_price"] for i in o["items"])
                break
        write("orders", orders)
        self.list_view.controls = self.create_items()
        self.page.update()

    def checkout(self, e):
        cart = self.get_cart()
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
            hint_text="м. Львів, вул. Бахматюка 1",
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
            if not validate_phone(phone):
                error_text.value = "Телефон має бути у форматі +380XXXXXXXXX (9 цифр після +380)"
                self.page.update()
                return

            address = address_field.value.strip()
            if not validate_address(address):
                error_text.value = "Введіть коректну адресу (мінімум 5 символів)"
                self.page.update()
                return

            if payment_method["value"] == "card":
                card_num = card_number_field.value.replace(" ", "")
                if not validate_card_number(card_num):
                    error_text.value = "Номер картки має містити 16 цифр"
                    self.page.update()
                    return
                if not validate_cvv(cvv_field.value):
                    error_text.value = "CVV має містити 3 цифри"
                    self.page.update()
                    return
                if not validate_expiry(expiry_field.value):
                    error_text.value = "Термін дії має бути у форматі MM/YY"
                    self.page.update()
                    return

            orders = read("orders")
            confirmed_items = []
            for o in orders:
                if o.get("customer_id") == self.current_user.id and o.get("status") == "cart":
                    o["status"] = "pending"
                    o["phone"] = phone
                    o["delivery_address"] = address
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

            self.page.pop_dialog()
            self.list_view.controls = self.create_items()

            def on_ok(e):
                self.page.pop_dialog()
                self.page.update()

            success_dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text(
                    "Замовлення успішно оформлено!",
                    size=18, weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                content=ft.Text(
                    "Дякуємо за покупку. Ваше замовлення передано в обробку.",
                    text_align=ft.TextAlign.CENTER,
                ),
                actions=[
                    ft.Button(
                        "OK",
                        on_click=on_ok,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.INDIGO_700,
                            color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.CENTER,
            )
            self.page.show_dialog(success_dlg)

        dialog_content = ft.Container(
                width=440,
                content=ft.Column([
                    ft.Container(
                        content=ft.Row([
                            ft.Text("Сума:", size=13, color=ft.Colors.GREY_600),
                            ft.Text(f"{total} ₴", size=16, weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.GREEN_700),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        bgcolor=ft.Colors.GREEN_50, border_radius=8,
                        padding=ft.Padding(12, 10, 12, 10),
                    ),
                    ft.Divider(),
                    ft.Text("Спосіб доставки", size=14, weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_800),
                    ft.Row(list(delivery_btns.values()), spacing=8),
                    address_field,
                    phone_field,
                    ft.Divider(),
                    ft.Text("Спосіб оплати", size=14, weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_800),
                    ft.Row(list(payment_btns.values()), spacing=8),
                    card_fields,
                    ft.Divider(),
                    error_text,
                    ft.Row([
                        ft.TextButton(
                            "Скасувати",
                            on_click=lambda e: [
                                self.page.pop_dialog(),
                                self.page.update(),
                            ],
                            style=ft.ButtonStyle(color=ft.Colors.GREY_600),
                        ),
                        ft.Button(
                            "Підтвердити",
                            on_click=confirm,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.INDIGO_700,
                                color=ft.Colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                        ),
                    ], alignment=ft.MainAxisAlignment.END, spacing=8),
                ], spacing=12, tight=True, scroll=ft.ScrollMode.AUTO),
            )
        dialog = ft.AlertDialog(
            modal=False,
            title=ft.Text("Оформлення замовлення", size=18, weight=ft.FontWeight.BOLD),
            content=dialog_content,
            actions=[],
        )
        self.page.show_dialog(dialog)

    def get_game_image(self, game_id):
        for g in read("games"):
            if g["id"] == game_id:
                return g.get("image_url", "")
        return ""

    def create_items(self):
        cart = self.get_cart()
        if not cart or not cart.get("items"):
            return [ft.Container(
                content=ft.Column([
                    ft.Text("Кошик порожній", size=18, color=ft.Colors.GREY_500),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.Alignment.CENTER, expand=True,
            )]

        items = []
        for item in cart["items"]:
            image_url = self.get_game_image(item["game_id"])
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


            games = read("games")
            stock = next((g["stock_qty"] for g in games if g["id"] == item["game_id"]), 0)
            at_max = item["quantity"] >= stock

            items.append(ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        img,
                        ft.Container(width=8),
                        ft.Text(item["game_title"], size=14, weight=ft.FontWeight.BOLD,
                                max_lines=2, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                        ft.Column([
                            ft.Row([
                                ft.TextButton("−",
                                              on_click=lambda e, gid=item["game_id"]: self.update_qty(gid, -1),
                                              style=ft.ButtonStyle(color=ft.Colors.GREY_700)),
                                ft.Text(str(item["quantity"]), size=14,
                                        weight=ft.FontWeight.BOLD, width=30,
                                        text_align=ft.TextAlign.CENTER),
                                ft.TextButton("+",
                                              on_click=lambda e, gid=item["game_id"]: self.update_qty(gid, 1),
                                              style=ft.ButtonStyle(color=ft.Colors.GREY_700)),
                            ], spacing=0),
                            ft.Text(
                                "Більше на складі немає",
                                size=10, color=ft.Colors.RED_400,
                                visible=at_max,
                            ),
                        ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Text(f"{item['quantity'] * item['unit_price']} ₴",
                                size=15, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREEN_700, width=80,
                                text_align=ft.TextAlign.RIGHT),
                        ft.TextButton("x",
                                      on_click=lambda e, gid=item["game_id"]: self.remove_item(gid),
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
                        on_click=self.checkout,
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
            controls=self.create_items(),
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
                padding=ft.Padding(16, 16, 16, 16), bgcolor=ft.Colors.TRANSPARENT,
            ),
        ], expand=True, spacing=0)
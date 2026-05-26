import flet as ft
from controllers.game_ctrl import GameController
from file_storage import read, write, next_id
from datetime import datetime

COLORS = [
    ft.Colors.INDIGO_700, ft.Colors.PURPLE_700, ft.Colors.TEAL_700,
    ft.Colors.BLUE_700, ft.Colors.RED_700, ft.Colors.GREEN_700,
    ft.Colors.ORANGE_700, ft.Colors.PINK_700,
]


class CatalogView:
    def __init__(self, page: ft.Page, show_view=None):
        self.page = page
        self.ctrl = GameController()
        self.show_view = show_view
        self.all_games = []
        self.search_query = ""
        self.current_user = None
        self.on_login_success = None

        self.selected_genre = "Всі"
        self.genre_row = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=8)
        self.price_from_field = ft.TextField(
            value="", width=90, height=40, border_radius=8,
            content_padding=ft.Padding(8, 0, 8, 0),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
            focused_border_color=ft.Colors.WHITE,
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
        )
        self.price_to_field = ft.TextField(
            value="", width=90, height=40, border_radius=8,
            content_padding=ft.Padding(8, 0, 8, 0),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
            focused_border_color=ft.Colors.WHITE,
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
        )
        self.wrap = ft.Row(wrap=True, spacing=16, run_spacing=16)

    def _create_genre_row(self, genre_options):
        def make_btn(g):
            def on_click(e, genre=g):
                self.selected_genre = genre
                self._create_genre_row(genre_options)
                self._apply_filters()
            return ft.Button(
                g, on_click=on_click, height=34,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.WHITE if g == self.selected_genre else ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
                    color=ft.Colors.INDIGO_700 if g == self.selected_genre else ft.Colors.WHITE,
                    shape=ft.RoundedRectangleBorder(radius=20),
                    padding=ft.Padding(12, 0, 12, 0),
                ),
            )
        self.genre_row.controls = [make_btn(g) for g in genre_options]
        self.page.update()

    def set_user(self, user):
        self.current_user = user

    def search_from_header(self, query: str):
        self.search_query = query.strip().lower()
        self._apply_filters()

    def _reset_filters(self):
        self.selected_genre = "Всі"
        self.price_from_field.value = ""
        self.price_to_field.value = ""
        self.search_query = ""

    def _apply_filters(self):
        from_val = self.price_from_field.value.strip()
        to_val   = self.price_to_field.value.strip()

        try:
            price_from = int(from_val) if from_val else None
        except ValueError:
            price_from = None
        try:
            price_to = int(to_val) if to_val else None
        except ValueError:
            price_to = None

        genre = self.selected_genre
        filtered = []
        for game in self.all_games:
            if genre != "Всі" and game.category.name != genre:
                continue
            if price_from is not None and game.price < price_from:
                continue
            if price_to is not None and game.price > price_to:
                continue
            if self.search_query and self.search_query not in game.title.lower():
                continue
            filtered.append(game)

        self.wrap.controls = [self._game_card(g, i) for i, g in enumerate(filtered)]
        self.page.update()

    def _remove_from_overlay(self, container):
        if container in self.page.overlay:
            self.page.overlay.remove(container)
        self.page.update()

    def _show_modal(self, text, color=ft.Colors.GREEN_700, error=False):
        modal_ref = {"obj": None}

        def close(e):
            if modal_ref["obj"] in self.page.overlay:
                self.page.overlay.remove(modal_ref["obj"])
            self.page.update()

        modal = ft.Container(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("✕" if error else "", size=36, color=color,
                            text_align=ft.TextAlign.CENTER) if error else ft.Container(height=0),
                    ft.Text(text, size=13, color=ft.Colors.GREY_800,
                            text_align=ft.TextAlign.CENTER),
                    ft.Container(height=8),
                    ft.Button(
                        "OK",
                        on_click=close,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.INDIGO_700, color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                    ),
                ], spacing=8, tight=True,
                   horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.Colors.WHITE,
                border_radius=16,
                padding=ft.Padding(32, 24, 32, 24),
                width=280,
            ),
            expand=True,
            alignment=ft.Alignment.CENTER,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
        )
        modal_ref["obj"] = modal
        self.page.overlay.append(modal)
        self.page.update()

    def _add_to_cart(self, game, details_overlay=None):
        if not self.current_user:
            from views.auth_view import AuthView

            if details_overlay is not None:
                self._remove_from_overlay(details_overlay)

            def on_success(user):
                self.current_user = user
                self._add_to_cart(game)
                if self.on_login_success:
                    self.on_login_success(user)

            AuthView(self.page, on_success).show_dialog()
            return

        cart = read("orders")
        existing = next((o for o in cart
                         if o.get("customer_id") == self.current_user.id
                         and o.get("status") == "cart"), None)

        if game.stock_qty <= 0:
            self._show_modal(f"'{game.title}' немає на складі",
                             color=ft.Colors.RED_700, error=True)
            return

        if existing:
            items = existing.get("items", [])
            found = False
            for item in items:
                if item["game_id"] == game.id:
                    if item["quantity"] >= game.stock_qty:
                        self._show_modal(
                            f"Більше немає.\nНа складі лише {game.stock_qty} шт.",
                            color=ft.Colors.RED_700, error=True,
                        )
                        return
                    item["quantity"] += 1
                    found = True
                    break
            if not found:
                items.append({"game_id": game.id, "game_title": game.title,
                               "quantity": 1, "unit_price": game.price})
            existing["items"] = items
            existing["total_amount"] = sum(i["quantity"] * i["unit_price"] for i in items)
            write("orders", cart)
        else:
            cart.append({
                "id": next_id("orders"),
                "customer_id": self.current_user.id,
                "status": "cart",
                "total_amount": game.price,
                "delivery_address": "", "notes": "",
                "created_at": str(datetime.now()),
                "items": [{"game_id": game.id, "game_title": game.title,
                            "quantity": 1, "unit_price": game.price}],
            })
            write("orders", cart)

        if details_overlay is not None:
            self._remove_from_overlay(details_overlay)

        self._show_modal(f"'{game.title}'\nдодано до кошика")

    def _show_details(self, game):
        release = game.release_date[:4] if game.release_date else "-"

        if game.image_url:
            image_block = ft.Container(
                content=ft.Image(src=game.image_url, width=320, height=180,
                                 fit="contain"),
                width=320, height=180,
                bgcolor=ft.Colors.GREY_900,
                border_radius=ft.BorderRadius(12, 12, 0, 0),
            )
        else:
            image_block = ft.Container(
                content=ft.Text(game.title[:2].upper(), size=48,
                                weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE,
                                text_align=ft.TextAlign.CENTER),
                bgcolor=ft.Colors.INDIGO_700,
                alignment=ft.Alignment.CENTER,
                width=320, height=180,
                border_radius=ft.BorderRadius(12, 12, 0, 0),
            )

        overlay_ref = {"obj": None}

        def close(e):
            self._remove_from_overlay(overlay_ref["obj"])

        def add_and_close(e):
            self._add_to_cart(game, details_overlay=overlay_ref["obj"])

        card = ft.Container(
            content=ft.Column([
                image_block,
                ft.Container(
                    content=ft.Column([
                        ft.Text(game.title, size=16, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREY_900),
                        ft.Divider(),
                        ft.Row([
                            ft.Text("Розробник:", size=12, color=ft.Colors.GREY_600,
                                    weight=ft.FontWeight.BOLD),
                            ft.Text(game.developer, size=12, color=ft.Colors.GREY_800),
                        ], spacing=6),
                        ft.Row([
                            ft.Text("Жанр:", size=12, color=ft.Colors.GREY_600,
                                    weight=ft.FontWeight.BOLD),
                            ft.Text(game.category.name, size=12, color=ft.Colors.GREY_800),
                        ], spacing=6),
                        ft.Row([
                            ft.Text("Рік випуску:", size=12, color=ft.Colors.GREY_600,
                                    weight=ft.FontWeight.BOLD),
                            ft.Text(release, size=12, color=ft.Colors.GREY_800),
                        ], spacing=6),
                        ft.Divider(),
                        ft.Text("Опис:", size=12, color=ft.Colors.GREY_600,
                                weight=ft.FontWeight.BOLD),
                        ft.Text(game.description or "Опис відсутній", size=12,
                                color=ft.Colors.GREY_700),
                        ft.Divider(),
                        ft.Row([
                            ft.Text(f"{game.price} ₴", size=18,
                                    weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_900),
                            ft.Row([
                                ft.TextButton(
                                    "Закрити",
                                    on_click=close,
                                    style=ft.ButtonStyle(color=ft.Colors.GREY_600),
                                ),
                                ft.Button(
                                    "В кошик",
                                    on_click=add_and_close,
                                    style=ft.ButtonStyle(
                                        bgcolor=ft.Colors.INDIGO_700,
                                        color=ft.Colors.WHITE,
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                    ),
                                ),
                            ], spacing=8),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ], spacing=8, tight=True),
                    padding=ft.Padding(16, 12, 16, 16),
                ),
            ], spacing=0, tight=True),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            width=320,
            shadow=ft.BoxShadow(blur_radius=30,
                               color=ft.Colors.with_opacity(0.25, ft.Colors.BLACK)),
        )

        overlay = ft.Container(
            content=ft.Column([
                ft.Container(expand=True),
                ft.Row([
                    ft.Container(expand=True),
                    card,
                    ft.Container(expand=True),
                ]),
                ft.Container(expand=True),
            ], expand=True),
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
        )

        overlay_ref["obj"] = overlay
        self.page.overlay.append(overlay)
        self.page.update()

    def _game_card(self, game, idx=0):
        color = COLORS[idx % len(COLORS)]
        if game.image_url:
            image_block = ft.Container(
                content=ft.Image(src=game.image_url, width=200, height=130,
                                 fit="contain"),
                width=200, height=130,
                bgcolor=ft.Colors.GREY_900,
            )
        else:
            image_block = ft.Container(
                content=ft.Text(game.title[:2].upper(), size=38,
                                weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE,
                                text_align=ft.TextAlign.CENTER),
                bgcolor=color, alignment=ft.Alignment.CENTER, width=200, height=130,
            )

        return ft.Card(
            elevation=3,
            shape=ft.RoundedRectangleBorder(radius=16),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            content=ft.Column([
                image_block,
                ft.Container(
                    content=ft.Column([
                        ft.Text(game.title, size=12, weight=ft.FontWeight.BOLD,
                                max_lines=2, overflow=ft.TextOverflow.ELLIPSIS,
                                color=ft.Colors.GREY_900),
                        ft.Text(game.category.name, size=10,
                                color=ft.Colors.GREY_500, italic=True),
                        ft.Text(game.description, size=10, color=ft.Colors.GREY_600,
                                max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(f"{game.price} ₴", size=16,
                                weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_900),
                        ft.Row([
                            ft.TextButton(
                                "Детальніше",
                                on_click=lambda e, g=game: self._show_details(g),
                                style=ft.ButtonStyle(
                                    color=ft.Colors.INDIGO_700,
                                    padding=ft.Padding(4, 0, 4, 0),
                                ),
                            ),
                            ft.Button(
                                "В кошик",
                                on_click=lambda e, g=game: self._add_to_cart(g),
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.INDIGO_700, color=ft.Colors.WHITE,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    padding=ft.Padding(8, 0, 8, 0),
                                ),
                            ),
                        ], spacing=0, alignment=ft.MainAxisAlignment.SPACE_BETWEEN, expand=True),
                    ], spacing=4, tight=True),
                    padding=ft.Padding(10, 8, 10, 8),
                ),
            ], spacing=0, tight=True),
            width=200,
        )

    def create_view(self):
        self.all_games = self.ctrl.get_all_games()

        self._reset_filters()

        categories = self.ctrl.get_all_categories()
        genre_options = ["Всі"] + [c.name for c in categories]
        self.selected_genre = "Всі"
        self._create_genre_row(genre_options)
        self._apply_filters()

        filter_bar = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Каталог ігор", size=20, weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE),
                ]),
                ft.Row([
                    ft.Text("Жанр:", size=13, color=ft.Colors.WHITE,
                            weight=ft.FontWeight.BOLD),
                    ft.Container(content=self.genre_row, expand=True),
                ], spacing=8),
                ft.Row([
                    ft.Row([
                        ft.Text("Ціна:", size=13, color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD),
                        ft.Text("від", size=12,
                                color=ft.Colors.with_opacity(0.8, ft.Colors.WHITE)),
                        self.price_from_field,
                        ft.Text("до", size=12,
                                color=ft.Colors.with_opacity(0.8, ft.Colors.WHITE)),
                        self.price_to_field,
                        ft.Text("₴", size=13, color=ft.Colors.WHITE),
                    ], spacing=8),
                    ft.Button(
                        "Застосувати",
                        on_click=lambda e: self._apply_filters(),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.WHITE,
                            color=ft.Colors.INDIGO_700,
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                    ),
                ], spacing=24),
            ], spacing=10),
            padding=ft.Padding(20, 12, 20, 12),
            bgcolor=ft.Colors.TRANSPARENT,
        )

        return ft.Container(
            content=ft.Column(
                [
                    filter_bar,
                    ft.Container(
                        content=self.wrap,
                        padding=ft.Padding(16, 0, 16, 16),
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            expand=True,
            bgcolor=ft.Colors.TRANSPARENT,
        )
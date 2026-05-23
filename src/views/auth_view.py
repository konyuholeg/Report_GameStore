import flet as ft
from file_storage import read, write, next_id
from models.user import Customer


class AuthView:
    def __init__(self, page: ft.Page, on_login_success, on_close=None):
        self.page = page
        self.on_login_success = on_login_success
        self.on_close = on_close
        self.is_login_mode = True
        self._dialog = None
        self._closing = False

        self.name_field = ft.TextField(label="Ім'я", border_radius=8, height=48,
                                           content_padding=ft.Padding(12, 0, 12, 0))
        self.email_field = ft.TextField(label="Email", border_radius=8, height=48,
                                           content_padding=ft.Padding(12, 0, 12, 0),
                                           keyboard_type=ft.KeyboardType.EMAIL)
        self.password_field = ft.TextField(label="Пароль", border_radius=8, height=48,
                                           content_padding=ft.Padding(12, 0, 12, 0),
                                           password=True, can_reveal_password=True)
        self.confirm_field = ft.TextField(label="Підтвердіть пароль", border_radius=8, height=48,
                                           content_padding=ft.Padding(12, 0, 12, 0),
                                           password=True, can_reveal_password=True)
        self.error_text = ft.Text("", color=ft.Colors.RED_400, size=13,
                                      text_align=ft.TextAlign.CENTER)
        self.form_container = ft.Column(spacing=12,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def _make_submit_btn(self, label):
        return ft.Button(
            label, on_click=self._submit,
            width=float("inf"), height=48,
            style=ft.ButtonStyle(bgcolor=ft.Colors.INDIGO_700, color=ft.Colors.WHITE,
                                 shape=ft.RoundedRectangleBorder(radius=8)),
        )

    def _make_toggle_btn(self, label):
        return ft.TextButton(
            label, on_click=self._toggle_mode,
            style=ft.ButtonStyle(color=ft.Colors.INDIGO_700),
        )

    def _login(self, email, password):
        for c in read("customers"):
            if c["email"] == email and c.get("password") == password:
                return Customer(
                    id=c["id"], name=c["name"], email=c["email"],
                    phone=c.get("phone", ""), address=c.get("address", ""),
                    password=c["password"], role=c.get("role", "user"),
                )
        return None

    def _register(self, name, email, password):
        customers = read("customers")
        if any(c["email"] == email for c in customers):
            return None
        c = {
            "id": next_id("customers"), "name": name, "email": email,
            "phone": "", "address": "", "password": password,
            "role": "user",
        }
        customers.append(c)
        write("customers", customers)
        return Customer(**c)

    def _toggle_mode(self, e):
        self.is_login_mode = not self.is_login_mode
        self.error_text.value = ""
        self._refresh_form()
        self.page.update()

    def _refresh_form(self):
        self.confirm_field.value = ""
        self.name_field.value = ""
        self.error_text.value = ""

        if self.is_login_mode:
            self.form_container.controls = [
                self.email_field, self.password_field,
                self.error_text,
                self._make_submit_btn("Увійти"),
                self._make_toggle_btn("Немає акаунту? Зареєструватись"),
            ]
        else:
            self.form_container.controls = [
                self.name_field, self.email_field, self.password_field,
                self.confirm_field, self.error_text,
                self._make_submit_btn("Зареєструватись"),
                self._make_toggle_btn("Вже є акаунт? Увійти"),
            ]

    def _close(self, callback=None):
        if self._closing or self._dialog is None:
            return
        self._closing = True
        d = self._dialog
        self._dialog = None
        try:
            self.page.overlay.remove(d)
            self.page.update()
        except Exception:
            pass
        self._closing = False
        if callback:
            callback()
        elif self.on_close:
            self.on_close()

    def _submit(self, e):
        email    = (self.email_field.value or "").strip()
        password = (self.password_field.value or "").strip()

        if not email or not password:
            self.error_text.color = ft.Colors.RED_400
            self.error_text.value = "Заповніть всі поля"
            self.page.update()
            return

        if self.is_login_mode:
            user = self._login(email, password)
            if user:
                self._close(callback=lambda: self.on_login_success(user))
            else:
                self.error_text.color = ft.Colors.RED_400
                self.error_text.value = "Невірний email або пароль"
                self.page.update()
        else:
            name    = (self.name_field.value or "").strip()
            confirm = (self.confirm_field.value or "").strip()
            if not name:
                self.error_text.color = ft.Colors.RED_400
                self.error_text.value = "Введіть ім'я"
                self.page.update()
            elif password != confirm:
                self.error_text.color = ft.Colors.RED_400
                self.error_text.value = "Паролі не співпадають"
                self.page.update()
            elif len(password) < 6:
                self.error_text.color = ft.Colors.RED_400
                self.error_text.value = "Пароль мінімум 6 символів"
                self.page.update()
            else:
                user = self._register(name, email, password)
                if user:
                    self.error_text.color = ft.Colors.GREEN_700
                    self.error_text.value = f"✓ Акаунт створено! Ласкаво просимо, {user.name}!"
                    self.page.update()
                    self._close(callback=lambda: self.on_login_success(user))
                else:
                    self.error_text.color = ft.Colors.RED_400
                    self.error_text.value = "Цей email вже зареєстрований"
                    self.page.update()

    def show_dialog(self):
        self.is_login_mode = True
        self._closing = False
        self.email_field.value = ""
        self.password_field.value = ""
        self._refresh_form()

        dialog_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(expand=True),
                    ft.Text("GameStore", size=24, weight=ft.FontWeight.BOLD,
                            color=ft.Colors.INDIGO_700),
                    ft.Container(expand=True),
                    ft.Button(
                        "✕",
                        on_click=lambda e: self._close(),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.TRANSPARENT,
                            color=ft.Colors.GREY_500,
                            elevation=0,
                            shadow_color=ft.Colors.TRANSPARENT,
                        ),
                    ),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Text("Магазин комп'ютерних ігор", size=12,
                        color=ft.Colors.GREY_500,
                        text_align=ft.TextAlign.CENTER),
                ft.Divider(),
                self.form_container,
            ], spacing=12, tight=True,
               horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=420,
            padding=ft.Padding(32, 24, 32, 24),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            shadow=ft.BoxShadow(blur_radius=30,
                               color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK)),
        )

        overlay = ft.Container(
            content=ft.Column([
                ft.Container(expand=True),
                ft.Row([
                    ft.Container(expand=True),
                    dialog_card,
                    ft.Container(expand=True),
                ]),
                ft.Container(expand=True),
            ], expand=True),
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
        )

        self._dialog = overlay
        self.page.overlay.append(overlay)
        self.page.update()
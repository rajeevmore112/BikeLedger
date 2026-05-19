# ================= PYRIGHT / PYLANCE SUPPRESSION =================
# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownParameterType=false
# pyright: reportUnknownLambdaType=false
# pyright: reportUntypedBaseClass=false
# pyright: reportMissingImports=false
# pyright: reportUndefinedVariable=false
# pyright: reportMissingParameterType=false
# pyright: reportUnusedVariable=false
# pyright: reportUnusedImport=false
# pyright: reportAttributeAccessIssue=false
# =================================================================

# ---------- MOBILE PREVIEW ----------
from kivy.config import Config
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.utils import platform

Config.set("input", "mouse", "mouse,multitouch_on_demand")
if platform not in ("android", "ios"):
    Window.size = (360, 780)

# ---------- KIVY / KIVYMD ----------
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager

# ---------- APP ----------
from app.database import Database, create_backup
from app.constants import (
    ACCENT_AMBER,
    ACCENT_TEAL,
    APP_BG,
    SURFACE,
    TEXT_MUTED,
    TEXT_PRIMARY,
    MOD_CATEGORIES,
    category_style,
)
from app.formatting import format_date, format_money
from app.ui.widgets import entry_card, summary_card
from app.ui.dialogs import add_entry_dialog, edit_entry_dialog


class BikesPassbook(MDApp):

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.accent_palette = "Amber"
        Window.clearcolor = APP_BG

        self.db = Database()
        self.conn = self.db.conn

        self.sm = ScreenManager()
        self._resize_trigger = Clock.create_trigger(
            lambda *_: self.apply_responsive_layout(), 0.12
        )
        Window.bind(size=lambda *_: self._resize_trigger())
        self.update_layout_metrics()
        self.build_main_screen()
        self.load_entries()
        self.apply_responsive_layout(reload_entries=False)
        return self.sm

    def update_layout_metrics(self):
        width = Window.width
        self.is_tiny = width < dp(340)
        self.is_compact = width < dp(390)
        self.page_padding = dp(10 if self.is_tiny else 16 if self.is_compact else 22)
        self.section_spacing = dp(12 if self.is_compact else 16)
        self.category_cols = 1 if width < dp(330) else 2 if width < dp(720) else 3
        self.category_card_height = dp(118 if self.is_compact else 132)
        self.summary_height = dp(114 if self.is_compact else 122)
        self.hero_height = dp(106 if self.is_compact else 126)
        self.bottom_bar_height = dp(82 if self.is_compact else 90)

    def apply_responsive_layout(self, *_args, reload_entries=True):
        self.update_layout_metrics()

        if hasattr(self, "content"):
            self.content.spacing = self.section_spacing
            self.content.padding = (
                self.page_padding,
                self.page_padding,
                self.page_padding,
                self.bottom_bar_height + dp(22),
            )

        if hasattr(self, "hero"):
            self.hero.height = self.hero_height
            self.hero.padding = dp(16 if self.is_compact else 20)
            self.hero_title.font_size = dp(30 if self.is_compact else 34)
            self.hero_subtitle.font_size = dp(12 if self.is_compact else 13)

        if hasattr(self, "schedule_card"):
            self.schedule_card.height = dp(76 if self.is_compact else 82)
            self.schedule_card.padding = dp(14 if self.is_compact else 16)
            self.schedule_label.font_size = dp(15 if self.is_compact else 16)

        if hasattr(self, "summary"):
            self.summary.height = self.summary_height
            self.summary.spacing = dp(8 if self.is_compact else 12)
            card_height = self.summary_height - dp(10)
            for card in (self.maint_card, self.mod_card, self.total_card):
                card.height = card_height

        if hasattr(self, "bottom_bar"):
            self.bottom_bar.height = self.bottom_bar_height
            self.bottom_bar.padding = (
                self.page_padding,
                dp(10),
                self.page_padding,
                dp(10),
            )
            self.add_button.height = dp(50 if self.is_compact else 54)

        if hasattr(self, "mod_grid"):
            self.mod_grid.cols = self.category_cols
            self.mod_grid.spacing = dp(12 if self.is_compact else 14)
            self.mod_grid.padding = dp(2 if self.is_compact else 6)
            if reload_entries:
                self.load_entries()

        if hasattr(self, "maint_value"):
            value_font = dp(15 if self.is_compact else 18)
            for label in (self.maint_value, self.mod_value, self.total_value):
                label.font_size = value_font

    # ================= MAIN SCREEN =================

    def build_main_screen(self):
        self.main_screen = MDScreen(name="main")
        self.main_screen.md_bg_color = APP_BG
        root = MDBoxLayout(orientation="vertical")

        # ---------- SCROLL CONTENT ----------
        scroll = MDScrollView()
        self.content = MDBoxLayout(
            orientation="vertical",
            spacing=self.section_spacing,
            size_hint_y=None,
            padding=(
                self.page_padding,
                self.page_padding,
                self.page_padding,
                self.bottom_bar_height + dp(22),
            ),
        )
        self.content.bind(minimum_height=self.content.setter("height"))
        scroll.add_widget(self.content)
        root.add_widget(scroll)

        # ---------- HERO ----------
        self.hero = MDCard(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(6),
            radius=[dp(24)],
            elevation=5,
            md_bg_color=(0.08, 0.18, 0.20, 1),
            size_hint_y=None,
            height=self.hero_height,
        )
        self.hero_title = MDLabel(
            text="BikeLedger",
            font_style="H4",
            theme_text_color="Custom",
            text_color=TEXT_PRIMARY,
            size_hint_y=None,
            height=dp(42),
        )
        self.hero_subtitle = MDLabel(
            text="Motorcycle spend, service notes, and upgrades",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=TEXT_MUTED,
            size_hint_y=None,
            height=dp(26),
        )
        self.hero.add_widget(self.hero_title)
        self.hero.add_widget(self.hero_subtitle)
        self.content.add_widget(self.hero)

        # ---------- MAINTENANCE CARD ----------
        self.schedule_card = MDCard(
            elevation=4,
            padding=dp(16),
            radius=[dp(18)],
            md_bg_color=SURFACE,
            size_hint_y=None,
            height=dp(78),
        )

        row = MDBoxLayout(spacing=dp(12))
        row.add_widget(
            MDIconButton(
                icon="clipboard-text-clock-outline",
                theme_text_color="Custom",
                text_color=ACCENT_AMBER,
            )
        )
        self.schedule_label = MDLabel(
            text="Maintenance Records",
            font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=TEXT_PRIMARY,
            size_hint_x=1,
        )
        self.schedule_label.bind(
            width=lambda label, width: setattr(label, "text_size", (width, None))
        )
        row.add_widget(self.schedule_label)
        row.add_widget(
            MDIconButton(
                icon="pencil-outline",
                theme_text_color="Custom",
                text_color=ACCENT_TEAL,
                on_release=self.edit_schedule,
            )
        )

        self.schedule_card.add_widget(row)
        self.content.add_widget(self.schedule_card)

        # ---------- SUMMARY ----------
        self.summary = MDBoxLayout(size_hint_y=None, height=self.summary_height, spacing=dp(8))
        self.maint_card, self.maint_value = summary_card(
            "Service",
            on_release=self.open_maintenance,
            icon="wrench-clock-outline",
            accent_color=ACCENT_AMBER,
        )
        self.mod_card, self.mod_value = summary_card(
            "Mods",
            icon="motorbike",
            accent_color=ACCENT_TEAL,
        )
        self.total_card, self.total_value = summary_card(
            "Total",
            icon="cash-multiple",
            accent_color=(0.78, 0.62, 1, 1),
        )
        self.summary.add_widget(self.maint_card)
        self.summary.add_widget(self.mod_card)
        self.summary.add_widget(self.total_card)
        self.content.add_widget(self.summary)

        # ---------- CATEGORY TITLE ----------
        self.content.add_widget(
            MDLabel(
                text="Modifications",
                font_style="H6",
                halign="center",
                theme_text_color="Custom",
                text_color=TEXT_PRIMARY,
                size_hint_y=None,
                height=dp(32),
            )
        )

        # ---------- CATEGORY GRID ----------
        self.mod_grid = GridLayout(
            cols=self.category_cols,
            spacing=dp(12),
            padding=dp(8),
            size_hint_y=None,
        )
        self.mod_grid.bind(minimum_height=self.mod_grid.setter("height"))
        self.content.add_widget(self.mod_grid)

        # ---------- BOTTOM BAR ----------
        self.bottom_bar = MDBoxLayout(
            size_hint_y=None,
            height=self.bottom_bar_height,
            padding=(self.page_padding, dp(10), self.page_padding, dp(10)),
        )

        # pill button layout
        self.add_button = MDCard(
            size_hint=(1, None),
            height=dp(52),
            padding=(dp(20), 0),
            md_bg_color=ACCENT_TEAL,
            radius=[dp(26)],
            elevation=6,
        )

        self.add_button.bind(on_touch_down=lambda inst, touch:
                  add_entry_dialog(self) if inst.collide_point(*touch.pos) else None)

        self.add_button.add_widget(
            MDIconButton(
                icon="plus",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                
            )
        )
        self.add_button.add_widget(
            MDLabel(
                text="ADD ENTRY",
                halign="center",
                valign="middle",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                font_style="Button",
            )
        )

        self.bottom_bar.add_widget(self.add_button)

        self.main_screen.add_widget(root)
        self.main_screen.add_widget(self.bottom_bar)
        self.sm.add_widget(self.main_screen)

    # ================= DATA =================

    def load_entries(self):
        self.mod_grid.clear_widgets()

        cur = self.conn.cursor()
        cur.execute("SELECT amount, entry_type FROM entries")

        m = mod = 0.0
        for amount, t in cur.fetchall():
            if t == "maintenance":
                m += amount or 0
            elif t == "modification":
                mod += amount or 0

        cur.execute(
            """
            SELECT category, COALESCE(SUM(amount), 0)
            FROM entries
            WHERE entry_type='modification'
            GROUP BY category
            """
        )
        category_totals = {category: total for category, total in cur.fetchall()}

        for category in MOD_CATEGORIES:
            category_total = category_totals.get(category, 0)
            style = category_style(category)
            card = MDCard(
                elevation=4,
                radius=[dp(18)],
                md_bg_color=style["bg"],
                size_hint=(1, None),
                height=self.category_card_height,
                padding=dp(12 if self.is_compact else 14),
                on_release=lambda _, c=category: self.open_category(c),
            )

            box = MDBoxLayout(orientation="vertical", spacing=dp(2))
            box.add_widget(
                MDIconButton(
                    icon=style["icon"],
                    theme_text_color="Custom",
                    text_color=style["color"],
                    size_hint_y=None,
                    height=dp(34),
                    pos_hint={"center_x": 0.18},
                )
            )
            title_label = MDLabel(
                text=category,
                halign="left",
                valign="bottom",
                font_style="Body2" if self.is_compact else "Body1",
                theme_text_color="Custom",
                text_color=TEXT_PRIMARY,
                size_hint_y=None,
                height=dp(40 if self.is_compact else 48),
            )
            title_label.bind(
                width=lambda i, w: setattr(i, "text_size", (w, i.height))
            )
            amount_label = MDLabel(
                text=format_money(category_total),
                halign="left",
                valign="top",
                font_style="Caption",
                theme_text_color="Custom",
                text_color=style["color"],
                size_hint_y=None,
                height=dp(22),
            )

            box.add_widget(title_label)
            box.add_widget(amount_label)
            card.add_widget(box)
            self.mod_grid.add_widget(card)

        self.maint_value.text = format_money(m)
        self.mod_value.text = format_money(mod)
        self.total_value.text = format_money(m + mod)

    # ================= NAV =================

    def open_category(self, category, *_, entry_type="modification"):
        name = f"{entry_type}_{category.replace(' ', '_')}"
        if self.sm.has_screen(name):
            if self.sm.current == name:
                self.sm.current = "main"
            self.sm.remove_widget(self.sm.get_screen(name))

        screen = MDScreen(name=name)
        screen.md_bg_color = APP_BG
        root = MDBoxLayout(orientation="vertical", padding=dp(12), spacing=dp(12))
        style = category_style(category)

        top = MDBoxLayout(size_hint_y=None, height=dp(48))
        top.add_widget(
            MDIconButton(
                icon="arrow-left",
                theme_text_color="Custom",
                text_color=TEXT_PRIMARY,
                on_release=self.go_back,
            )
        )
        top.add_widget(
            MDLabel(
                text="Back",
                valign="middle",
                theme_text_color="Custom",
                text_color=TEXT_MUTED,
            )
        )
        top.add_widget(MDBoxLayout(size_hint_x=1))
        root.add_widget(top)

        header = MDCard(
            orientation="horizontal",
            padding=dp(14),
            spacing=dp(10),
            radius=[dp(20)],
            elevation=4,
            md_bg_color=style["bg"],
            size_hint_y=None,
            height=dp(72),
        )
        header.add_widget(
            MDIconButton(
                icon=style["icon"],
                theme_text_color="Custom",
                text_color=style["color"],
            )
        )
        header.add_widget(
            MDLabel(
                text=category,
                font_style="H5",
                valign="middle",
                theme_text_color="Custom",
                text_color=TEXT_PRIMARY,
            )
        )
        root.add_widget(header)

        scroll = MDScrollView()
        box = MDBoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None)
        box.bind(minimum_height=box.setter("height"))
        scroll.add_widget(box)
        root.add_widget(scroll)

        cur = self.conn.cursor()
        if entry_type == "maintenance":
            cur.execute(
                """
                SELECT id, title, amount, date
                FROM entries
                WHERE entry_type='maintenance'
                ORDER BY id DESC
                """
            )
        else:
            cur.execute(
                """
                SELECT id, title, amount, date
                FROM entries
                WHERE entry_type='modification' AND category=?
                ORDER BY id DESC
                """,
                (category,),
            )

        rows = cur.fetchall()
        total = sum(amount or 0 for _, _, amount, _ in rows)
        entry_count = len(rows)
        count_label = "entry" if entry_count == 1 else "entries"
        box.add_widget(
            entry_card(
                f"{category} Total",
                f"{entry_count} {count_label} - {format_money(total)}",
                accent_color=style["color"],
            )
        )

        for entry_id, title, amount, date_text in rows:
            subtitle = f"{format_money(amount)} - {format_date(date_text)}"
            box.add_widget(
                entry_card(
                    title,
                    subtitle,
                    accent_color=style["color"],
                    on_edit=lambda _, i=entry_id: edit_entry_dialog(
                        self,
                        i,
                        on_saved=lambda new_type, new_category: self.refresh_after_entry_change(
                            category, entry_type, new_type, new_category
                        ),
                    ),
                    on_delete=lambda _, i=entry_id, t=title: self.confirm_delete_entry(
                        i, t, category, entry_type
                    ),
                )
            )

        screen.add_widget(root)
        self.sm.add_widget(screen)
        self.sm.current = name

    def open_maintenance(self, *_):
        self.open_category("Maintenance", entry_type="maintenance")

    def go_back(self, *_):
        self.sm.current = "main"

    def confirm_delete_entry(self, entry_id, title, category, entry_type):
        dialog = MDDialog(
            title="Delete entry?",
            text=f"Remove \"{title}\" from your passbook?",
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda *_: dialog.dismiss()),
                MDFlatButton(
                    text="DELETE",
                    theme_text_color="Custom",
                    text_color=(1, 0.35, 0.35, 1),
                    on_release=lambda *_: self.delete_entry(
                        entry_id, category, entry_type, dialog
                    ),
                ),
            ],
        )
        dialog.open()

    def delete_entry(self, entry_id, category, entry_type, dialog):
        create_backup(self.db.db_path, "before_delete")
        cur = self.conn.cursor()
        cur.execute("DELETE FROM entries WHERE id=?", (entry_id,))
        self.conn.commit()
        dialog.dismiss()
        self.load_entries()
        self.open_category(category, entry_type=entry_type)

    def refresh_after_entry_change(
        self,
        old_category,
        old_entry_type,
        new_entry_type,
        new_category,
    ):
        if new_entry_type == old_entry_type:
            target_category = new_category if new_entry_type == "modification" else "Maintenance"
        else:
            target_category = "Maintenance" if new_entry_type == "maintenance" else new_category

        self.open_category(target_category or old_category, entry_type=new_entry_type)

    # ================= DIALOG =================

    def edit_schedule(self, *_):
        field = MDTextField(
            text=self.get_schedule_text(),
            multiline=True,
            size_hint_y=None,
            height=dp(220),
        )

        dialog = MDDialog(
            title="Edit Maintenance Records",
            type="custom",
            content_cls=field,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda *_: dialog.dismiss()),
                MDFlatButton(
                    text="SAVE",
                    on_release=lambda *_: self._save_schedule(field, dialog),
                ),
            ],
        )
        dialog.open()

    def _save_schedule(self, field, dialog):
        create_backup(self.db.db_path, "before_schedule_edit")
        cur = self.conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO schedule (id, note) VALUES (1, ?)",
            (field.text.strip(),),
        )
        self.conn.commit()
        dialog.dismiss()

    def get_schedule_text(self):
        cur = self.conn.cursor()
        cur.execute("SELECT note FROM schedule WHERE id=1")
        row = cur.fetchone()
        return row[0] if row else ""


if __name__ == "__main__":
    BikesPassbook().run()

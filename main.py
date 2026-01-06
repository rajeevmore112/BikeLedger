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

from kivymd.uix.button import MDIconButton
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFloatingActionButton, MDFlatButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager

from app.database import Database
from app.constants import MOD_CATEGORIES
from app.ui.widgets import entry_card, summary_card
from app.ui.dialogs import add_entry_dialog


class BikesPassbook(MDApp):

    # ================= APP =================

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"

        self.db = Database()
        self.conn = self.db.conn

        self.sm = ScreenManager()
        self.build_main_screen()
        self.load_entries()
        return self.sm

    # ================= MAIN SCREEN =================

    def build_main_screen(self):
        self.main_screen = MDScreen(name="main")

        root = MDBoxLayout(orientation="vertical")

        # ---------- SCROLL CONTAINER ----------
        scroll = MDScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            padding=16,
            spacing=16,
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter("height"))
        scroll.add_widget(content)
        root.add_widget(scroll)

        # ---------- TITLE ----------
        content.add_widget(
            MDLabel(
                text="BikeLedger",
                halign="center",
                font_style="H4",
                size_hint_y=None,
                height=52,
            )
        )

        # ---------- SCHEDULE (HEADER ONLY) ----------
        schedule_card = MDCard(
            radius=[20],
            elevation=3,
            padding=16,
            md_bg_color=(0.12, 0.16, 0.22, 1),
            size_hint_y=None,
            height=72,
        )

        schedule_container = MDBoxLayout(
            orientation="horizontal",
            spacing=12,
        )

        schedule_container.add_widget(
            MDLabel(
                text="Maintenance Records",
                font_style="Subtitle1",
                halign="left",
            )
        )
        
        schedule_container.add_widget(
            MDBoxLayout(size_hint_x=1)
        )

        schedule_container.add_widget(
            MDIconButton(
                icon="pencil-outline",
                on_release=self.edit_schedule,
            )
        )

        schedule_card.add_widget(schedule_container)
        content.add_widget(schedule_card)

        # ---------- SUMMARY ----------
        summary = MDBoxLayout(
            spacing=14,
            size_hint_y=None,
            height=120,
        )

        self.maint_card, self.maint_value = summary_card(
            "Maintenance Cost", on_release=self.open_maintenance
        )
        self.mod_card, self.mod_value = summary_card("Modification Cost")
        self.total_card, self.total_value = summary_card("Grand Total")

        summary.add_widget(self.maint_card)
        summary.add_widget(self.mod_card)
        summary.add_widget(self.total_card)
        content.add_widget(summary)

        # ---------- CATEGORIES ----------
        content.add_widget(
            MDLabel(
                text="Modification",
                font_style="H6",
                theme_text_color="Primary",
                size_hint_y=None,
                height=32,
                halign="center",
            )
        )

        cat_scroll = MDScrollView(size_hint_y=None, height=280)

        self.mod_grid = GridLayout(
            cols=3,
            spacing=16,
            padding=6,
            size_hint_y=None,
        )
        self.mod_grid.bind(minimum_height=self.mod_grid.setter("height"))

        cat_scroll.add_widget(self.mod_grid)
        content.add_widget(cat_scroll)

        self.main_screen.add_widget(root)
        self.sm.add_widget(self.main_screen)

        # ---------- FAB ----------
        self.main_screen.add_widget(
            MDFloatingActionButton(
                icon="plus",
                pos_hint={"right": 0.95, "y": 0.03},
                on_release=lambda *_: add_entry_dialog(self),
            )
        )

    # ================= SCHEDULE EDIT =================

    def edit_schedule(self, *_):
        field = MDTextField(
            text=self.get_schedule_text(),
            multiline=True,
            size_hint_y=None,
            height=220,
        )

        def save(*_):
            text = field.text.strip()
            cur = self.conn.cursor()
            cur.execute(
                "INSERT OR REPLACE INTO schedule (id, note) VALUES (1, ?)",
                (text,),
            )
            self.conn.commit()
            dialog.dismiss()

        dialog = MDDialog(
            title="Edit Maintenance Records",
            type="custom",
            content_cls=field,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda *_: dialog.dismiss()),
                MDFlatButton(text="SAVE", on_release=save),
            ],
        )
        dialog.open()

    def get_schedule_text(self):
        cur = self.conn.cursor()
        cur.execute("SELECT note FROM schedule WHERE id=1")
        row = cur.fetchone()
        return row[0] if row else "No scheduled maintenance yet"

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

        for category in MOD_CATEGORIES:
            card = MDCard(
                radius=[22],
                elevation=4,
                md_bg_color=(0.14, 0.19, 0.26, 1),
                size_hint=(1, None),
                height=96,
                padding=12,
                on_release=lambda _, c=category: self.open_category(c),
            )

            label = MDLabel(
                text=category,
                halign="center",
                valign="middle",
                font_style="Subtitle1",
            )
            label.bind(size=label.setter("text_size"))

            card.add_widget(label)
            self.mod_grid.add_widget(card)

        self.maint_value.text = f"₹{int(m)}"
        self.mod_value.text = f"₹{int(mod)}"
        self.total_value.text = f"₹{int(m + mod)}"

    # ================= NAV =================

    def open_category(self, category, *_):
        name = f"cat_{category.replace(' ', '_')}"
        if self.sm.has_screen(name):
            self.sm.current = name
            return

        screen = MDScreen(name=name)
        root = MDBoxLayout(orientation="vertical", padding=12, spacing=12)

        # ---------- TOP BAR ----------
        top_bar = MDBoxLayout(
        orientation="horizontal",
        spacing=8,
        size_hint_y=None,
        height=48,
        )
        
        top_bar.add_widget(
            MDIconButton(
                icon="arrow-left",
                on_release=lambda *_: self.go_back(),
                )
            )
        
        top_bar.add_widget(
            MDLabel(
                text="Back",
                valign="middle",
                theme_text_color="Primary",
                )
        )

        # Right spacer (visual balance)top_bar.add_widget(MDBoxLayout(size_hint_x=1))
        top_bar.add_widget(MDBoxLayout(size_hint_x=1))
        root.add_widget(top_bar)

        root.add_widget(
            MDLabel(
                text=category,
                font_style="H5",
                halign="center",
                size_hint_y=None,
                height=48,
            )
        )

        scroll = MDScrollView()
        box = MDBoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        box.bind(minimum_height=box.setter("height"))
        scroll.add_widget(box)
        root.add_widget(scroll)

        cur = self.conn.cursor()
        cur.execute(
            "SELECT title, amount FROM entries WHERE category=? ORDER BY id DESC",
            (category,),
        )

        for title, amount in cur.fetchall():
            box.add_widget(entry_card(title, f"₹{amount}"))

        screen.add_widget(root)
        self.sm.add_widget(screen)
        self.sm.current = name

    def open_maintenance(self, *_):
        self.open_category("Maintenance")

    def go_back(self):
        self.sm.current = "main"


if __name__ == "__main__":
    BikesPassbook().run() 


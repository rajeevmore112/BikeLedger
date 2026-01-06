# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownParameterType=false
# pyright: reportMissingParameterType=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportUnknownLambdaType=false


from datetime import datetime
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.menu import MDDropdownMenu

from app.constants import MOD_CATEGORIES


def schedule_dialog(app):
    field = MDTextField(text=app.get_schedule_text(), multiline=True)

    dialog = MDDialog(
        title="Scheduled Maintenance",
        type="custom",
        content_cls=field,
        buttons=[
            MDFlatButton(text="CANCEL", on_release=lambda _: dialog.dismiss()),
            MDRaisedButton(
                text="SAVE",
                on_release=lambda _: save_schedule(app, field.text, dialog),
            ),
        ],
    )
    dialog.open()


def save_schedule(app, text, dialog):
    app.conn.execute(
        "INSERT OR REPLACE INTO schedule (id, note) VALUES (1, ?)",
        (text,),
    )
    app.conn.commit()
    app.sched_label.text = text
    dialog.dismiss()


def add_entry_dialog(app):
    title_input = MDTextField(hint_text="What was done?")
    amount_input = MDTextField(hint_text="Amount (₹)", input_filter="float")

    app.entry_type = "maintenance"
    app.category = None

    type_btn = MDRaisedButton(text="Type: Maintenance")
    category_btn = MDRaisedButton(text="Select Category", disabled=True)

    def set_type(t, menu):
        app.entry_type = t
        type_btn.text = f"Type: {t.capitalize()}"
        category_btn.disabled = t != "modification"
        if t != "modification":
            app.category = None
            category_btn.text = "Select Category"
        menu.dismiss()

    def open_type_menu(*_args):
        menu = MDDropdownMenu(
        caller=type_btn,
        items=[
            {
                "text": "Maintenance",
                "on_release": lambda *_: set_type("maintenance", menu),
            },
            {
                "text": "Modification",
                "on_release": lambda *_: set_type("modification", menu),
            },
        ],
    )
        menu.open()

    def open_category_menu(*_args):
        menu = MDDropdownMenu(
        caller=category_btn,
        items=[
            {
                "text": c,
                "on_release": lambda *_args, cat=c: set_category(cat, menu),
            }
            for c in MOD_CATEGORIES
        ],
    )
        menu.open()

    def set_category(cat, menu):
        app.category = cat
        category_btn.text = cat
        menu.dismiss()

    type_btn.on_release = open_type_menu 
    category_btn.on_release = open_category_menu

    content = MDBoxLayout(orientation="vertical", spacing=12, size_hint_y=None)
    content.bind(minimum_height=content.setter("height"))
    content.add_widget(title_input)
    content.add_widget(amount_input)
    content.add_widget(type_btn)
    content.add_widget(category_btn)

    dialog = MDDialog(
        title="Add Entry",
        type="custom",
        content_cls=content,
        buttons=[
            MDFlatButton(text="CANCEL", on_release=lambda _: dialog.dismiss()),
            MDRaisedButton(
                text="ADD",
                on_release=lambda _: save_entry(
                    app, title_input.text, amount_input.text, dialog
                ),
            ),
        ],
    )
    dialog.open()


def save_entry(app, title, amount, dialog):
    if not title or not amount:
        return
    if app.entry_type == "modification" and not app.category:
        return

    app.conn.execute(
        """
        INSERT INTO entries (title, amount, entry_type, category, date)
        VALUES (?,?,?,?,?)
        """,
        (
            title.strip(),
            float(amount),
            app.entry_type,
            app.category,
            datetime.now().isoformat(),
        ),
    )
    app.conn.commit()
    dialog.dismiss()
    app.load_entries()

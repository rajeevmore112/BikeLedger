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
from app.database import create_backup


def show_error(message):
    dialog = MDDialog(
        title="Check entry",
        text=message,
        buttons=[MDFlatButton(text="OK", on_release=lambda *_: dialog.dismiss())],
    )
    dialog.open()


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


def edit_entry_dialog(app, entry_id, on_saved=None):
    cur = app.conn.cursor()
    cur.execute(
        """
        SELECT title, amount, entry_type, category
        FROM entries
        WHERE id=?
        """,
        (entry_id,),
    )
    row = cur.fetchone()
    if not row:
        show_error("This entry no longer exists.")
        return

    title, amount, entry_type, category = row
    title_input = MDTextField(text=str(title or ""), hint_text="What was done?")
    amount_input = MDTextField(
        text=f"{amount:g}" if amount is not None else "",
        hint_text="Amount (₹)",
        input_filter="float",
    )

    selected_type = {"value": entry_type or "maintenance"}
    selected_category = {"value": category}

    type_btn = MDRaisedButton(text=f"Type: {selected_type['value'].capitalize()}")
    category_btn = MDRaisedButton(
        text=selected_category["value"] or "Select Category",
        disabled=selected_type["value"] != "modification",
    )

    def set_type(t, menu):
        selected_type["value"] = t
        type_btn.text = f"Type: {t.capitalize()}"
        category_btn.disabled = t != "modification"
        if t != "modification":
            selected_category["value"] = None
            category_btn.text = "Select Category"
        menu.dismiss()

    def set_category(cat, menu):
        selected_category["value"] = cat
        category_btn.text = cat
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

    type_btn.on_release = open_type_menu
    category_btn.on_release = open_category_menu

    content = MDBoxLayout(orientation="vertical", spacing=12, size_hint_y=None)
    content.bind(minimum_height=content.setter("height"))
    content.add_widget(title_input)
    content.add_widget(amount_input)
    content.add_widget(type_btn)
    content.add_widget(category_btn)

    dialog = MDDialog(
        title="Edit Entry",
        type="custom",
        content_cls=content,
        buttons=[
            MDFlatButton(text="CANCEL", on_release=lambda _: dialog.dismiss()),
            MDRaisedButton(
                text="SAVE",
                on_release=lambda _: save_edited_entry(
                    app,
                    entry_id,
                    title_input.text,
                    amount_input.text,
                    selected_type["value"],
                    selected_category["value"],
                    dialog,
                    on_saved,
                ),
            ),
        ],
    )
    dialog.open()


def save_entry(app, title, amount, dialog):
    title = title.strip()
    amount = amount.strip()

    if not title:
        show_error("Add a short description for the entry.")
        return

    if not amount:
        show_error("Enter the amount spent.")
        return

    try:
        amount_value = float(amount)
    except ValueError:
        show_error("Enter a valid amount.")
        return

    if amount_value <= 0:
        show_error("Amount should be greater than zero.")
        return

    if app.entry_type == "modification" and not app.category:
        show_error("Select a modification category.")
        return

    app.conn.execute(
        """
        INSERT INTO entries (title, amount, entry_type, category, date)
        VALUES (?,?,?,?,?)
        """,
        (
            title,
            amount_value,
            app.entry_type,
            app.category,
            datetime.now().isoformat(),
        ),
    )
    app.conn.commit()
    dialog.dismiss()
    app.load_entries()


def save_edited_entry(
    app,
    entry_id,
    title,
    amount,
    entry_type,
    category,
    dialog,
    on_saved=None,
):
    title = title.strip()
    amount = amount.strip()

    if not title:
        show_error("Add a short description for the entry.")
        return

    if not amount:
        show_error("Enter the amount spent.")
        return

    try:
        amount_value = float(amount)
    except ValueError:
        show_error("Enter a valid amount.")
        return

    if amount_value <= 0:
        show_error("Amount should be greater than zero.")
        return

    if entry_type == "modification" and not category:
        show_error("Select a modification category.")
        return

    if entry_type != "modification":
        category = None

    create_backup(app.db.db_path, "before_edit")
    app.conn.execute(
        """
        UPDATE entries
        SET title=?, amount=?, entry_type=?, category=?
        WHERE id=?
        """,
        (title, amount_value, entry_type, category, entry_id),
    )
    app.conn.commit()
    dialog.dismiss()
    app.load_entries()
    if on_saved:
        on_saved(entry_type, category)

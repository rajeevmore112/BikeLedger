# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownParameterType=false
# pyright: reportMissingParameterType=false


from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel 
from kivymd.uix.button import MDIconButton
from kivy.metrics import dp

from app.constants import ACCENT_TEAL, SURFACE_ALT, TEXT_MUTED, TEXT_PRIMARY


def entry_card(title, subtitle, on_edit=None, on_delete=None, accent_color=None):
    title = str(title) if title else "No description"
    subtitle = str(subtitle) if subtitle else ""
    accent_color = accent_color or ACCENT_TEAL

    card = MDCard(
        padding=14,
        radius=[14],
        elevation=2,
        size_hint_y=None,
        height=86,
        md_bg_color=SURFACE_ALT,
    )

    row = MDBoxLayout(orientation="horizontal", spacing=8)
    accent = MDCard(
        size_hint=(None, 1),
        width=4,
        radius=[4],
        elevation=0,
        md_bg_color=accent_color,
    )
    box = MDBoxLayout(orientation="vertical", spacing=2)

    box.add_widget(
        MDLabel(
            text=title,
            font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=TEXT_PRIMARY,
        )
    )

    if subtitle:
        box.add_widget(
            MDLabel(
                text=subtitle,
                font_style="Caption",
                theme_text_color="Custom",
                text_color=TEXT_MUTED,
            )
        )

    row.add_widget(accent)
    row.add_widget(box)

    if on_edit:
        row.add_widget(
            MDIconButton(
                icon="pencil-outline",
                theme_text_color="Custom",
                text_color=(0.55, 0.75, 1, 1),
                on_release=on_edit,
            )
        )

    if on_delete:
        row.add_widget(
            MDIconButton(
                icon="delete-outline",
                theme_text_color="Custom",
                text_color=(1, 0.45, 0.45, 1),
                on_release=on_delete,
            )
        )

    card.add_widget(row)
    return card



def summary_card(title, on_release=None, icon="wallet-outline", accent_color=None):
    accent_color = accent_color or ACCENT_TEAL
    kwargs = dict(
        padding=(8, 8, 8, 8),
        radius=[18],
        elevation=4,
        size_hint=(1, None),
        height=104,
        md_bg_color=(0.11, 0.145, 0.19, 1),
        
    )

    if on_release:
        kwargs["on_release"] = on_release

    card = MDCard(**kwargs)

    box = MDBoxLayout(orientation="vertical", spacing=0)

    box.add_widget(
        MDIconButton(
            icon=icon,
            theme_text_color="Custom",
            text_color=accent_color,
            size_hint_y=None,
            height=dp(30),
            pos_hint={"center_x": 0.5},
        )
    )

    box.add_widget(
        MDLabel(
            text=title,
            halign="center",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=TEXT_MUTED,
            size_hint_y=None,
            height=dp(20),
            shorten=True,
        )
    )

    value_label = MDLabel(
        text="₹0",
        halign="center",
        font_style="Subtitle1",
        theme_text_color="Custom",
        text_color=TEXT_PRIMARY,
        size_hint_y=None,
        height=dp(42),
        shorten=True,
    )
    value_label.bind(width=lambda label, width: setattr(label, "text_size", (width, None)))

    box.add_widget(value_label)
    card.add_widget(box)

    return card, value_label
